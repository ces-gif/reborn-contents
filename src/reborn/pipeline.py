"""매일 도는 파이프라인 전체.

드라이브 사진 → 상품 묶기 → 가격 읽기 → 카드뉴스 PNG → BEST5 블로그 → 드라이브 업로드 → 알림.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import branding, notify, social
from .blog import write_post
from .cardnews import CardData, render_card
from .config import ASSETS, Settings
from .drive import Drive, DriveFile
from .grouping import filter_for_day, group_photos
from .ranking import pick_best
from .state import LEDGER_NAME, Ledger
from .vision import Product, extract_product, save_products

log = logging.getLogger(__name__)

_UNSAFE = re.compile(r"[^0-9A-Za-z가-힣ㄱ-ㅎㅏ-ㅣ]+")


def slugify(text: str, max_len: int = 28) -> str:
    slug = _UNSAFE.sub("-", (text or "").strip()).strip("-")
    return (slug[:max_len].rstrip("-")) or "상품"


@dataclass
class RunResult:
    day: date
    photos_seen: int = 0
    groups: int = 0
    products: list[Product] = field(default_factory=list)
    cards: list[Path] = field(default_factory=list)
    blog_files: list[Path] = field(default_factory=list)
    social_files: list[Path] = field(default_factory=list)
    needs_review: list[Product] = field(default_factory=list)
    drive_folder_id: str | None = None
    drive_folder_url: str | None = None
    uploaded: dict[str, str] = field(default_factory=dict)
    notified: dict[str, bool] = field(default_factory=dict)
    skipped_reason: str | None = None

    @property
    def published(self) -> list[Product]:
        return [p for p in self.products if p.publishable]


def anthropic_client(settings: Settings):
    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY 가 없습니다. 사진에서 상품명과 가격을 읽으려면 필요합니다. "
            "(docs/SETUP.md 참고)"
        )
    from anthropic import Anthropic

    return Anthropic(api_key=settings.anthropic_api_key)


def ensure_logo(drive: Drive | None, settings: Settings) -> Path:
    """드라이브에 있는 실제 리본마켓 로고를 받아 캐시한다."""
    cache = branding.LOGO_CACHE
    if cache.exists() and cache.stat().st_size > 0:
        return cache
    if drive is None or not settings.logo_file_id:
        return branding.logo_path()  # 없으면 LogoMissing 을 던진다
    cache.parent.mkdir(parents=True, exist_ok=True)
    drive.download(settings.logo_file_id, cache)
    log.info("리본마켓 로고 내려받음: %s (%d bytes)", cache, cache.stat().st_size)
    return cache


def run(
    settings: Settings,
    *,
    day: date | None = None,
    out_root: Path = Path("out"),
    work_root: Path = Path("work"),
    dry_run: bool = False,
    reprocess: bool = False,
) -> RunResult:
    zone = ZoneInfo(settings.timezone)
    target_day = day or datetime.now(zone).date()
    result = RunResult(day=target_day)

    drive = Drive()
    ensure_logo(drive, settings)

    # 1) 그날 올라온 사진 모으기 --------------------------------------------
    files = drive.list_children(settings.source_folder_id, only_images=True)
    todays = filter_for_day(
        files, datetime.combine(target_day, datetime.min.time(), tzinfo=zone), tz=settings.timezone
    )
    log.info("소스 폴더 사진 %d장 중 %s 업로드분 %d장", len(files), target_day, len(todays))

    # dry-run 일 때는 드라이브에 아무것도 만들지 않는다 (폴더 생성도 쓰기다).
    publish_root = _find_publish_root(drive, settings) if dry_run else _ensure_publish_root(
        drive, settings
    )
    ledger = _load_ledger(drive, publish_root, work_root) if publish_root else Ledger()

    if not reprocess:
        before = len(todays)
        todays = [f for f in todays if not ledger.seen(f.id)]
        if before != len(todays):
            log.info("이미 처리한 사진 %d장 제외", before - len(todays))

    result.photos_seen = len(todays)
    if not todays:
        result.skipped_reason = "오늘 새로 올라온 상품 사진이 없습니다"
        log.info(result.skipped_reason)
        return result

    # 2) 같은 상품끼리 묶기 --------------------------------------------------
    groups = group_photos(
        todays, max_gap_seconds=settings.max_gap_seconds, tz=settings.timezone
    )
    if settings.max_cards_per_day > 0:
        groups = groups[: settings.max_cards_per_day]
    result.groups = len(groups)
    log.info("상품 묶음 %d개", len(groups))

    day_slug = target_day.strftime("%Y-%m-%d")
    out_dir = out_root / day_slug
    work_dir = work_root / day_slug
    if out_dir.exists():
        shutil.rmtree(out_dir)
    for sub in ("카드뉴스", "블로그", "소셜", "_data"):
        (out_dir / sub).mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    client = anthropic_client(settings)

    # 3) 사진에서 상품 정보 읽기 --------------------------------------------
    for group in groups:
        picked = group.files[: settings.max_photos_per_group]
        paths: list[Path] = []
        for file in picked:
            dest = work_dir / f"{group.index:02d}-{file.name}"
            if not dest.exists():
                drive.download(file.id, dest)
            paths.append(dest)
        try:
            product = extract_product(
                client,
                paths,
                model=settings.vision_model,
                group_index=group.index,
                source_file_ids=[f.id for f in group.files],
            )
        except Exception as exc:
            log.error("상품 %d번 정보 추출 실패: %s", group.index, exc)
            continue
        log.info(
            "  [%02d] %s | %s → %s | 검토필요=%s",
            group.index,
            product.product_name,
            product.original_price,
            product.sale_price,
            product.needs_review,
        )
        result.products.append(product)
        if not product.publishable:
            result.needs_review.append(product)

    # 4) 카드뉴스 만들기 ------------------------------------------------------
    for order, product in enumerate(result.published, start=1):
        card = CardData(
            product_name=product.product_name,
            one_liner=product.one_liner,
            sale_price=product.sale_price,
            original_price=product.original_price,
            discount_pct=product.discount_pct,
            date_label=target_day.strftime("%Y.%m.%d"),
            footer=settings.visit_line or f"{settings.store_name} · 매장에서 직접 보고 구매하세요",
            orig_label=settings.orig_label,
            sale_label=settings.sale_label,
        )
        path = out_dir / "카드뉴스" / f"{order:02d}-{slugify(product.product_name)}.png"
        render_card(card, product.best_photo, path)
        result.cards.append(path)

    # 5) BEST5 블로그 ---------------------------------------------------------
    picks = pick_best(
        result.published, count=settings.best_count, client=client, model=settings.writing_model
    )
    if picks:
        post = write_post(
            client,
            picks,
            model=settings.writing_model,
            store_name=settings.store_name,
            day=target_day,
            footer_note=settings.footer_note,
        )
        md_path = out_dir / "블로그" / f"{day_slug}-best{len(picks)}-blog.md"
        html_path = out_dir / "블로그" / f"{day_slug}-best{len(picks)}-blog.html"
        md_path.write_text(
            post.to_markdown(settings.store_name, settings.footer_note), encoding="utf-8"
        )
        html_path.write_text(
            post.to_naver_html(settings.store_name, settings.footer_note), encoding="utf-8"
        )
        result.blog_files = [md_path, html_path]

    # 6) 카톡 공지 / 인스타 캡션 ---------------------------------------------
    best_products = [p for p, _ in picks] or result.published
    if best_products:
        kakao_path = out_dir / "소셜" / f"{day_slug}-카톡공지.txt"
        insta_path = out_dir / "소셜" / f"{day_slug}-인스타캡션.txt"
        kakao_text = social.kakao_notice(
            best_products,
            day=target_day,
            store_name=settings.store_name,
            footer_note=settings.footer_note,
        )
        kakao_path.write_text(kakao_text, encoding="utf-8")
        insta_path.write_text(
            social.instagram_caption(
                best_products,
                day=target_day,
                store_name=settings.store_name,
                handle=settings.store_handle,
            ),
            encoding="utf-8",
        )
        result.social_files = [kakao_path, insta_path]
    else:
        kakao_text = ""

    # 7) 근거 자료 + 실행 리포트 ---------------------------------------------
    save_products(result.products, out_dir / "_data" / "products.json")
    (out_dir / "_data" / "리포트.md").write_text(_report(result, settings), encoding="utf-8")

    if dry_run:
        log.info("dry-run: 드라이브 업로드와 알림을 건너뜁니다")
        return result

    # 8) 드라이브 업로드 ------------------------------------------------------
    day_folder = drive.ensure_folder(day_slug, publish_root)
    result.drive_folder_id = day_folder
    result.drive_folder_url = f"https://drive.google.com/drive/folders/{day_folder}"
    from .drive import upload_tree

    result.uploaded = upload_tree(drive, out_dir, day_folder)
    log.info("드라이브 업로드 %d개 → %s", len(result.uploaded), result.drive_folder_url)

    # 9) 원장 갱신 -------------------------------------------------------------
    ledger.mark([f.id for f in todays])
    ledger.record_run(
        {
            "day": day_slug,
            "photos": result.photos_seen,
            "products": len(result.products),
            "cards": len(result.cards),
            "needs_review": len(result.needs_review),
            "drive_folder": result.drive_folder_url,
            "at": datetime.now(zone).isoformat(),
        }
    )
    ledger_path = ledger.save(work_root / LEDGER_NAME)
    drive.upload(ledger_path, publish_root, name=LEDGER_NAME)

    # 10) 알림 ----------------------------------------------------------------
    if kakao_text:
        result.notified = notify.broadcast(kakao_text, result.drive_folder_url)

    return result


def _find_publish_root(drive: Drive, settings: Settings) -> str | None:
    parent = settings.publish_parent_id or drive.get_parent(settings.source_folder_id)
    if not parent:
        return None
    return drive.find_child(parent, settings.publish_folder_name)


def _ensure_publish_root(drive: Drive, settings: Settings) -> str:
    parent = settings.publish_parent_id or drive.get_parent(settings.source_folder_id)
    return drive.ensure_folder(settings.publish_folder_name, parent)


def _load_ledger(drive: Drive, publish_root: str, work_root: Path) -> Ledger:
    work_root.mkdir(parents=True, exist_ok=True)
    local = work_root / LEDGER_NAME
    remote = drive.find_child(publish_root, LEDGER_NAME)
    if remote:
        try:
            drive.download(remote, local)
        except Exception as exc:
            log.warning("원장 내려받기 실패, 새로 시작합니다: %s", exc)
    return Ledger.load(local)


def _report(result: RunResult, settings: Settings) -> str:
    lines = [
        f"# {result.day} 리본마켓 콘텐츠 자동 발행 리포트",
        "",
        f"- 사진: {result.photos_seen}장",
        f"- 상품 묶음: {result.groups}개",
        f"- 카드뉴스: {len(result.cards)}장",
        f"- 블로그: {'생성' if result.blog_files else '없음'}",
        "",
        "## 생성된 상품",
    ]
    for i, p in enumerate(result.published, start=1):
        pct = f" ({p.computed_pct}%↓)" if p.computed_pct else ""
        orig = f"{p.original_price:,}원 → " if p.original_price else ""
        lines.append(f"{i}. {p.product_name} — {orig}{p.sale_price:,}원{pct}  · 근거: {p.price_source}")
    if result.needs_review:
        lines += ["", "## 사람이 확인해야 하는 건 (카드뉴스 미생성)"]
        for p in result.needs_review:
            lines.append(
                f"- {p.product_name or '(상품 아님)'} — {p.review_reason or '상품 사진이 아님'}"
                f"  · 사진: {', '.join(Path(x).name for x in p.photo_paths)}"
            )
    lines += ["", f"생성 시각 기준 매장: {settings.store_name}"]
    return "\n".join(lines) + "\n"


def print_summary(result: RunResult) -> None:
    if result.skipped_reason:
        print(f"⏭  {result.day}: {result.skipped_reason}")
        return
    print(f"✅ {result.day} 완료")
    print(f"   사진 {result.photos_seen}장 → 상품 {result.groups}개 → 카드뉴스 {len(result.cards)}장")
    if result.blog_files:
        print(f"   블로그: {result.blog_files[0].name} (+ 네이버 붙여넣기용 HTML)")
    if result.needs_review:
        print(f"   ⚠️  확인 필요 {len(result.needs_review)}건 (가격을 못 읽었거나 상품 사진이 아님)")
    if result.drive_folder_url:
        print(f"   드라이브: {result.drive_folder_url}")
    if result.notified:
        sent = [k for k, v in result.notified.items() if v]
        print(f"   알림 전송: {', '.join(sent) if sent else '(설정된 채널 없음)'}")
