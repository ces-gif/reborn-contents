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
import os
import re
import shutil
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import branding, instagram, llm, notify, reels, research, social
from .llm import LLMQuotaError
from .blog import write_post
from .cardnews import CardData, render_card, render_cover
from .config import ASSETS, Settings, Source
from .drive import Drive, DriveFile, upload_tree
from .grouping import capture_time, filter_for_day, group_by_content
from .imaging import exif_capture_time
from .ranking import pick_best
from .state import LEDGER_NAME, Ledger
from .vision import (
    Product,
    classify_photos,
    extract_product,
    pick_card_photo,
    plan_store_photos,
    products_from_plan,
    save_products,
)

log = logging.getLogger(__name__)

_UNSAFE = re.compile(r"[^0-9A-Za-z가-힣ㄱ-ㅎㅏ-ㅣ]+")


def slugify(text: str, max_len: int = 28) -> str:
    slug = _UNSAFE.sub("-", (text or "").strip()).strip("-")
    return (slug[:max_len].rstrip("-")) or "상품"


@dataclass
class RunResult:
    day: date
    store_name: str = ""
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
    reel: instagram.ReelReport | None = None
    cover: Path | None = None
    reel_video: Path | None = None
    reel_error: str = ""
    skipped_reason: str | None = None
    quota_note: str | None = None
    reading_mode: str = ""  # 사진을 어떻게 읽었는지 (통판독 / 예전 방식)
    failed_groups: int = 0
    # 카드뉴스 뒤에 붙는 단계(블로그·소셜 등)가 넘어진 기록. 발행 자체는 계속한다.
    step_failures: list[str] = field(default_factory=list)

    @property
    def published(self) -> list[Product]:
        return [p for p in self.products if p.publishable]


def make_llm(settings: Settings):
    """설정에 맞는 모델 공급자를 만든다 (제미나이 무료 / Claude 유료)."""
    return llm.make_client(settings)


def ensure_logo(drive: Drive | None, settings: Settings):
    """이 매장의 로고를 확보한다.

    매장마다 로고가 다르므로 **매장별로** 찾고 매장별 경로에 캐시한다.
    한 매장의 로고가 다른 매장 카드에 찍히면 안 된다.

    찾는 순서:
      1. REBORN_LOGO_PATH 환경변수 (테스트·임시 교체용)
      2. 설정의 logo_asset — 저장소에 동봉한 파일
      3. 드라이브 logo_file_id — 지정한 파일
      4. 드라이브 logo_folder_id — 그 폴더의 최신 이미지
         (새 매장은 로고를 이 폴더에 넣기만 하면 다음 실행부터 반영된다)
      5. logo_wordmark 를 켠 매장이면 매장 이름을 글자로 (로고가 아직 없는 신규 매장만)
    """
    override = os.environ.get(branding.LOGO_ENV_PATH)
    if override and Path(override).exists():
        return Path(override)

    if settings.logo_asset:
        asset = ASSETS / settings.logo_asset
        if asset.exists() and asset.stat().st_size > 0:
            return asset

    cache = branding.REPO_ROOT / ".cache" / f"logo-{slugify(settings.store_id)}.png"
    file_id = settings.logo_file_id or _newest_image_id(drive, settings.logo_folder_id)
    if drive is not None and file_id:
        cache.parent.mkdir(parents=True, exist_ok=True)
        drive.download(file_id, cache)
        _verify_png(cache)
        log.info("[%s] 로고 내려받음: %s (%d bytes)", settings.store_name, cache, cache.stat().st_size)
        return cache
    if cache.exists() and cache.stat().st_size > 0:
        return cache

    if settings.logo_wordmark:
        log.warning(
            "[%s] 로고 파일이 아직 없어 매장 이름을 글자로 넣습니다. "
            "드라이브 '로고' 폴더에 PNG 를 올리면 다음 실행부터 진짜 로고가 들어갑니다.",
            settings.store_name,
        )
        return branding.wordmark(settings.store_name, 200)

    return branding.logo_path()  # LogoMissing 을 그대로 던진다


