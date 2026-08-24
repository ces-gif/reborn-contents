"""리본마켓 자동 콘텐츠 발행 파이프라인."""

__version__ = "1.0.0"

# 아이폰 사진(HEIC)을 Pillow 가 열 수 있게 미리 등록한다.
# 사진을 여는 곳이 여러 군데(판독·카드 렌더링)라 여기서 한 번에 해 둔다.
from .imaging import register_heif as _register_heif  # noqa: E402

_register_heif()
