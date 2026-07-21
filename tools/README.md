# staff-cards / tools

큐카드(cue-card) 렌더러. 발행 전 항상 raw URL 200 확인.

## make_card_v2.py — V2 포토 카드뉴스 (뉴스·정보 슬롯 기본)
실사진 배경 + 하단 그라디언트 + 중앙 대형 흰 타이포(악센트 키워드) + 출처 + `SEGMENT` 워드마크.
스타일 SSOT: `cards/sample-v2-photo-style.jpg`.

```bash
python3 make_card_v2.py --photo bg.jpg \
  --title $'매장은 비용이 아니라\n수익을 내는 자산입니다' \
  --kw "자산" \
  --sub "공간을 '측정되는 곳'으로 읽는 사람이 이깁니다" \
  --source "출처 · segment.im" --out card.jpg
```
- `--title` : `\n`(또는 `$'...\n...'`)으로 줄바꿈. 짧은 2줄 권장.
- `--kw`    : 타이틀 안에서 악센트 컬러를 줄 키워드.
- 배경 사진 : 무인물·무텍스트·무로고 실사진. Flux 생성 시
  `POST https://api.bfl.ai/v1/flux-pro-1.1` (header `x-key: $BFL_API_KEY`) → polling_url status=Ready → result.sample.

## make_card.py — V1 단색 flat 텍스트 카드 (최후 수단)
사진 확보 불가 시에만. `--style ivory|charcoal|clay|sage --role --title --body --source`.
> ⚠️ 빈 단색 카드(텍스트 없는 card-*.jpg) 직접 발행은 **금지**(Board 2026-07-21). 반드시 텍스트 렌더.
