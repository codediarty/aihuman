# -*- coding: utf-8 -*-
"""AiHuman 아임웹 상품 그림 · 토큰 이용 안내 그림 · 공유 그림(og.png) 만들기
python3 _src/shop/render.py
  -> _src/shop/out/ah-<id>-1x1.jpg (1200x1200), ah-tokens-guide.png (1080x1350)
  -> docs/assets/product/ 에도 복사(사이트 Product 구조화 데이터 · 아임웹 상세 그림에서 씀), docs/assets/img/og.png(1200x630)
형제 사이트 상품 그림의 짜임(로고 · 토큰 카드 · 장점 세 칸 · 실측 예시)을 바탕으로 AiHuman 색(남색 · 파랑 · 하늘)과 궤도선으로.
정가 표시 없이(형제 사이트 방침). 전후 AI 작성률은 _src/demo.json(AiHuman 엔진 실측값) 논문 예시 그대로.
글꼴: _src/shop/pretendard.css(저장소에 올리지 않음, PretendardVariable.woff2 를 같은 폴더에)"""
import asyncio, json, os, shutil
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
ROOT = os.path.dirname(SRC)
OUT = os.path.join(HERE, "out")
PROD = os.path.join(ROOT, "docs", "assets", "product")
IMG = os.path.join(ROOT, "docs", "assets", "img")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PROD, exist_ok=True)
FONT = "file://" + os.path.join(HERE, "pretendard.css")
LOGO = "file://" + os.path.join(SRC, "brand", "logo-cut.png")
LOGO_W = "file://" + os.path.join(SRC, "brand", "logo-full-w.png")
MARK = "file://" + os.path.join(SRC, "brand", "logo-mark.png")

DEMO = json.load(open(os.path.join(SRC, "demo.json"), encoding="utf-8"))
T = DEMO["samples"][0]
B_RATE, A_RATE, T_LABEL = T["before"]["rate"], T["after"]["rate"], T["label"]

PACKS = [
    {"id": "lt", "name": "라이트", "tok": "100", "price": "9,900원", "per": "토큰당 99원", "save": "", "badge": "", "fit": "자기소개서 · 짧은 과제", "pg": "레포트 약 10페이지"},
    {"id": "pl", "name": "플러스", "tok": "350", "price": "19,900원", "per": "토큰당 약 57원", "save": "", "badge": "", "fit": "레포트 · 과제 여러 편", "pg": "레포트 약 35페이지"},
    {"id": "pr", "name": "프로", "tok": "1,000", "price": "39,900원", "per": "토큰당 약 40원", "save": "플러스 대비 토큰당 약 30% 절약", "badge": "BEST 추천", "fit": "논문 · 학위논문", "pg": "논문 약 100페이지"},
    {"id": "mx", "name": "맥스", "tok": "2,000", "price": "69,900원", "per": "토큰당 약 34원", "save": "플러스 대비 토큰당 약 40% 절약", "badge": "최고 혜택", "fit": "논문 전체 · 여러 편", "pg": "논문 약 250페이지"},
]

