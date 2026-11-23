# AIHuman · AI휴먼 (aihuman.ai.kr)

한국어 AI 휴머나이징 사이트입니다. AI 작성률을 무료로 검사하고, AI 탐지기에 걸리는 문장만 사람 문장으로 바꿉니다.

- `docs/` : GitHub Pages로 배포되는 사이트(정적 파일, 사용자 도메인 aihuman.ai.kr)
- `_src/build.py` · `_src/pages.py` · `_src/guides.py` : 사이트 생성기(`python3 _src/build.py` 를 실행하면 `docs/` 를 다시 만듭니다). docs/ 를 직접 고치지 말고 원본(_src)에서 고칩니다
- `_src/brand/make_brand.py` : 대표가 준 로고(A 리본 표지 + AIHuman)로 로고 · 파비콘 만들기
- `_src/shop/render.py` : 아임웹 상품 그림 · 토큰 이용 안내 그림 · 공유 그림(og.png)
- `_src/make_demo.py` : 엔진 실측값(AH서버.gs ahDemoAll)을 첫 화면 예시 데이터로
- 엔진: AIMarker 서버(Apps Script)의 AIMarker 엔진 그대로, AIHuman 배포(버전 39, AH서버.gs 층). 교차검증 AIMarker ↔ AIHuman 8/8 · 한국휴머나이징 ↔ AIHuman 8/8 일치

운영 성균관컨설팅 · contact@skkc.co.kr