def _newest_image_id(drive: Drive | None, folder_id: str) -> str:
    """로고 폴더에서 가장 최근에 올라온 이미지 하나."""
    if drive is None or not folder_id:
        return ""
    try:
        images = drive.list_children(folder_id, only_images=True)
    except Exception as exc:  # 로고 폴더가 없거나 권한이 없어도 발행은 계속한다
        log.warning("로고 폴더를 읽지 못했습니다(%s): %s", folder_id, exc)
        return ""
    if not images:
        return ""
    return max(images, key=lambda f: f.created_time).id


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
    # 매장별로 작업 폴더를 나눈다. 안 나누면 두 매장의 001-xxx.jpg 가 서로 덮어쓴다.
    work_root = work_root / slugify(settings.store_id)
    result = RunResult(day=target_day, store_name=settings.store_name)

    drive = Drive()
    logo = ensure_logo(drive, settings)

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

        # 먼저 원본을 그대로 받는다. 파일 안의 EXIF 촬영 시각을 봐야
        # 진짜 찍은 순서를 알 수 있는데, 그러려면 파일이 손에 있어야 한다.
        photo_dir = work_dir / slugify(source.name)
        photo_dir.mkdir(parents=True, exist_ok=True)
        raw_by_id: dict[str, Path] = {}
        for file in files:
            raw = photo_dir / f"원본-{file.id[:10]}-{file.name}"
            if not raw.exists():
                drive.download(file.id, raw)
            raw_by_id[file.id] = raw

        # 찍은 순서대로 다시 세운다.
        # 아이폰 사진(IMG_7499.HEIC)은 파일명에 시각이 없어서 예전에는
        # 드라이브 업로드 시각으로 세웠는데, 한 번에 20여 장을 올리면
        # 업로드가 병렬로 끝나 순서가 뒤섞였다. 그러면 상품 사진과 가격표
        # 사진이 서로 떨어져서 짝을 못 찾는다(08-25 일산점: 23장 → 묶음 22개).
        files.sort(
            key=lambda f: exif_capture_time(raw_by_id[f.id], settings.timezone)
            or capture_time(f, settings.timezone)
        )

        paths_by_id: dict[str, Path] = {}
        for i, file in enumerate(files, start=1):
            dest = photo_dir / f"{i:03d}-{file.name}"
            _place(raw_by_id[file.id], dest)
            paths_by_id[file.id] = dest

        photo_paths = [paths_by_id[f.id] for f in files]

        # ── 통판독: 사진 전부를 한 번에 보여주고 상품별로 정리하게 한다 ──
        # 좁은 질문 넷으로 쪼개던 예전 방식은 앞 단계가 버린 정보를 되살릴 수
        # 없었다. 여기서 성공하면 묶기·이름·가격·카드 사진이 한 번에 끝난다.
        planned = _plan_products(
            client,
            photo_paths,
            [f.id for f in files],
            source=source,
            store_name=settings.store_name,
            limit=remaining,
        )
        if planned is not None:
            result.reading_mode = "한 번에 전부 보고 판단"
            if remaining is not None:
                remaining -= len(planned)
            result.groups += len(planned)
            log.info("[%s] 사진 %d장 → 상품 %d개 (통판독)", source.name, len(files), len(planned))
            for product in planned:
                log.info(
                    "  [%s %02d] %s | 사진 %s | %s → %s | 검토필요=%s %s",
                    source.name,
                    product.group_index,
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
            continue

        # ── 통판독이 안 되면 예전 4단계 방식으로 물러난다 ──
        log.warning("[%s] 통판독이 안 돼서 예전 방식(분류→묶기→판독)으로 진행합니다", source.name)
        result.reading_mode = "예전 방식(분류→묶기→판독)"
        classes = classify_photos(client, photo_paths, model=client.vision_model)
        kinds = [c.kind for c in classes]
        items = [c.item for c in classes]
        shows = [c.product_visible for c in classes]
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
            by_id = {f.id: i for i, f in enumerate(files)}
            known_seen = [shows[by_id[f.id]] for f in group.files]
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
                    known_shows=known_seen,
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

    # 3) 카드에 쓸 사진을 한 장씩 검문한다 (가격표 사진이 배경으로 나가는 것을 막는 마지막 관문)
    _screen_card_photos(client, result)

    # 4) 인터넷에서 제품을 찾아 짧은 설명을 붙인다 (확인 안 되면 안 붙인다) --
    research.research_all(client, result.products, model=client.writing_model)

    # 4) 카드뉴스 만들기 ------------------------------------------------------
    counters: dict[str, int] = {}
    for product in result.published:
        counters[product.source_name] = counters.get(product.source_name, 0) + 1
        card = CardData(
            product_name=product.product_name,
            one_liner=product.card_line,
            condition_note=product.card_condition,
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
        render_card(card, product.best_photo, path, logo=logo)
        result.cards.append(path)

    # 4-1) 릴스 맨 앞장에 붙일 표지 ------------------------------------------
    if result.cards and settings.reel_enabled:
        try:
            result.cover = render_cover(
                out_dir / "카드뉴스" / "00-표지.png",
                date_label=target_day.strftime("%Y.%m.%d"),
                store_name=settings.store_name,
                headline=settings.reel_headline,
                item_count=len(result.cards),
                logo=logo,
            )
        except Exception as exc:
            # 표지가 없다고 릴스를 통째로 포기하지 않는다 — 상품 카드만으로도 영상은 된다
            log.warning("릴스 표지 생성 실패(표지 없이 진행): %s", exc)

        # 영상은 인스타 설정과 상관없이 만들어 둔다. 자동 게시가 막힌 날에도
        # 드라이브에 영상이 있으면 손으로 올릴 수 있다.
        # 카드와 같은 폴더(카드뉴스/리퍼)에 둔다 — 그날 결과물이 한자리에 모인다.
        try:
            frames = ([result.cover] if result.cover else []) + result.cards
            result.reel_video = reels.build_slideshow(
                frames,
                out_dir / "카드뉴스" / _reel_folder(result) / f"{day_slug}-릴스.mp4",
                seconds_per_card=settings.reel_seconds_per_card,
            )
        except Exception as exc:
            # 조용히 넘기지 않는다. 리포트에 남겨야 영상이 왜 없는지 알 수 있다.
            result.reel_error = str(exc)
            result.step_failures.append(f"릴스 영상: {exc}")
            log.warning("릴스 영상 생성 실패: %s", exc)

    # 5) BEST5 블로그 ---------------------------------------------------------
    # 카드뉴스는 이미 다 만들었다. 여기서 넘어져도 그걸 날리지 않는다.
    # (실제로 블로그 한 칸의 형식이 어긋나 일산 카드뉴스 13장이 통째로 사라졌다)
    picks: list = []
    try:
        picks = pick_best(
            result.published, count=settings.best_count, client=client, model=client.writing_model
        )
    except Exception as exc:
        log.error("BEST 상품 고르기 실패, 카드뉴스는 그대로 발행합니다: %s", exc)
        result.step_failures.append(f"BEST 상품 고르기: {exc}")

    if picks:
        try:
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
        except Exception as exc:
            log.error("블로그 글 작성 실패, 카드뉴스는 그대로 발행합니다: %s", exc)
            result.step_failures.append(f"블로그 글: {exc}")

    # 6) 카톡 공지 / 인스타 캡션 ---------------------------------------------
    best_products = [p for p, _ in picks] or result.published
    kakao_text = ""
    try:
        kakao_text = _write_social(result, settings, best_products, out_dir, day_slug, target_day)
    except Exception as exc:
        log.error("소셜 문구 작성 실패, 카드뉴스는 그대로 발행합니다: %s", exc)
        result.step_failures.append(f"소셜 문구: {exc}")

    # 7) 근거 자료 + 실행 리포트 ---------------------------------------------
    save_products(result.products, out_dir / "_data" / "products.json")

    if dry_run:
        (out_dir / "_data" / "리포트.md").write_text(_report(result, settings), encoding="utf-8")
        log.info("dry-run: 드라이브 업로드·인스타 게시·알림을 건너뜁니다")
        return result

    # 8) 인스타그램 게시 — 스토리 + 피드 (컴퓨터 없이 자동) -------------------
    if settings.instagram_enabled and result.cards:
        result.stories = instagram.publish_cards(
            result.cards,
            key_prefix=f"cardnews/{day_slug}",
            max_stories=settings.max_stories_per_day,
            delay_seconds=settings.story_delay_seconds,
        )
        if settings.reel_enabled and result.reel_video:
            result.reel = instagram.publish_reel_video(
                result.reel_video,
                caption=_read_caption(result),
                key_prefix=f"reels/{day_slug}",
                cover=result.cover,
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
            "reel": bool(result.reel and result.reel.ok),
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


# 한 번에 넘기는 사진 수의 상한.
# 08-29 평택은 38장이었는데 통판독이 실패해 예전 방식으로 물러났다.
# 사진이 많아지면 한 번의 호출이 감당하지 못한다. 그래서 **찍은 순서대로**
# 잘라서 여러 번 통판독한다. 자르는 자리에서 상품 하나가 갈라질 수 있지만
# 그건 경계마다 최대 한 개고, 통째로 예전 방식으로 물러나는 것보다 훨씬 낫다.
PLAN_CHUNK = 24


def _chunks(n: int, size: int) -> list[tuple[int, int]]:
    """0..n 을 size 이하의 덩어리로 고르게 나눈 (시작, 끝) 목록."""
    if n <= size:
        return [(0, n)]
    parts = -(-n // size)  # 올림
    base, extra = divmod(n, parts)
    out, start = [], 0
    for i in range(parts):
        end = start + base + (1 if i < extra else 0)
        out.append((start, end))
        start = end
    return out


def _plan_products(
    client,
    photo_paths: list[Path],
    file_ids: list[str],
    *,
    source,
    store_name: str,
    limit: int | None,
) -> list | None:
    """사진을 한 번에 보고 상품 목록을 만든다. 안 되면 None.

    코워크에서 하던 방식이다 — 스무 장을 펼쳐놓고 한 사람이 다 본다.
    사진이 PLAN_CHUNK 보다 많으면 찍은 순서대로 잘라서 여러 번 본다.
    한 덩어리라도 실패하면 None 을 돌려 예전 방식으로 넘긴다 —
    그 덩어리의 사진이 조용히 사라지는 것보다 낫다.
    """
    if not photo_paths:
        return None

    products: list = []
    spans = _chunks(len(photo_paths), PLAN_CHUNK)
    if len(spans) > 1:
        log.info("사진 %d장 → %d번에 나눠 통판독합니다", len(photo_paths), len(spans))
    for start, end in spans:
        paths = photo_paths[start:end]
        ids = file_ids[start:end]
        try:
            plan = plan_store_photos(
                client,
                paths,
                model=client.vision_model,
                source_kind=source.kind,
                store_name=store_name,
            )
        except LLMQuotaError:
            raise
        except Exception as exc:
            log.warning(
                "통판독 실패 (사진 %d~%d번, %s): %s",
                start + 1,
                end,
                type(exc).__name__,
                exc,
            )
            return None
        products += products_from_plan(
            plan,
            paths,
            ids,
            source_name=source.name,
            source_kind=source.kind,
            eyebrow=source.eyebrow,
            start_index=len(products) + 1,
        )

    if not products:
        log.warning("통판독이 상품을 하나도 못 찾았습니다")
        return None
    if limit is not None and len(products) > limit:
        log.warning("상품 %d개 중 하루 상한(%d)만큼만 만듭니다", len(products), limit)
        products = products[:limit]
    return products


def _place(src: Path, dest: Path) -> None:
    """받아둔 원본을 촬영 순서 번호가 붙은 이름으로 놓는다.

    같은 파일을 두 번 받지 않으려고 하드링크를 먼저 시도하고,
    안 되면(파일시스템이 다르거나 권한이 없으면) 복사한다.
    """
    if dest.exists():
        dest.unlink()
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(src, dest)
    except OSError:
        shutil.copy2(src, dest)


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
        f"# {result.day} {result.store_name or '매장'} 콘텐츠 자동 발행 리포트",
        "",
        f"- 사진: {result.photos_seen}장 ("
        + ", ".join(f"{name} {n}장" for name, n in result.per_source.items())
        + ")",
        f"- 상품 묶음: {result.groups}개",
        f"- 카드뉴스: {len(result.cards)}장",
        f"- 블로그: {'생성' if result.blog_files else '없음'}",
    ]
    if result.reading_mode:
        lines.insert(4, f"- 사진 판독: {result.reading_mode}")
    if result.failed_groups:
        lines.append(f"- ⚠️ 판독하지 못한 묶음: {result.failed_groups}개")
    for failure in result.step_failures:
        lines.append(f"- ⚠️ 만들지 못한 것 — {failure}")
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
        if p.cautions:
            lines.append(f"   · ⚠️ 확인 권장: {p.cautions}")

    cautioned = [p for p in result.published if p.cautions]
    if cautioned:
        lines += [
            "",
            "## 확인 권장 (카드뉴스는 만들었습니다)",
            "가격은 가격표에서 읽은 그대로입니다. 상품명 표기만 한 번 봐주세요.",
        ]
        for p in cautioned:
            lines.append(f"- [{p.source_name}] {p.product_name} — {p.cautions}")

    if result.needs_review:
        lines += ["", "## 카드뉴스를 만들지 못한 것"]
        for p in result.needs_review:
            lines.append(
                f"- [{p.source_name}] {p.product_name or '(상품명 불명)'} — "
                f"{p.review_reason or '사유 미상'}"
                f"  · 사진: {', '.join(Path(x).name for x in p.photo_paths)}"
                f" ({'+'.join(p.photo_kinds) or '?'})"
            )
    if result.reel_error:
        lines.append(f"- 릴스 영상: **만들지 못했습니다** — {result.reel_error}")
    elif result.reel_video:
        lines.append(f"- 릴스 영상: {result.reel_video.name} (표지 포함 {len(result.cards) + (1 if result.cover else 0)}장)")
    if result.reel is not None:
        if result.reel.skipped_reason:
            lines.append(f"- 인스타 릴스 게시: 건너뜀 — {result.reel.skipped_reason}")
        elif result.reel.ok:
            lines.append("- 인스타 릴스 게시: 완료")
        else:
            lines.append(f"- 인스타 릴스 게시: 실패 — {result.reel.error}")
    if result.stories and result.stories.failed:
        lines += ["", "## 인스타 스토리 실패"]
        for r in result.stories.failed:
            lines.append(f"- {r.card.name} — {r.error}")
    lines += ["", f"생성 시각 기준 매장: {settings.store_name}"]
    return "\n".join(lines) + "\n"


def print_summary(result: RunResult) -> None:
    who = f"{result.store_name} " if result.store_name else ""
    if result.skipped_reason:
        print(f"⏭  {who}{result.day}: {result.skipped_reason}")
        return
    counts = ", ".join(f"{name} {n}장" for name, n in result.per_source.items())
    print(f"✅ {who}{result.day} 완료")
    print(f"   사진 {result.photos_seen}장 ({counts}) → 상품 {result.groups}개 → 카드뉴스 {len(result.cards)}장")
    if result.blog_files:
        print(f"   블로그: {result.blog_files[0].name} (+ 네이버 붙여넣기용 HTML)")
    if result.stories is not None:
        if result.stories.skipped_reason:
            print(f"   인스타 스토리: 건너뜀 — {result.stories.skipped_reason}")
        else:
            print(f"   인스타 스토리: {len(result.stories.published)}건 게시")
    if result.reel_error:
        print(f"   ⚠️  릴스 영상을 만들지 못했습니다 — {result.reel_error}")
    elif result.reel_video:
        print(f"   릴스 영상: {result.reel_video.name}")
    if result.reel is not None:
        if result.reel.skipped_reason:
            print(f"   인스타 릴스 게시: 건너뜀 — {result.reel.skipped_reason}")
        elif result.reel.ok:
            print(f"   인스타 릴스: 게시 완료 (표지 포함 {result.reel.card_count}장)")
        else:
            print(f"   인스타 릴스: 실패 — {result.reel.error}")
    if result.needs_review:
        print(f"   ⚠️  확인 필요 {len(result.needs_review)}건")
    if result.failed_groups:
        print(f"   ⚠️  판독 실패 {result.failed_groups}개")
    for failure in result.step_failures:
        print(f"   ⚠️  {failure}")
    if result.quota_note:
        print(f"   ⚠️  {result.quota_note}")
    if result.drive_folder_url:
        print(f"   드라이브: {result.drive_folder_url}")
    if result.notified:
        sent = [k for k, v in result.notified.items() if v]
        print(f"   알림 전송: {', '.join(sent) if sent else '(설정된 채널 없음)'}")


def _write_social(result, settings, best_products, out_dir: Path, day_slug: str, target_day) -> str:
    """카톡 공지와 인스타 캡션을 파일로 남기고 카톡 문구를 돌려준다."""
    if not best_products:
        return ""
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
    return kakao_text


def _screen_card_photos(client, result: RunResult) -> None:
    """카드 배경 후보를 병렬로 검문한다. 상품끼리 독립이라 동시에 돌린다."""
    from concurrent.futures import ThreadPoolExecutor

    targets = [p for p in result.products if p.publishable]
    if not targets:
        return
    log.info("카드에 쓸 사진 %d개를 검문합니다", len(targets))
    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(lambda p: pick_card_photo(client, p, model=client.vision_model), targets))

    blocked = [p for p in targets if not p.publishable]
    for product in blocked:
        if product not in result.needs_review:
            result.needs_review.append(product)
    if blocked:
        log.warning("가격표만 크게 찍혀 카드를 만들지 않는 상품 %d개", len(blocked))


def _read_caption(result: "RunResult") -> str:
    """이미 만들어 둔 인스타 캡션 파일을 읽어 릴스 캡션으로 쓴다."""
    for path in result.social_files:
        if "인스타캡션" in path.name:
            try:
                return path.read_text(encoding="utf-8")
            except OSError:
                break
    return ""


def _reel_folder(result: "RunResult") -> str:
    """릴스를 넣을 카드뉴스 하위 폴더. 카드가 가장 많이 나온 쪽(보통 '리퍼')."""
    counts: dict[str, int] = {}
    for product in result.published:
        counts[product.source_name] = counts.get(product.source_name, 0) + 1
    if not counts:
        return "리퍼"
    return slugify(max(counts, key=counts.get))
