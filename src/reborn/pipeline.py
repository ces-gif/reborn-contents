"""매일 도는 파이프라인 전체.

드라이브 사진 → 상품 묶기 → 가격 읽기 → 웹 검색 설명 → 카드뉴스 PNG
  → BEST5 블로그 → 드라이브 업로드 → 인스타 스토리 게시 → 알림.

사진 폴더는 두 곳이다:
  - 리퍼    : 검수를 마친 리퍼브 상품
  - 새상품  : 제조사와 직거래한 미개봉 새 제품을 초저가로
두 폴더를 같이 처리하되, 문구(눈썹)와 상태 표현 규칙이 다르다.
"""

from __future__ import annotations

import logging
import re
import shutil
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import branding, instagram, llm, notify, research, social
from .llm import LLMQuotaError
from .blog import write_post
from .cardnews import CardData, render_card
from .config import Settings, Source
from .drive import Drive, DriveFile, upload_tree
from .grouping import capture_time, filter_for_day, group_by_content
from .ranking import pick_best
from .state import LEDGER_NAME, Ledger
from .vision import Product, classify_photos, extract_product, save_products

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
    per_source: dict[str, int] = field(default_factory=dict)
    drive_folder_id: str | None = None
    drive_folder_url: str | None = None
    uploaded: dict[str, str] = field(default_factory=dict)
    notified: dict[str, bool] = field(default_factory=dict)
    stories: instagram.PublishReport | None = None
    skipped_reason: str | None = None
    quota_note: str | None = None
    failed_groups: int = 0

    @property
    def published(self) -> list[Product]:
        return [p for p in self.products if p.publishable]


def make_llm(settings: Settings):
    """설정에 맞는 모델 공급자를 만든다 (제미나이 무료 / Claude 유료)."""
    return llm.make_client(settings)


def ensure_logo(drive: Drive | None, settings: Settings) -> Path:
    """실제 리본마켓 로고를 확보한다. 저장소 파일이 있으면 그걸 쓰고, 없으면 드라이브에서 받는다."""
    try:
        return branding.logo_path()
    except branding.LogoMissing:
        pass
    if drive is None or not settings.logo_file_id:
        return branding.logo_path()  # LogoMissing 을 그대로 던진다
    cache = branding.LOGO_CACHE
    cache.parent.mkdir(parents=True, exist_ok=True)
    drive.download(settings.logo_file_id, cache)
    _verify_png(cache)
    log.info("리본마켓 로고 내려받음: %s (%d bytes)", cache, cache.stat().st_size)
    return cache


