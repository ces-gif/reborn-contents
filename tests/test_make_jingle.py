"""주제곡 반주 합성기 검증.

`scripts/make_jingle.py` 는 numpy 를 쓰는데, 매일 도는 파이프라인은 numpy 가
필요 없다 (mp3 는 저장소에 커밋해 둔다). 그래서 requirements.txt 에 넣지 않고
numpy 가 없는 환경에서는 이 테스트를 건너뛴다.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

# pytest.importorskip 은 버전에 따라 ImportError 종류를 가려 잡는다. 직접 잡는다.
try:
    import numpy as np

    import make_jingle
except ImportError:  # pragma: no cover - numpy 있는 환경에서는 안 온다
    pytest.skip("합성기 전용 의존성(numpy)이 없습니다", allow_module_level=True)


def test_길이가_마디_수와_박자에_맞는다():
    audio = make_jingle.build(bpm=128, bars=8)
    # 8마디 × 4박 × (60/128)초 = 15초. 끝 여운 0.6초를 더한 만큼.
    expected = 8 * 4 * (60 / 128) + 0.6
    assert len(audio) / make_jingle.SR == pytest.approx(expected, abs=0.05)


def test_스테레오다():
    assert make_jingle.build(bars=2).shape[1] == 2


def test_찌그러지지_않는다():
    """피크가 1.0 을 넘으면 인코딩에서 깨진 소리가 난다."""
    assert float(np.max(np.abs(make_jingle.build(bars=4)))) <= 1.0


def test_중간에_소리가_끊기지_않는다():
    """광고 음악이라 빈 구간이 있으면 안 된다. 짧은 릴스에서 무음으로 들린다."""
    audio = make_jingle.build(bars=8)
    mono = audio.mean(axis=1)
    hop = int(0.05 * make_jingle.SR)
    # 끝 여운(마지막 1초)은 제외하고 본다
    body = mono[: -make_jingle.SR]
    frames = np.array([(body[i : i + hop] ** 2).mean() for i in range(0, len(body) - hop, hop)])
    loud = np.sqrt(frames)
    assert (loud < loud.mean() * 0.1).sum() == 0


def test_첫_박부터_소리가_난다():
    """느린 인트로가 붙으면 3초짜리 릴스에서 후킹이 안 들린다."""
    audio = make_jingle.build(bars=4)
    first = audio[: int(0.05 * make_jingle.SR)]
    assert float(np.max(np.abs(first))) > 0.05


def test_박자가_지정한_BPM_으로_찍힌다():
    """자기상관의 최대 주기가 한 박 길이여야 리듬이 있는 음악이다."""
    audio = make_jingle.build(bpm=128, bars=8)
    mono = audio.mean(axis=1)
    hop = int(0.01 * make_jingle.SR)
    rms = np.sqrt(
        np.array([(mono[i : i + hop] ** 2).mean() for i in range(0, len(mono) - hop, hop)])
    )
    centred = rms - rms.mean()
    ac = np.correlate(centred, centred, mode="full")[len(centred) - 1 :]
    lo, hi = 30, 120  # 0.30초 ~ 1.20초 사이에서 주기를 찾는다
    lag_seconds = (lo + int(np.argmax(ac[lo:hi]))) * 0.01
    assert lag_seconds == pytest.approx(60 / 128, abs=0.02)


def test_저역과_고역이_모두_있다():
    """킥·베이스만 있고 고역이 없으면 먹먹하게 들린다."""
    mono = make_jingle.build(bars=4).mean(axis=1)
    spec = np.abs(np.fft.rfft(mono))
    freq = np.fft.rfftfreq(len(mono), 1 / make_jingle.SR)
    low = spec[(freq >= 20) & (freq < 200)].mean()
    high = spec[(freq >= 2000) & (freq < 16000)].mean()
    assert low > 0 and high > 0
