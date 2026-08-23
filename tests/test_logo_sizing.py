"""매장마다 로고 모양이 달라도 카드에서 비슷한 크기로 보이는지."""

from __future__ import annotations

from PIL import Image

from reborn.branding import FAINT_ALPHA, fit_logo, trim_margins
from reborn.cardnews import LOGO_AREA, LOGO_MAX_H, LOGO_MAX_W


def fitted(w: int, h: int):
    return fit_logo(Image.new("RGBA", (w, h)), area=LOGO_AREA, max_w=LOGO_MAX_W, max_h=LOGO_MAX_H)


def test_shapes_end_up_the_same_visual_weight():
    """가로로 긴 워드마크와 정사각형 마스코트가 같은 크기로 보여야 한다.

    높이만 맞추던 예전 방식에서는 여우마켓 로고(거의 정사각형)가
    리본마켓 로고 옆에서 콩알만 하게 나왔다.
    """
    wide = fitted(1200, 300)      # 워드마크형
    square = fitted(603, 657)     # 마스코트+글자형
    assert abs(wide.width * wide.height - square.width * square.height) < LOGO_AREA * 0.05


def test_a_wide_wordmark_keeps_the_original_look():
    """리본마켓 카드가 예전과 같아야 한다 (312 x 78)."""
    assert fitted(1200, 300).size == (312, 78)


def test_aspect_ratio_is_preserved():
    for size in [(1200, 300), (603, 657), (800, 800)]:
        out = fitted(*size)
        assert abs(out.width / out.height - size[0] / size[1]) < 0.05


def test_nothing_overflows_the_box():
    for size in [(4000, 100), (100, 4000), (50, 50)]:
        out = fitted(*size)
        assert out.width <= LOGO_MAX_W and out.height <= LOGO_MAX_H


def test_faint_glow_is_treated_as_margin():
    """여우마켓 로고는 옅은 발광이 이미지 전체에 깔려 있었다.

    알파가 0보다 크기만 하면 남기는 방식으로는 한 픽셀도 못 잘라내서,
    카드에 로고가 콩알만 하게 박혔다.
    """
    img = Image.new("RGBA", (200, 200), (255, 255, 255, FAINT_ALPHA - 5))  # 전면 옅은 발광
    img.paste((255, 90, 0, 255), (80, 80, 120, 120))                        # 가운데 진짜 그림
    assert trim_margins(img).size == (40, 40)


def test_a_normal_transparent_logo_is_untouched():
    img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    img.paste((255, 90, 0, 255), (50, 60, 150, 140))
    assert trim_margins(img).size == (100, 80)
