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
FADE_OUT = 0.6  # 끝에서 음악을 이만큼 줄인다 (뚝 끊기면 듣기 싫다)
MUSIC_VOLUME = 0.85


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


def audio_args(music: Path | None, total_seconds: float) -> tuple[list[str], list[str]]:
    """오디오 입력 인자와 필터 인자.

    음악이 있으면 영상 길이에 맞춰 **반복 재생하고 끝에서 페이드아웃**한다. 주제곡이
    영상보다 짧아도 끊기지 않고, 길어도 뚝 잘리지 않는다. 음악이 없으면 예전처럼
    무음 트랙을 넣는다 — 릴스는 오디오 트랙이 아예 없으면 처리에서 실패한 적이 있다.
    """
    if music is None:
        return (
            ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"],
            [],
        )
    fade_start = max(0.0, total_seconds - FADE_OUT)
    chain = (
        f"volume={MUSIC_VOLUME},"
        f"afade=t=out:st={fade_start:.3f}:d={FADE_OUT},"
        "aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo"
    )
    # -stream_loop -1 은 입력 **앞**에 와야 그 입력에만 걸린다
    return (["-stream_loop", "-1", "-i", str(music.resolve())], ["-af", chain])


def build_slideshow(
    cards: list[Path],
    out_path: Path,
    *,
    seconds_per_card: float = DEFAULT_SECONDS_PER_CARD,
    music: Path | None = None,
) -> Path:
    """카드들을 **번호 순서 그대로** 이어 붙인 세로 영상을 만든다.

    순서는 손님에게 중요하다 — 카드에 붙은 번호로 예약을 걸기 때문에, 영상이
    1·2·3 순서로 흘러야 "몇 번이요" 가 통한다. 여기서는 받은 목록을 절대
    다시 정렬하지 않는다.
    """
    if not cards:
        raise ValueError("영상으로 만들 카드가 없습니다")
    if music is not None and not Path(music).exists():
        log.warning("주제곡 파일이 없어 무음으로 만듭니다: %s", music)
        music = None

    durations = plan_durations(len(cards), seconds_per_card=seconds_per_card)
    total = sum(durations)
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

        audio_in, audio_filter = audio_args(music, total)
        cmd = [
            ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(listing),
            *audio_in,
            "-shortest",
            # 홀수 픽셀이면 H.264 가 거부한다. 짝수로 맞추고 비율은 건드리지 않는다.
            "-vf", f"fps={FPS},scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p",
            *audio_filter,
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            str(out_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not out_path.exists():
            raise RuntimeError(f"릴스 영상 생성 실패: {result.stderr.strip()[:400]}")

    log.info(
        "릴스 영상 생성: %s (카드 %d장, 약 %.1f초, 음악 %s)",
        out_path.name, len(cards), total, music.name if music else "없음",
    )
    return out_path
