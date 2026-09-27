#!/usr/bin/env python3
"""매장 주제곡 반주(instrumental)를 직접 합성한다.

왜 직접 만드는가: 허깅페이스 MiniMax Music 3 은 무료 GPU 할당량이 막혀 손에
닿지 않는 날이 있고(컨테이너가 공용 프록시 IP 로 나가 익명 할당량을 나눠 쓴다),
Higgsfield 는 음악 생성을 아예 지원하지 않는다. 그래서 외부 모델 없이 도는
길을 하나 둔다. 여기서 나온 소리는 우리가 만든 것이라 **라이선스 표기가 필요
없다** — 릴스 캡션의 `🎵 …` 한 줄도 붙지 않는다.

가사(노래)는 없다. 브랜드 이름을 잘못 부르는 것보다 반주만 깔리는 게 낫다.
노래가 들어간 판이 준비되면 같은 파일명으로 덮어쓰면 된다.

사용:
    python scripts/make_jingle.py assets/music/fox-theme.mp3
    python scripts/make_jingle.py out.mp3 --bars 16 --bpm 128

소리의 성격은 `assets/music/주제곡-가사.md` 의 제작 지시문을 그대로 따른다 —
128 BPM, C major, 첫 박부터 밝고 빠르게, 네 박 킥 + 2·4 박 클랩, 통통 튀는
신스 플럭과 둥근 베이스, 후렴 자리에 글로켄슈필 반짝임.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

SR = 44100
BPM = 128.0
BARS = 16

# C major I–V–vi–IV. 한 마디에 한 코드. 광고 음악에서 가장 안전하게 밝은 진행이다.
CHORDS = [
    ("C", [261.63, 329.63, 392.00]),   # C  E  G
    ("G", [196.00, 246.94, 392.00]),   # G  B  G
    ("Am", [220.00, 261.63, 329.63]),  # A  C  E
    ("F", [174.61, 261.63, 349.23]),   # F  C  F
]
ROOTS = [130.81, 98.00, 110.00, 87.31]  # 한 옥타브 아래 베이스 루트


def _env(n: int, attack: float, decay: float) -> np.ndarray:
    """어택-디케이 엔벨로프. 클릭(딱 소리) 안 나게 어택을 아주 짧게라도 준다."""
    a = max(1, int(attack * SR))
    out = np.ones(n, dtype=np.float32)
    a = min(a, n)
    out[:a] = np.linspace(0.0, 1.0, a, dtype=np.float32)
    if decay > 0:
        out[a:] = np.exp(-np.arange(n - a, dtype=np.float32) / (decay * SR))
    return out


def _add(buf: np.ndarray, start: int, sound: np.ndarray, pan: float = 0.0) -> None:
    """buf(스테레오) 의 start 위치에 sound(모노) 를 섞는다. pan 은 -1(좌)~+1(우)."""
    end = min(len(buf), start + len(sound))
    if end <= start:
        return
    chunk = sound[: end - start]
    left = np.sqrt((1.0 - pan) / 2.0)
    right = np.sqrt((1.0 + pan) / 2.0)
    buf[start:end, 0] += chunk * left
    buf[start:end, 1] += chunk * right


def kick(dur: float = 0.18) -> np.ndarray:
    """피치가 떨어지는 사인 = 펀치 있는 킥. 네 박 내내 이 소리가 바닥을 잡는다."""
    t = np.arange(int(dur * SR), dtype=np.float32) / SR
    freq = 120.0 * np.exp(-t * 28.0) + 45.0
    phase = 2 * np.pi * np.cumsum(freq) / SR
    return (np.sin(phase) * _env(len(t), 0.001, 0.045) * 0.9).astype(np.float32)


def clap(dur: float = 0.12) -> np.ndarray:
    """노이즈 세 번 겹쳐서 손뼉. 한 번만 쓰면 '틱' 이 되고 겹치면 '짝' 이 된다."""
    n = int(dur * SR)
    rng = np.random.default_rng(7)
    noise = rng.standard_normal(n).astype(np.float32)
    noise = np.diff(noise, prepend=np.float32(0))  # 거친 하이패스 — 고역만 남긴다
    out = np.zeros(n, dtype=np.float32)
    for offset, gain in ((0, 1.0), (int(0.008 * SR), 0.7), (int(0.016 * SR), 0.5)):
        seg = noise[: n - offset] * _env(n - offset, 0.0005, 0.03) * gain
        out[offset : offset + len(seg)] += seg
    return out * 0.35


def hat(dur: float = 0.05, gain: float = 0.12) -> np.ndarray:
    n = int(dur * SR)
    rng = np.random.default_rng(11)
    noise = np.diff(rng.standard_normal(n).astype(np.float32), prepend=np.float32(0))
    return noise * _env(n, 0.0003, 0.012) * gain


def _harmonics(freq: float, dur: float, weights, decay: float) -> np.ndarray:
    """배음을 더해 음색을 만든다. 필터 없이 밝은 소리를 얻는 가장 단순한 방법."""
    t = np.arange(int(dur * SR), dtype=np.float32) / SR
    out = np.zeros_like(t)
    for i, w in enumerate(weights, start=1):
        if freq * i < SR / 2:  # 나이퀴스트 넘는 배음은 앨리어싱만 만든다
            out += w * np.sin(2 * np.pi * freq * i * t)
    return out * _env(len(t), 0.002, decay)


def pluck(freq: float, dur: float = 0.22) -> np.ndarray:
    """통통 튀는 신스 플럭. 16분음표 아르페지오의 주재료."""
    return _harmonics(freq, dur, (1.0, 0.5, 0.3, 0.18, 0.1, 0.06), 0.07) * 0.16


def bass(freq: float, dur: float) -> np.ndarray:
    """둥근 베이스. 2배음만 살짝 섞어 두께를 준다."""
    return _harmonics(freq, dur, (1.0, 0.25), 0.16) * 0.30


def glock(freq: float, dur: float = 0.9) -> np.ndarray:
    """글로켄슈필 반짝임. 마디 머리에서 제목 자리를 따라 울린다."""
    return _harmonics(freq, dur, (1.0, 0.0, 0.45, 0.0, 0.2), 0.28) * 0.11


def riser(dur: float) -> np.ndarray:
    """노이즈 라이저. 다음 마디로 밀어 넣는 소리."""
    n = int(dur * SR)
    rng = np.random.default_rng(23)
    noise = np.diff(rng.standard_normal(n).astype(np.float32), prepend=np.float32(0))
    return noise * np.linspace(0.0, 1.0, n, dtype=np.float32) ** 2.5 * 0.14


def build(bpm: float = BPM, bars: int = BARS) -> np.ndarray:
    beat = 60.0 / bpm
    bar = beat * 4
    total = int((bars * bar + 0.6) * SR)  # 끝에 여운 자리를 조금 남긴다
    buf = np.zeros((total, 2), dtype=np.float32)

    k, c = kick(), clap()
    h_soft, h_loud = hat(gain=0.09), hat(gain=0.16)

    for b in range(bars):
        bar_start = b * bar
        name, tones = CHORDS[b % len(CHORDS)]
        root = ROOTS[b % len(ROOTS)]

        # 리듬 — 에너지를 떨어뜨리지 않는다. 빈 마디도, 브레이크다운도 없다.
        for beat_i in range(4):
            _add(buf, int((bar_start + beat_i * beat) * SR), k)
            if beat_i in (1, 3):  # 2·4 박 클랩
                _add(buf, int((bar_start + beat_i * beat) * SR), c)
            for eighth in (0.0, 0.5):
                pos = bar_start + (beat_i + eighth) * beat
                _add(buf, int(pos * SR), h_loud if eighth == 0.0 else h_soft)

        # 베이스 — 8분음표로 통통 튄다
        for eighth in range(8):
            pos = bar_start + eighth * beat / 2
            _add(buf, int(pos * SR), bass(root, beat / 2 * 1.1))

        # 플럭 아르페지오 — 16분음표로 코드음을 훑는다. 좌우로 벌려 넓게 들린다
        for sixteenth in range(16):
            pos = bar_start + sixteenth * beat / 4
            tone = tones[sixteenth % len(tones)] * (2.0 if sixteenth % 8 >= 4 else 1.0)
            _add(buf, int(pos * SR), pluck(tone), pan=0.5 if sixteenth % 2 else -0.5)

        # 마디 머리 글로켄슈필. 4마디마다 한 옥타브 위로 올려 후렴을 열어준다
        _add(buf, int(bar_start * SR), glock(tones[-1] * (2.0 if b % 4 == 0 else 1.0)))

        # 4마디 묶음의 마지막 박에 라이저를 넣어 다음 묶음으로 밀어 넣는다
        if b % 4 == 3:
            _add(buf, int((bar_start + 3 * beat) * SR), riser(beat))

    # 마지막 한 방 — 종소리로 끝을 맺는다
    _add(buf, int((bars * bar - beat) * SR), glock(1046.5, dur=1.4))

    # 노멀라이즈. -1dBFS 를 넘기지 않게 두고, 릴스 쪽에서 볼륨과 페이드를 건다.
    peak = float(np.max(np.abs(buf)))
    if peak > 0:
        buf *= 0.89 / peak
    return buf


def write_mp3(audio: np.ndarray, out_path: Path, ffmpeg: str) -> None:
    pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype("<i2")
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "jingle.wav"
        with wave.open(str(wav), "wb") as fh:
            fh.setnchannels(2)
            fh.setsampwidth(2)
            fh.setframerate(SR)
            fh.writeframes(pcm.tobytes())
        out_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(wav)]
        if out_path.suffix.lower() == ".mp3":
            cmd += ["-c:a", "libmp3lame", "-b:a", "192k"]
        cmd += ["-ar", str(SR), "-ac", "2", str(out_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not out_path.exists():
            raise RuntimeError(f"인코딩 실패: {result.stderr.strip()[:300]}")


def _ffmpeg_exe() -> str:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from reborn.reels import ffmpeg_exe

    return ffmpeg_exe()


def main() -> int:
    parser = argparse.ArgumentParser(description="매장 주제곡 반주 합성")
    parser.add_argument("out", help="내보낼 파일 (.mp3 또는 .wav)")
    parser.add_argument("--bpm", type=float, default=BPM)
    parser.add_argument("--bars", type=int, default=BARS)
    args = parser.parse_args()

    audio = build(bpm=args.bpm, bars=args.bars)
    out_path = Path(args.out)
    write_mp3(audio, out_path, _ffmpeg_exe())
    print(f"{out_path} ({len(audio) / SR:.1f}초, {args.bpm:g}BPM, {args.bars}마디)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
