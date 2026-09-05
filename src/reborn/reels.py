"""카드뉴스 PNG 들을 릴스 영상(MP4) 한 편으로 잇는다.

왜 릴스인가: 카드가 이미 1080x1920(9:16)이라 릴스 규격에 **그대로** 맞는다.
피드 캐러셀은 4:5 까지만 받아서 가격이 잘리는데, 릴스는 자를 필요가 없다.

ffmpeg 는 시스템에 깔린 것에 기대지 않는다. imageio-ffmpeg 가 정적 바이너리를
같이 들고 오므로 깃허브 러너에서도 apt 없이 그대로 돈다.

인스타 릴스 요건 중 우리가 지켜야 하는 것:
  - 3초 이상 (카드가 몇 장 없는 날 마지막 장을 늘려서 채운다)
  - MP4(H.264) + AAC 오디오. 무음이라도 오디오 트랙이 있어야 탈이 없다.
  - 세로 9:16 권장 — 우리 카드가 정확히 그 비율이다.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

log = logging.getLogger(__name__)

FPS = 30
MIN_DURATION = 3.2  # 인스타 최소 3초. 살짝 여유를 둔다.
DEFAULT_SECONDS_PER_CARD = 0.8


class FfmpegMissing(RuntimeError):
    pass


def ffmpeg_exe() -> str:
    """정적 ffmpeg 경로. 없으면 시스템 것이라도 찾아본다."""
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # pragma: no cover - 설치돼 있으면 여기 안 온다
        found = shutil.which("ffmpeg")
        if not found:
            raise FfmpegMissing(
                "ffmpeg 를 찾을 수 없습니다. `pip install imageio-ffmpeg` 로 설치하세요."
            )
        return found


def plan_durations(
    count: int,
    *,
    seconds_per_card: float = DEFAULT_SECONDS_PER_CARD,
    min_total: float = MIN_DURATION,
) -> list[float]:
    """장당 시간을 정한다. 총 길이가 인스타 최소치에 못 미치면 마지막 장을 늘린다."""
    if count <= 0:
        return []
    durations = [seconds_per_card] * count
    shortfall = min_total - sum(durations)
    if shortfall > 0:
        durations[-1] += shortfall
    return durations


def build_slideshow(
    cards: list[Path],
    out_path: Path,
    *,
    seconds_per_card: float = DEFAULT_SECONDS_PER_CARD,
) -> Path:
    """카드들을 순서대로 이어 붙인 세로 영상을 만든다."""
    if not cards:
        raise ValueError("영상으로 만들 카드가 없습니다")

    durations = plan_durations(len(cards), seconds_per_card=seconds_per_card)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        listing = Path(tmp) / "cards.txt"
        lines = []
        for card, seconds in zip(cards, durations):
            # concat demuxer 는 경로에 작은따옴표가 있으면 깨진다 — 이스케이프한다
            safe = str(card.resolve()).replace("'", r"'\''")
            lines.append(f"file '{safe}'")
            lines.append(f"duration {seconds:.3f}")
        # concat demuxer 는 마지막 파일을 한 번 더 적어야 그 장이 잘리지 않는다
        lines.append(f"file '{str(cards[-1].resolve())}'")
        listing.write_text("\n".join(lines), encoding="utf-8")

        cmd = [
            ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(listing),
            # 무음 오디오 트랙 — 릴스는 오디오가 없으면 처리에서 실패하는 경우가 있다
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-shortest",
            # 홀수 픽셀이면 H.264 가 거부한다. 짝수로 맞추고 비율은 건드리지 않는다.
            "-vf", f"fps={FPS},scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            str(out_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not out_path.exists():
            raise RuntimeError(f"릴스 영상 생성 실패: {result.stderr.strip()[:400]}")

    log.info(
        "릴스 영상 생성: %s (카드 %d장, 약 %.1f초)",
        out_path.name, len(cards), sum(durations),
    )
    return out_path