def _verify_png(path: Path) -> None:
    """내려받은 로고가 깨지지 않았는지 PNG 청크 CRC 로 확인한다.

    깨진 로고로 카드를 찍어 내보내는 것보다 여기서 멈추는 편이 낫다.
    """
    import struct
    import zlib

    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise branding.LogoMissing(f"로고 파일이 PNG 가 아닙니다: {path}")
    offset = 8
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        end = offset + 8 + length
        if end + 4 > len(data):
            raise branding.LogoMissing(f"로고 파일이 잘렸습니다: {path}")
        expected = struct.unpack(">I", data[end : end + 4])[0]
        if zlib.crc32(kind + data[offset + 8 : end]) & 0xFFFFFFFF != expected:
            raise branding.LogoMissing(f"로고 파일이 손상됐습니다({kind.decode()} 청크): {path}")
        offset = end + 4
        if kind == b"IEND":
            return
    raise branding.LogoMissing(f"로고 파일에 IEND 가 없습니다: {path}")


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

    publish_root = (
        _find_publish_root(drive, settings) if dry_run else _ensure_publish_root(drive, settings)
    )
    ledger = _load_ledger(drive, publish_root, work_root) if publish_root else Ledger()

    # 1) 폴더별로 그날 올라온 사진 모으기 ------------------------------------
    day_start = datetime.combine(target_day, datetime.min.time(), tzinfo=zone)
    per_source: list[tuple[Source, list[DriveFile]]] = []
    for source in settings.sources:
        files = drive.list_children(source.folder_id, only_images=True)
        todays = filter_for_day(files, day_start, tz=settings.timezone)
        if not reprocess:
            todays = [f for f in todays if not ledger.seen(f.id)]
        # 촬영 순서대로 세운다 — 내용으로 묶으려면 찍은 순서가 맞아야 한다.
        todays.sort(key=lambda f: capture_time(f, settings.timezone))
        log.info("[%s] 전체 %d장 중 %s 신규 %d장", source.name, len(files), target_day, len(todays))
        per_source.append((source, todays))
        result.per_source[source.name] = len(todays)

    all_new = [f for _, files in per_source for f in files]
    result.photos_seen = len(all_new)
    if not all_new:
        result.skipped_reason = "오늘 새로 올라온 상품 사진이 없습니다"
        log.info(result.skipped_reason)
        return result

    day_slug = target_day.strftime("%Y-%m-%d")
    out_dir = out_root / day_slug
    work_dir = work_root / day_slug
    if out_dir.exists():
        shutil.rmtree(out_dir)
    for sub in ("카드뉴스", "블로그", "소셜", "_data"):
        (out_dir / sub).mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    client = make_llm(settings)
    log.info("모델: 판독 %s / 글쓰기 %s", client.vision_model, client.writing_model)

    # 2) 폴더별로 상품 묶고 가격표 읽기 --------------------------------------
    # 사진을 먼저 전부 받아서 "가격표냐 상품이냐"를 한 장씩 판독한 뒤,
    # 그 내용으로 같은 상품끼리 묶는다. 촬영 시각으로 묶던 예전 방식은
    # 연달아 찍으면 수십 장이 한 덩어리가 되어버렸다.
    remaining = settings.max_cards_per_day or None
    for source, files in per_source:
        if not files:
            continue

        paths_by_id: dict[str, Path] = {}
        for i, file in enumerate(files, start=1):
            dest = work_dir / slugify(source.name) / f"{i:03d}-{file.name}"
            if not dest.exists():
                drive.download(file.id, dest)
            paths_by_id[file.id] = dest

        photo_paths = [paths_by_id[f.id] for f in files]
        classes = classify_photos(client, photo_paths, model=client.vision_model)
        kinds = [c.kind for c in classes]
        items = [c.item for c in classes]
        log.info(
            "[%s] 사진 판독: 상품 %d · 가격표 %d · 상품+가격표 %d · 제외 %d",
            source.name,
            kinds.count("product"),
            kinds.count("price_tag"),
            kinds.count("both"),
            kinds.count("other"),
        )

        groups = group_by_content(
            files, kinds, items, tz=settings.timezone, max_size=settings.max_photos_per_group
        )
        if remaining is not None:
            if len(groups) > remaining:
                log.warning(
                    "[%s] 상품 묶음 %d개 중 하루 상한(%d)만큼만 만듭니다",
                    source.name,
                    len(groups),
                    remaining,
                )
            groups = groups[:remaining]
            remaining -= len(groups)
        result.groups += len(groups)
        log.info("[%s] 사진 %d장 → 상품 묶음 %d개", source.name, len(files), len(groups))

        for group in groups:
            paths = [paths_by_id[f.id] for f in group.files]
            known = list(group.kinds)
            try:
                product = extract_product(
                    client,
                    paths,
                    model=client.vision_model,
                    group_index=group.index,
                    source_file_ids=[f.id for f in group.files],
                    source_name=source.name,
                    source_kind=source.kind,
                    eyebrow=source.eyebrow,
                    known_kinds=known,
                )
            except LLMQuotaError as exc:
                result.quota_note = str(exc).split("\n")[0]
                result.failed_groups += 1
                log.error(
                    "[%s] 상품 %d번부터는 하루 요청 한도를 다 써서 판독하지 못했습니다",
                    source.name,
                    group.index,
                )
                continue
            except Exception as exc:
                result.failed_groups += 1
                log.error("[%s] 상품 %d번 정보 추출 실패: %s", source.name, group.index, exc)
                continue
            log.info(
                "  [%s %02d] %s | 사진 %s | %s → %s | 검토필요=%s %s",
                source.name,
                group.index,
                product.product_name,
                "+".join(product.photo_kinds),
                product.original_price,
                product.sale_price,
                product.needs_review,
                product.review_reason,
            )
            result.products.append(product)
            if not product.publishable:
                result.needs_review.append(product)

    # 3) 인터넷에서 제품을 찾아 짧은 설명을 붙인다 (확인 안 되면 안 붙인다) --
    research.research_all(client, result.products, model=client.writing_model)

    # 4) 카드뉴스 만들기 ------------------------------------------------------
    counters: dict[str, int] = {}
    for product in result.published:
        counters[product.source_name] = counters.get(product.source_name, 0) + 1
        card = CardData(
            product_name=product.product_name,
            one_liner=product.card_line,
            sale_price=product.sale_price,
            original_price=product.original_price,
            discount_pct=product.discount_pct,
            eyebrow=product.eyebrow,
            date_label=target_day.strftime("%Y.%m.%d"),
            footer=settings.visit_line or f"{settings.store_name} · 매장에서 직접 보고 구매하세요",
            orig_label=settings.orig_label,
            sale_label=settings.sale_label,
        )
        path = (
            out_dir
            / "카드뉴스"
            / slugify(product.source_name)
            / f"{counters[product.source_name]:02d}-{slugify(product.product_name)}.png"
        )
        render_card(card, product.best_photo, path)
        result.cards.append(path)

    # 5) BEST5 블로그 ---------------------------------------------------------
    picks = pick_best(
        result.published, count=settings.best_count, client=client, model=client.writing_model
    )
    if picks:
        post = write_post(
            client,
            picks,
            model=client.writing_model,
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
    kakao_text = ""
    if best_products:
        kakao_text = social.kakao_notice(
            best_products,
            day=target_day,
            store_name=settings.store_name,
            footer_note=settings.footer_note,
        )
        kakao_path = out_dir / "소셜" / f"{day_slug}-카톡공지.txt"
        insta_path = out_dir / "소셜" / f"{day_slug}-인스타캡션.txt"
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

    # 7) 근거 자료 + 실행 리포트 ---------------------------------------------
    save_products(result.products, out_dir / "_data" / "products.json")

    if dry_run:
        (out_dir / "_data" / "리포트.md").write_text(_report(result, settings), encoding="utf-8")
        log.info("dry-run: 드라이브 업로드·인스타 게시·알림을 건너뜁니다")
        return result

    # 8) 인스타그램 스토리 게시 (컴퓨터 없이 자동) ---------------------------
    if settings.instagram_enabled and result.cards:
        result.stories = instagram.publish_cards(
            result.cards,
            key_prefix=f"cardnews/{day_slug}",
            max_stories=settings.max_stories_per_day,
            delay_seconds=settings.story_delay_seconds,
        )

    (out_dir / "_data" / "리포트.md").write_text(_report(result, settings), encoding="utf-8")

    # 9) 드라이브 업로드 ------------------------------------------------------
    day_folder = drive.ensure_folder(day_slug, publish_root)
    result.drive_folder_id = day_folder
    result.drive_folder_url = f"https://drive.google.com/drive/folders/{day_folder}"
    result.uploaded = upload_tree(drive, out_dir, day_folder)
    log.info("드라이브 업로드 %d개 → %s", len(result.uploaded), result.drive_folder_url)

    # 10) 원장 갱신 ------------------------------------------------------------
    ledger.mark([f.id for f in all_new])
    ledger.record_run(
        {
            "day": day_slug,
            "photos": result.photos_seen,
            "per_source": result.per_source,
            "products": len(result.products),
            "cards": len(result.cards),
            "needs_review": len(result.needs_review),
            "stories": len(result.stories.published) if result.stories else 0,
            "drive_folder": result.drive_folder_url,
            "at": datetime.now(zone).isoformat(),
        }
    )
    ledger_path = ledger.save(work_root / LEDGER_NAME)
    drive.upload(ledger_path, publish_root, name=LEDGER_NAME)

    # 11) 알림 ----------------------------------------------------------------
    if kakao_text:
        result.notified = notify.broadcast(kakao_text, result.drive_folder_url)

    return result


def _ensure_publish_root(drive: Drive, settings: Settings) -> str:
    parent = settings.publish_parent_id or drive.get_parent(settings.sources[0].folder_id)
    return drive.ensure_folder(settings.publish_folder_name, parent)


def _find_publish_root(drive: Drive, settings: Settings) -> str | None:
    parent = settings.publish_parent_id or drive.get_parent(settings.sources[0].folder_id)
    if not parent:
        return None
    return drive.find_child(parent, settings.publish_folder_name)


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
        f"- 사진: {result.photos_seen}장 ("
        + ", ".join(f"{name} {n}장" for name, n in result.per_source.items())
        + ")",
        f"- 상품 묶음: {result.groups}개",
        f"- 카드뉴스: {len(result.cards)}장",
        f"- 블로그: {'생성' if result.blog_files else '없음'}",
    ]
    if result.failed_groups:
        lines.append(f"- ⚠️ 판독하지 못한 묶음: {result.failed_groups}개")
    if result.quota_note:
        lines += ["", "## ⚠️ 오늘 만들다 만 이유", result.quota_note]
    if result.stories is not None:
        if result.stories.skipped_reason:
            lines.append(f"- 인스타 스토리: 건너뜀 — {result.stories.skipped_reason}")
        else:
            lines.append(
                f"- 인스타 스토리: {len(result.stories.published)}건 게시"
                + (f", {len(result.stories.failed)}건 실패" if result.stories.failed else "")
            )
    lines += ["", "## 생성된 상품"]
    for i, p in enumerate(result.published, start=1):
        pct = f" ({p.computed_pct}%↓)" if p.computed_pct else ""
        orig = f"{p.original_price:,}원 → " if p.original_price else ""
        lines.append(f"{i}. [{p.source_name}] {p.product_name} — {orig}{p.sale_price:,}원{pct}")
        lines.append(f"   · 가격 근거: {p.price_source}")
        lines.append(
            "   · 제품 설명: "
            + (f"웹 확인됨 — {p.spec_line}" if p.research_matched else "검색으로 특정 못 함 (설명 없음)")
        )
        if p.condition_note:
            lines.append(f"   · 상태 표기: {p.condition_note}")
    if result.needs_review:
        lines += ["", "## 사람이 확인해야 하는 건 (카드뉴스 미생성)"]
        for p in result.needs_review:
            lines.append(
                f"- [{p.source_name}] {p.product_name or '(상품명 불명)'} — "
                f"{p.review_reason or '사유 미상'}"
                f"  · 사진: {', '.join(Path(x).name for x in p.photo_paths)}"
                f" ({'+'.join(p.photo_kinds) or '?'})"
            )
    if result.stories and result.stories.failed:
        lines += ["", "## 인스타 스토리 실패"]
        for r in result.stories.failed:
            lines.append(f"- {r.card.name} — {r.error}")
    lines += ["", f"생성 시각 기준 매장: {settings.store_name}"]
    return "\n".join(lines) + "\n"


