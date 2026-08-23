"""사진 한 장씩 '가격표냐 상품이냐'를 먼저 판독하는 1차 패스."""

from PIL import Image

from reborn import vision


def photos(tmp_path, n):
    paths = []
    for i in range(1, n + 1):
        p = tmp_path / f"{i:02d}.jpg"
        Image.new("RGB", (80, 60), (200, 200, 200)).save(p)
        paths.append(p)
    return paths


class Client:
    def __init__(self, answers=None, fail=False):
        self.answers = list(answers or [])
        self.fail = fail
        self.batches: list[int] = []

    def structured(self, *, system, parts, schema, max_tokens=8000, search=False, model=None):
        images = [p for p in parts if p["type"] == "image"]
        self.batches.append(len(images))
        if self.fail:
            raise RuntimeError("모델이 답을 안 했습니다")
        kinds = [self.answers.pop(0) if self.answers else "product" for _ in images]
        return vision.PhotoBatch(
            photos=[vision.PhotoClass(index=i + 1, kind=k, item="") for i, k in enumerate(kinds)]
        )


def test_classifies_every_photo_in_order(tmp_path):
    client = Client(["both", "price_tag", "product", "other"])
    got = vision.classify_photos(client, photos(tmp_path, 4), model="m")
    assert [c.kind for c in got] == ["both", "price_tag", "product", "other"]
    assert [c.index for c in got] == [1, 2, 3, 4]


def test_splits_into_batches_and_renumbers(tmp_path):
    client = Client(["both"] * 10)
    got = vision.classify_photos(client, photos(tmp_path, 10), model="m", batch_size=4)
    assert client.batches == [4, 4, 2]
    assert [c.index for c in got] == list(range(1, 11))


def test_failed_batch_falls_back_to_product_not_dropped(tmp_path):
    """판독에 실패해도 사진을 버리지 않는다 — 상품 사진으로 보고 넘어간다."""
    client = Client(fail=True)
    got = vision.classify_photos(client, photos(tmp_path, 5), model="m", batch_size=2)
    assert len(got) == 5
    assert all(c.kind == "product" for c in got)