CHECK = ('<svg viewBox="0 0 24 24" width="30" height="30" fill="none"><circle cx="12" cy="12" r="11" fill="#eaf2ff"/>'
         '<path d="m7.5 12.3 3 3 6-6.3" stroke="#0b63f6" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
ORBIT = ('<svg class="orb" viewBox="0 0 1000 700" fill="none"><defs><linearGradient id="g1" x1="0" x2="1"><stop offset="0" stop-color="#1ca6fe" stop-opacity="0"/>'
         '<stop offset=".5" stop-color="#64d2ff" stop-opacity=".8"/><stop offset="1" stop-color="#0b63f6" stop-opacity="0"/></linearGradient>'
         '<radialGradient id="g3"><stop offset="0" stop-color="#fff"/><stop offset=".4" stop-color="#9fe2ff" stop-opacity=".9"/><stop offset="1" stop-color="#1ca6fe" stop-opacity="0"/></radialGradient></defs>'
         '<ellipse cx="500" cy="350" rx="470" ry="150" stroke="url(#g1)" stroke-width="2.4" transform="rotate(-16 500 350)"/>'
         '<ellipse cx="500" cy="350" rx="380" ry="230" stroke="url(#g1)" stroke-width="1.3" opacity=".6" transform="rotate(22 500 350)"/>'
         '<circle cx="770" cy="214" r="30" fill="url(#g3)"/></svg>')

BASE = ("<!doctype html><html><head><meta charset='utf-8'><link rel='stylesheet' href='%s'><style>"
        "*{box-sizing:border-box;margin:0;padding:0}html,body{font-family:'Pretendard Variable',Pretendard,sans-serif;-webkit-font-smoothing:antialiased;letter-spacing:-.02em;color:#0a1430;word-break:keep-all}"
        "%%s</style></head><body>%%s</body></html>") % FONT

THUMB_CSS = """
body{width:1200px;height:1200px;position:relative;overflow:hidden;background:radial-gradient(700px 420px at 100% 0%,rgba(28,166,254,.10),transparent 70%),linear-gradient(180deg,#ffffff 0%,#f1f5fc 100%)}
.lg{position:absolute;left:92px;top:74px;height:98px}
.card{position:absolute;left:92px;top:212px;width:1016px;height:600px;border-radius:48px;overflow:hidden;color:#fff;
 background:radial-gradient(560px 380px at 100% 0%,rgba(28,166,254,.55),transparent 70%),radial-gradient(520px 360px at 0% 110%,rgba(11,99,246,.55),transparent 64%),linear-gradient(155deg,#00113a 0%,#03215f 58%,#00113a 100%);
 box-shadow:0 44px 80px -34px rgba(0,17,58,.65)}
.card:before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:56px 56px}
.orb{position:absolute;right:-170px;top:-60px;width:900px;opacity:.85}
.km{position:absolute;right:-30px;bottom:-40px;height:380px;opacity:.16;filter:brightness(1.6)}
.hdr{position:absolute;left:58px;top:54px;display:flex;align-items:center;gap:14px;font-size:30px;font-weight:720;color:#cfe3ff;z-index:2}
.badge{position:absolute;right:56px;top:46px;height:56px;padding:0 26px;border-radius:28px;display:flex;align-items:center;font-size:27px;font-weight:860;z-index:2}
.badge.best{background:linear-gradient(135deg,#7fdcff,#3ea6ff);color:#00113a}
.badge.top{background:#fff;color:#00113a}
.pills{position:absolute;left:56px;top:128px;display:flex;gap:14px;z-index:2}
.pill{height:58px;padding:0 26px;border-radius:29px;display:flex;align-items:center;font-size:29px;font-weight:860}
.pill.n{background:linear-gradient(135deg,#0a3fd1,#0b63f6 50%,#1ca6fe);color:#fff;box-shadow:0 10px 24px -10px rgba(28,166,254,.9)}
.pill.o{border:2px solid rgba(255,255,255,.36);color:#fff;font-weight:720}
.big{position:absolute;left:48px;top:206px;display:flex;align-items:flex-end;z-index:2}
.big b{font-size:@BIG@px;font-weight:880;letter-spacing:-.06em;line-height:.8;background:linear-gradient(180deg,#ffffff 30%,#bfe6ff 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 18px 40px rgba(0,0,0,.35))}
.big span{font-size:60px;font-weight:860;margin:0 0 6px 16px}
.fit{position:absolute;left:58px;bottom:124px;font-size:27px;font-weight:650;color:rgba(255,255,255,.88);z-index:2}
.save{position:absolute;left:56px;bottom:50px;height:54px;padding:0 20px;border-radius:12px;border:2px solid rgba(127,220,255,.75);background:rgba(127,220,255,.12);color:#9fe2ff;font-size:25px;font-weight:820;display:flex;align-items:center;z-index:2}
.note{position:absolute;left:58px;bottom:58px;font-size:25px;font-weight:650;color:#9fd2ff;z-index:2}
.price{position:absolute;right:56px;bottom:44px;text-align:right;z-index:2}
.price b{display:block;font-size:78px;font-weight:880;letter-spacing:-.04em;line-height:1}
.price small{display:block;font-size:25px;font-weight:650;color:rgba(255,255,255,.78);margin-top:10px}
.feat{position:absolute;left:92px;right:92px;top:852px;display:grid;grid-template-columns:.82fr 1.36fr 1.12fr;gap:16px}
.feat div{display:flex;align-items:center;gap:10px;height:96px;padding:0 18px;border-radius:22px;background:#fff;border:1.5px solid #e2e7f0;font-size:24px;letter-spacing:-.03em;white-space:nowrap;font-weight:760;color:#0a1430}
.proof{position:absolute;left:92px;right:92px;bottom:76px;height:120px;border-radius:24px;background:#fff;border:1.5px solid #e2e7f0;display:flex;align-items:center;gap:26px;padding:0 34px}
.proof .k{font-size:24px;font-weight:800;color:#69748f;letter-spacing:-.01em}
.proof .v{display:flex;align-items:baseline;gap:14px;font-weight:880;letter-spacing:-.04em}
.proof .v s{font-size:50px;color:#e5154f;text-decoration-thickness:4px}
.proof .v i{font-style:normal;font-size:38px;color:#98a2b3}
.proof .v b{font-size:62px;color:#0b8f63}
.proof .t{margin-left:auto;text-align:right;font-size:23px;font-weight:650;color:#39445f;line-height:1.45}
"""


def thumb_html(p):
    badge = ('<div class="badge best">%s</div>' % p["badge"]) if p["badge"] == "BEST 추천" else (('<div class="badge top">%s</div>' % p["badge"]) if p["badge"] else "")
    low = ('<div class="save">%s</div>' % p["save"]) if p["save"] else '<div class="note">AI 작성률 검사 · AI 휴머나이징 서비스</div>'
    big = 250 if len(p["tok"]) <= 3 else 205
    css = THUMB_CSS.replace("@BIG@", str(big))
    body = ('<img class="lg" src="%s" alt="">'
            '<div class="card">%s<img class="km" src="%s" alt=""><div class="hdr">AI 작성률 낮추기 · AI 휴머나이징</div>%s'
            '<div class="pills"><span class="pill n">%s</span><span class="pill o">토큰 충전</span></div>'
            '<div class="big"><b>%s</b><span>토큰</span></div><div class="fit">%s · %s</div>%s'
            '<div class="price"><b>%s</b><small>%s · 부가세 포함</small></div></div>'
            '<div class="feat"><div>%s월 구독 없음</div><div>%s쓴 만큼 차감 · 기한 무제한</div><div>%s결제 즉시 코드 발송</div></div>'
            '<div class="proof"><span class="k">실측 예시</span><span class="v"><s>%d%%</s><i>→</i><b>%d%%</b></span><span class="t">%s · 한 번의 휴머나이징<br>실제 엔진으로 잰 값 · 글마다 다릅니다</span></div>') % (
        LOGO, ORBIT, MARK, badge, p["name"], p["tok"], p["fit"], p["pg"], low, p["price"], p["per"], CHECK, CHECK, CHECK, B_RATE, A_RATE, T_LABEL)
    return BASE % (css, body)


GUIDE_CSS = """
body{width:1080px;height:1350px;position:relative;overflow:hidden;background:radial-gradient(640px 380px at 100% 0%,rgba(28,166,254,.12),transparent 70%),linear-gradient(180deg,#ffffff,#f1f5fc)}
.lg{position:absolute;left:72px;top:62px;height:82px}
h1{position:absolute;left:72px;top:184px;font-size:56px;line-height:1.22;font-weight:860;letter-spacing:-.045em;color:#00113a}
h1 em{font-style:normal;background:linear-gradient(135deg,#0a3fd1,#0b63f6 50%,#1ca6fe);-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{position:absolute;left:74px;top:336px;font-size:26px;color:#39445f;font-weight:560;line-height:1.6}
.steps{position:absolute;left:72px;right:72px;top:404px;display:grid;gap:16px}
.st{display:flex;gap:22px;align-items:flex-start;padding:24px 28px;border-radius:24px;background:#fff;border:1.5px solid #e2e7f0}
.st i{flex:none;width:58px;height:58px;border-radius:50%;background:linear-gradient(135deg,#0a3fd1,#0b63f6 50%,#1ca6fe);color:#fff;font-style:normal;font-weight:860;font-size:28px;display:grid;place-items:center}
.st b{display:block;font-size:31px;font-weight:860;letter-spacing:-.03em;color:#0a1430}
.st p{margin-top:4px;font-size:22.5px;line-height:1.5;color:#39445f}
.cost{position:absolute;left:72px;right:72px;bottom:56px;padding:30px 34px;border-radius:26px;color:#fff;overflow:hidden;background:radial-gradient(420px 260px at 100% 0%,rgba(28,166,254,.6),transparent 70%),linear-gradient(150deg,#00113a,#03215f)}
.cost h2{font-size:30px;font-weight:860;letter-spacing:-.03em}
.cost ul{list-style:none;margin-top:14px;display:grid;grid-template-columns:1fr 1fr;gap:10px 26px;font-size:24px;color:#d6e4fb}
.cost b{color:#fff}
"""


def guide_html():
    steps = [("결제", "토큰을 고르고 성균관컨설팅 결제 페이지에서 결제합니다. 회원가입 없이 카드 · 간편결제로 끝납니다."),
             ("메일로 코드", "결제가 확인되면 보통 1분 안에 주문서의 이메일로 16자리 토큰 코드가 갑니다. 보내는 이름은 'AiHuman'입니다."),
             ("바로 이어서", "메일의 '바로 이어서 하기'를 누르면 코드가 들어간 채로 aihuman.ai.kr 이 열리고, 하던 글을 그대로 이어 갑니다."),
             ("쓴 만큼만", "글을 넣고 검사 · 휴머나이징을 누르면 글자 수만큼만 빠집니다. 남은 토큰은 기한 없이 그대로입니다.")]
    s = "".join('<div class="st"><i>%d</i><div><b>%s</b><p>%s</p></div></div>' % (i + 1, a, b) for i, (a, b) in enumerate(steps))
    body = ('<img class="lg" src="%s" alt=""><h1>결제하고 <em>1분</em>,<br>메일로 받은 코드로 바로</h1><p class="sub">AI 작성률 검사 · AI 휴머나이징 서비스에 쓰는 토큰 이용 안내</p><div class="steps">%s</div>'
            '<div class="cost"><h2>토큰은 이렇게 빠집니다</h2><ul><li>AI 작성률 검사 <b>무료</b></li><li>상세 진단 <b>1,000자 2토큰</b></li><li>휴머나이징 <b>1,000자 4토큰</b></li><li>1토큰 <b>100원</b> · 구독 없음</li></ul></div>') % (LOGO, s)
    return BASE % (GUIDE_CSS, body)


OG_CSS = """
body{width:1200px;height:630px;position:relative;overflow:hidden;color:#fff;
 background:radial-gradient(620px 420px at 92% 0%,rgba(28,166,254,.42),transparent 64%),radial-gradient(560px 420px at 0% 0%,rgba(11,99,246,.45),transparent 62%),linear-gradient(165deg,#00113a 0%,#03215f 58%,#00143f 100%)}
body:before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);background-size:48px 48px}
.orb{position:absolute;right:-260px;top:-150px;width:1000px;opacity:.9}
.lg{position:absolute;left:72px;top:58px;height:96px}
.kw{position:absolute;left:76px;top:190px;font-size:26px;font-weight:760;color:#a9c7f5;letter-spacing:-.01em}
h1{position:absolute;left:72px;top:232px;font-size:70px;line-height:1.14;font-weight:860;letter-spacing:-.05em}
h1 em{font-style:normal;background:linear-gradient(92deg,#7fdcff,#3ea6ff 55%,#7c9dff);-webkit-background-clip:text;background-clip:text;color:transparent}
.chips{position:absolute;left:76px;bottom:62px;display:flex;gap:12px}
.chips span{height:48px;padding:0 20px;border-radius:24px;display:flex;align-items:center;font-size:21px;font-weight:720;border:1.5px solid rgba(255,255,255,.26);color:#e2ecff;background:rgba(255,255,255,.06)}
.chips span:first-child{background:linear-gradient(135deg,#0a3fd1,#0b63f6 50%,#1ca6fe);border-color:transparent;color:#fff}
.proof{position:absolute;right:72px;bottom:58px;width:330px;padding:22px 26px;border-radius:24px;background:#fff;color:#0a1430;box-shadow:0 30px 60px -20px rgba(0,0,0,.55)}
.proof small{display:block;font-size:17px;font-weight:760;color:#69748f}
.proof .v{display:flex;align-items:baseline;gap:12px;margin-top:6px;font-weight:880;letter-spacing:-.04em}
.proof .v s{font-size:40px;color:#e5154f;text-decoration-thickness:3px}
.proof .v i{font-style:normal;font-size:30px;color:#98a2b3}
.proof .v b{font-size:56px;color:#0b8f63}
.proof p{font-size:16px;color:#69748f;margin-top:4px}
"""


def og_html():
    body = ('%s<img class="lg" src="%s" alt=""><p class="kw">AI 휴머나이징 · AI 작성률 낮추기 · 한국어 AI 휴머나이저</p><h1>AI가 쓴 글을<br><em>사람의 문장</em>으로.</h1>'
            '<div class="chips"><span>AI 작성률 무료 검사</span><span>한글 · 워드 · PDF</span><span>aihuman.ai.kr</span></div>'
            '<div class="proof"><small>%s 예시 · 한 번의 휴머나이징</small><div class="v"><s>%d%%</s><i>→</i><b>%d%%</b></div><p>실제 엔진으로 잰 값 · 글마다 다릅니다</p></div>') % (ORBIT, LOGO_W, T_LABEL, B_RATE, A_RATE)
    return BASE % (OG_CSS, body)


async def shot(b, html, w, h, fp, jpeg=False):
    path = os.path.join(HERE, "_t_%d.html" % abs(hash(fp)))
    open(path, "w", encoding="utf-8").write(html)
    pg = await b.new_page(viewport={"width": w, "height": h})
    await pg.goto("file://" + path); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(300)
    if jpeg:
        await pg.screenshot(path=fp, type="jpeg", quality=90)
    else:
        await pg.screenshot(path=fp)
    await pg.close(); os.remove(path)


async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--allow-file-access-from-files"])
        for p in PACKS:
            fp = os.path.join(OUT, "ah-%s-1x1.jpg" % p["id"])
            await shot(b, thumb_html(p), 1200, 1200, fp, jpeg=True)
            shutil.copy(fp, os.path.join(PROD, os.path.basename(fp)))
        fp = os.path.join(OUT, "ah-tokens-guide.png")
        await shot(b, guide_html(), 1080, 1350, fp)
        shutil.copy(fp, os.path.join(PROD, os.path.basename(fp)))
        await shot(b, og_html(), 1200, 630, os.path.join(IMG, "og.png"))
        await b.close()
    print("ok", sorted(os.listdir(OUT)))

asyncio.run(main())
