# data/private — git에 올라가지 않는 폴더

이 폴더에는 **개인정보와 영업기밀**만 둔다. `.gitignore`로 제외되어 있다.

| 파일 | 내용 |
|---|---|
| `company.yaml` | 사업자등록번호, 대표자, 주소, 결제계좌 |
| `contacts.yaml` | 병원 교수·간호사·구매 담당자, 공급사 담당자 (실명·휴대폰·이메일) |
| `accounts.yaml` | 계정별 매출·할인율·렌트 재고·민감 메모 |
| `pricing.yaml` | 품목별 단가·상한금액 |

## 만드는 법

두 가지 중 하나:

```bash
# 1) 예시 파일을 복사해서 손으로 채운다
cp data/private/company.example.yaml data/private/company.yaml

# 2) 구글 드라이브의 인수인계 자료에서 자동 생성한다 (권장)
python scripts/bootstrap_private_data.py
```

컨테이너/PC를 새로 잡을 때마다 다시 만들면 된다. 이 폴더가 없어도 나머지 기능은
개인정보 없이 전부 동작한다 (이름 자리에 `(비공개)` 가 들어갈 뿐).