def print_summary(result: RunResult) -> None:
    if result.skipped_reason:
        print(f"⏭  {result.day}: {result.skipped_reason}")
        return
    counts = ", ".join(f"{name} {n}장" for name, n in result.per_source.items())
    print(f"✅ {result.day} 완료")
    print(f"   사진 {result.photos_seen}장 ({counts}) → 상품 {result.groups}개 → 카드뉴스 {len(result.cards)}장")
    if result.blog_files:
        print(f"   블로그: {result.blog_files[0].name} (+ 네이버 붙여넣기용 HTML)")
    if result.stories is not None:
        if result.stories.skipped_reason:
            print(f"   인스타 스토리: 건너뜀 — {result.stories.skipped_reason}")
        else:
            print(f"   인스타 스토리: {len(result.stories.published)}건 게시")
    if result.needs_review:
        print(f"   ⚠️  확인 필요 {len(result.needs_review)}건")
    if result.failed_groups:
        print(f"   ⚠️  판독 실패 {result.failed_groups}개")
    if result.quota_note:
        print(f"   ⚠️  {result.quota_note}")
    if result.drive_folder_url:
        print(f"   드라이브: {result.drive_folder_url}")
    if result.notified:
        sent = [k for k, v in result.notified.items() if v]
        print(f"   알림 전송: {', '.join(sent) if sent else '(설정된 채널 없음)'}")
