#!/usr/bin/env python3
"""주제곡에 한국어 가사를 얹는다 — 반주(make_jingle) + 음성(MeloTTS).

왜 이렇게 만드는가: 노래를 불러 주는 음악 모델에 손이 닿지 않는다.
  - 허깅페이스 MiniMax Music 3 → 익명 ZeroGPU 할당량이 계속 막힘
  - Higgsfield → 음악 생성 미지원, 크레딧 0, 무료 할당량도 없음
그래서 **반주는 직접 합성하고(scripts/make_jingle.py), 가사는 음성 합성으로
읽혀서** 박자에 맞춰 얹는다. CM송에서 후렴을 외치는 방식과 같다.

솔직히 밝혀 둘 것: **노래가 아니라 외치는 목소리다.** 음높이를 따라가지 않는다.
광고 지시문이 인트로·아웃트로를 "chanted and rhythmic" 로 잡아 둔 건 이 방식과
맞지만, 후렴을 멜로디로 부르게 하려면 음악 모델이 필요하다.

상업 사용:
  - MeloTTS 코드 MIT, myshell-ai/MeloTTS-Korean 가중치 MIT → 표기 의무 없음
  - 발음/운율 보조로 kykim/bert-kor-base 를 쓰는데 라이선스 표기가 없다.
    소리를 만드는 모델이 아니고 결과물에 포함되지도 않는다.
  - 표기 의무가 없으므로 `reel_music_credit` 는 비워 둔다.

의존성이 무겁다 (torch, MeloTTS, mecab 사전, NLTK 자료 ~2GB). 매일 도는
파이프라인에는 필요 없다 — 만들어진 mp3 를 저장소에 커밋해 두고 쓴다.
그래서 requirements.txt 에 넣지 않았다. 다시 만들 때만 아래를 깔면 된다:

    pip install --index-url https://download.pytorch.org/whl/cpu torch torchaudio
    pip install "git+https://github.com/myshell-ai/MeloTTS.git" unidic-lite
    pip uninstall -y unidic            # 빈 일본어 사전이 MeCab 초기화를 깨뜨린다
    NLTK_ALLOW_PROXIED_URLOPEN=1 python -c "import nltk; \
        [nltk.download(p, quiet=True) for p in ('cmudict','averaged_perceptron_tagger_eng')]"

사용:
    python scripts/make_theme_vocals.py fox assets/music/fox-theme.mp3
    python scripts/make_theme_vocals.py reborn out.mp3 --keep-work
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_jingle  # noqa: E402

SR = make_jingle.SR
BPM = 128.0
BAR = 4 * 60.0 / BPM  # 1.875초

# 가사를 마디 위에 놓는다. (시작 마디, 배정 마디 수, 가사)
# 릴스가 10~25초라 인트로 후킹이 **첫 마디**에 와야 한다.
LINES = [
    (0, 2, "{chant}"),
    (2, 2, "{verse1}"),
    (4, 2, "포장만 뜯긴 새 상품"),
    (6, 2, "검수 끝! 교환도 오케이!"),
    (8, 2, "가성비 좋은 신개념 쇼핑몰"),
    (10, 2, "{name} {name}"),
    (12, 2, "오늘도 반값 득템하러 가요"),
    (14, 2, "{chant}"),
]

STORES = {
    "fox": {
        "chant": "여우! 여우! 여우마켓!",
        "verse1": "똑똑하게 쇼핑하는 법",
        "name": "여우마켓",
    },
    "reborn": {
        "chant": "리본! 리본! 리본마켓!",
        "verse1": "정가 주고 사지 마요",
        "name": "리본마켓",
    },
}

TTS_SPEED = 1.25  # 광고 톤. 느리게 읽으면 한 마디에 안 들어간다.
VOCAL_GAIN = 0.85
DUCK_DB = -5.0  # 목소리가 있는 동안 반주를 이만큼 낮춘다 (말이 또렷해야 한다)


def read_wav(path: Path) -> np.ndarray:
    """모노 float32 로 읽는다. MeloTTS 는 모노 16bit 로 쓴다."""
    with wave.open(str(path), "rb") as fh:
        frames = fh.readframes(fh.getnframes())
        data = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768.0
        if fh.getnchannels() == 2:
            data = data.reshape(-1, 2).mean(axis=1)
        rate = fh.getframerate()
    if rate != SR:  # 표본율이 다르면 선형보간으로 맞춘다
        n = int(len(data) * SR / rate)
        data = np.interp(np.linspace(0, len(data) - 1, n), np.arange(len(data)), data)
    return data.astype(np.float32)


def fit_to(path: Path, seconds: float, ffmpeg: str) -> np.ndarray:
    """가사 한 줄을 배정된 길이 안에 넣는다.

    길면 ffmpeg atempo 로 빠르게 만든다 — 음높이는 그대로 두고 속도만 바꾼다.
    (표본율을 건드려 줄이면 목소리가 삐뚤어진다.)
    짧으면 그대로 둔다. 남는 여백이 오히려 숨 쉴 틈이 된다.
    """
    audio = read_wav(path)
    duration = len(audio) / SR
    if duration <= seconds:
        return audio
    tempo = min(2.0, duration / seconds)
    out = path.with_name(path.stem + "-fit.wav")
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(path),
           "-filter:a", f"atempo={tempo:.4f}", str(out)]
    if subprocess.run(cmd, capture_output=True, text=True).returncode != 0:
        return audio[: int(seconds * SR)]  # 최악의 경우 잘라서라도 맞춘다
    fitted = read_wav(out)
    return fitted[: int(seconds * SR)] if len(fitted) > seconds * SR else fitted


def synth_lines(store: str, work: Path) -> list[tuple[float, np.ndarray]]:
    """가사를 한 줄씩 합성해 (시작 초, 파형) 목록으로 돌려준다."""
    from melo.api import TTS  # 무거운 의존성 — 필요할 때만 불러온다

    from reborn.reels import ffmpeg_exe

    words = STORES[store]
    tts = TTS(language="KR", device="cpu")
    speaker = list(tts.hps.data.spk2id.values())[0]
    ffmpeg = ffmpeg_exe()
    work.mkdir(parents=True, exist_ok=True)

    placed: list[tuple[float, np.ndarray]] = []
    for index, (bar, bars, template) in enumerate(LINES):
        text = template.format(**words)
        raw = work / f"line{index:02d}.wav"
        tts.tts_to_file(text, speaker, str(raw), speed=TTS_SPEED)
        audio = fit_to(raw, bars * BAR, ffmpeg)
        placed.append((bar * BAR, audio))
        print(f"  {bar:>2}마디 {len(audio) / SR:4.1f}초  {text}")
    return placed


def mix(bed: np.ndarray, lines: list[tuple[float, np.ndarray]]) -> np.ndarray:
    """반주 위에 목소리를 얹고, 목소리가 있는 동안 반주를 낮춘다."""
    total = len(bed)
    vocal = np.zeros(total, dtype=np.float32)
    for start, audio in lines:
        at = int(start * SR)
        end = min(total, at + len(audio))
        if end > at:
            vocal[at:end] += audio[: end - at]

    peak = float(np.max(np.abs(vocal)))
    if peak > 0:
        vocal *= VOCAL_GAIN / peak

    # 목소리 구간을 부드럽게 따서 덕킹 곡선을 만든다. 갑자기 줄면 숨 넘어가는
    # 소리가 난다 — 40ms 창으로 뭉갠 뒤 쓴다.
    window = int(0.04 * SR)
    envelope = np.convolve(np.abs(vocal), np.ones(window, dtype=np.float32) / window, "same")
    present = np.clip(envelope / (envelope.max() + 1e-9) * 6.0, 0.0, 1.0)
    duck = 10 ** (DUCK_DB / 20.0)
    gain = (1.0 - present) + present * duck

    out = bed * gain[:, None] + vocal[:, None] * np.array([0.72, 0.72], dtype=np.float32)
    peak = float(np.max(np.abs(out)))
    if peak > 0:
        out *= 0.89 / peak
    return out.astype(np.float32)


def main() -> int:
    parser = argparse.ArgumentParser(description="주제곡에 한국어 가사를 얹는다")
    parser.add_argument("store", choices=sorted(STORES), help="fox 또는 reborn")
    parser.add_argument("out", help="내보낼 파일 (.mp3 또는 .wav)")
    parser.add_argument("--work", default=None, help="중간 wav 를 둘 폴더")
    args = parser.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from reborn.reels import ffmpeg_exe

    bars = LINES[-1][0] + LINES[-1][1]
    bed = make_jingle.build(bpm=BPM, bars=bars)

    work = Path(args.work) if args.work else Path("out") / "jingle-work" / args.store
    print(f"[{args.store}] 가사 {len(LINES)}줄 합성")
    lines = synth_lines(args.store, work)

    audio = mix(bed, lines)
    out_path = Path(args.out)
    make_jingle.write_mp3(audio, out_path, ffmpeg_exe())
    print(f"{out_path} ({len(audio) / SR:.1f}초, {bars}마디, 가사 있음)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
