# -*- coding: utf-8 -*-
"""AiHuman(aihuman.ai.kr) 정적 사이트 만들기

    python3 _src/build.py

docs/ 에 페이지 · sitemap.xml · robots.txt · llms.txt · llms-full.txt · rss.xml 을 씁니다(GitHub Pages 가 docs/ 를 그대로 서빙).
검사 · 휴머나이징 엔진은 AIMarker 서버(Apps Script 'AIMarker 서버' 프로젝트)의 같은 엔진, AiHuman 배포(버전 39, AH서버.gs 층)를 씁니다.
대표(2026.11.22 12:26): 'aihuman.ai.kr 도메인 구매했으니 휴머나이징 웹사이트 더 잘 만들어줘. AIMarker와 엔진 동일하게 하고 아임웹 상품 구성 및
웹사이트 휴머나이징 레이아웃도 참고로 해서 제작하되 조금 더 개선되게 해줘 디자인말이야(엔진 성능과 기능은 동일하게 해야됨). 노출도 잘되어야 하니까
아래 키워드 참고해서 적용해줘 세팅 모두 다 해줘'. 교차검증(AIMarker ↔ AiHuman 8/8 · 한국휴머나이징 ↔ AiHuman 8/8 일치)
"""
import datetime
import difflib
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "docs")
sys.path.insert(0, HERE)
from icons import ICONS  # noqa: E402
import pages as P  # noqa: E402

# ---------------- 설정 ----------------
SITE = "https://aihuman.ai.kr"
HOST = "aihuman.ai.kr"
BRAND = "AiHuman"
BRAND_KO = "AI휴먼"
VER = "20261122a"
TODAY = "2026-11-22"
# AiHuman 배포(AIMarker 서버 프로젝트 버전 39, 엔진은 AIMarker 와 같음 · 2026.11.22 12:48)
API = "https://script.google.com/macros/s/AKfycby_nRD2dpVLYztnfUlaiQfS3zOXZwfBMVewmZgecSqnONA3vVmiiIyQuZ32Ae5hcOntyg/exec"
SHOP = "https://skkc.co.kr/shop_view?idx=%s&kaiec_buy=1"
# 성균관컨설팅(아임웹) AiHuman 전용 상품 번호. 서버는 스크립트 속성 AH_IDX 로 같은 번호를 ah1~ah4 로 봄
SHOP_IDX = {}
NAVER_VERIFY = ""
GOOGLE_VERIFY = ""
BING_VERIFY = ""
INDEXNOW_KEY = "7c3e9a51d2b84f06a1e5c8d94b2f6a07"
GOOGLE_FILES = []
BIZ = {"name": "성균관컨설팅", "ceo": "이채연", "no": "272-32-01885", "ecom": "제2026-경기송탄-0622",
       "addr": "경기도 수원시 장안구 서부로 2066 성균관대학교 브릿지팩토리(연구실)", "mail": "contact@skkc.co.kr"}
# 가격 · 토큰은 AIMarker 개인 토큰 · 형제 사이트와 같음(서버 ah1~ah4). 요금 카드는 정가 없이 간단하게(형제 사이트 방침과 같게)
PACKS = [
    {"id": "lt", "name": "라이트", "tok": 100, "price": 9900, "per": "99원", "who": "자기소개서 · 짧은 과제", "chars": "약 25,000자", "pg": "약 10페이지", "sub": "AI 작성률 낮추기, 미니멀하게", "doc": "레포트"},
    {"id": "pl", "name": "플러스", "tok": 350, "price": 19900, "per": "약 57원", "who": "레포트 · 과제 여러 편", "chars": "약 87,500자", "pg": "약 35페이지", "sub": "AI 작성률 낮추기, 합리적으로", "doc": "레포트"},
    {"id": "pr", "name": "프로", "tok": 1000, "price": 39900, "per": "약 40원", "who": "논문 · 학위논문", "chars": "약 250,000자", "pg": "약 100페이지", "best": "BEST 추천", "save": "플러스보다 토큰당 약 30% 절약", "sub": "AI 작성률 낮추기, 더 효과적으로", "doc": "논문"},
    {"id": "mx", "name": "맥스", "tok": 2000, "price": 69900, "per": "약 35원", "who": "논문 전체 · 여러 편", "chars": "약 500,000자", "pg": "약 250페이지", "top": "최고 혜택", "save": "플러스보다 토큰당 약 39% 절약", "sub": "반복 변환으로 AI 작성률 극한까지 낮추기", "doc": "논문"},
]
COST = {"check": (0, 0), "hum": (4, 2)}   # 1,000자당 토큰 · 최소 토큰(서버와 같게: AI 작성률 검사 무료, 휴머나이징 1,000자 4토큰)


def esc(s):
    return html.escape(str(s), quote=True)


def ico(name, cls="ico"):
    return '<svg class="%s" viewBox="0 0 24 24" aria-hidden="true">%s</svg>' % (cls, ICONS.get(name, ""))


def won(n):
    return "{:,}원".format(n)


def shop(pid):
    ix = SHOP_IDX.get(pid) or ""
    return SHOP % ix if ix else ""


# 로고: 대표가 준 그림(A 리본 표지 + AiHuman, 2026.11.22) 그대로. 어두운 바닥글은 글자만 흰색 판(logo-w.png)
LOGO = '<a class="logo" href="/" aria-label="%s(%s) 홈"><img src="/assets/img/logo.png?v=%s" width="542" height="120" alt="%s"></a>' % (BRAND, BRAND_KO, VER, BRAND)
LOGO_W = '<a class="logo" href="/" aria-label="%s(%s) 홈"><img src="/assets/img/logo-w.png?v=%s" width="542" height="120" alt="%s"></a>' % (BRAND, BRAND_KO, VER, BRAND)

# 메뉴: 형제 사이트에서 대표가 정한 대로 'AI 휴머나이저(AI 작성률 낮추기)' 하나가 첫 칸(헷갈리지 않고 결제로). 검사기 이름은 메뉴에 쓰지 않음
NAV = [("", "AI 휴머나이저<small>(AI 작성률 낮추기)</small>"), ("pricing/", "요금"), ("guide/", "가이드"), ("faq/", "자주 묻는 질문")]


def header(path):
    nav = "".join('<a href="/%s"%s>%s</a>' % (p, ' aria-current="page"' if path == p else "", t) for p, t in NAV)
    mnav = "".join('<a href="/%s">%s</a>' % (p, t) for p, t in NAV)
    top = ('<div class="topbar"><div class="wrap"><span class="dot" aria-hidden="true"></span><span><b>AI 작성률 검사 무료</b> · 가입 없이 20만 자<span class="hide-s"> · 한글 · 워드 · PDF 그대로</span></span>'
           '<a href="/#tool" data-tool>지금 검사하기 →</a></div></div>')
    return (top + '<header class="hd" id="hd"><div class="wrap hd-in">%s<nav class="nav" aria-label="주요 메뉴">%s</nav>'
            '<div class="hd-r"><a class="btn btn-g btn-s" href="/pricing/">토큰 충전</a><a class="btn btn-p btn-s" href="/#tool" data-tool>%s<span class="hl">무료 AI 작성률 검사</span><span class="hs">무료 검사</span></a>'
            '<button class="menu-btn" id="menuBtn" type="button" aria-label="메뉴 열기" aria-expanded="false" aria-controls="mnav">%s</button></div></div></header>'
            '<nav class="mnav" id="mnav" aria-label="모바일 메뉴">%s<a href="/#tool" data-tool>무료 AI 작성률 검사</a><a href="/#example">실제 측정 결과</a><a href="/about/">회사 소개</a></nav>') % (LOGO, nav, ico("search"), ico("menu"), mnav)


def guide_by(slug):
    return next(g for g in P.GUIDES if g["slug"] == slug)


# 바닥글 검색어 링크(검색어 = 그 글의 주제, 첫 화면 방침대로 검사기 이름 글은 넣지 않음)
FT_KW = [("/", "AI 휴머나이징"), ("/guide/ai-rate-lower/", "AI 작성률 낮추기"), ("/", "AI 휴머나이저"), ("/guide/ai-text-humanize/", "AI 글 인간화"),
         ("/guide/korean-humanizer/", "한국어 휴머나이저"), ("/guide/ai-sentence-converter/", "AI 문장 변환기"), ("/guide/ai-detector/", "AI 탐지기"), ("/pricing/", "AI 휴머나이징 가격")]


def footer():
    gl = [("/guide/", "가이드 전체")] + [("/guide/%s/" % s, guide_by(s)["kw"].split(" · ")[0]) for s in ["ai-rate-lower", "thesis-ai-rate", "resume-ai-rate", "humanizer-compare", "free-humanizing"]]
    cols = [
        ("서비스", [("/#tool", "무료 AI 작성률 검사"), ("/#example", "실제 측정 결과"), ("/pricing/", "요금 · 토큰 충전"), ("/faq/", "자주 묻는 질문")]),
        ("가이드", gl),
        ("회사 · 정책", [("/about/", "회사 소개"), ("/terms/", "이용약관"), ("/privacy/", "개인정보처리방침"), ("mailto:" + BIZ["mail"], "문의 " + BIZ["mail"])]),
    ]
    c = "".join('<div><h4>%s</h4><ul>%s</ul></div>' % (h, "".join('<li><a href="%s">%s</a></li>' % (u, t) for u, t in L)) for h, L in cols)
    kw = "".join('<a href="%s"><span>%s</span></a>' % (u, t) for u, t in FT_KW)
    return ('<footer class="ft"><div class="wrap"><div class="ft-top"><div>%s<p>AI휴먼 | AI 휴머나이징 전문 서비스.<br>AI 작성률을 무료로 검사하고, 걸리는 문장만 사람 문장으로 바꿉니다.</p><div class="ft-kw">%s</div></div>%s</div>'
            '<div class="ft-biz"><b>운영</b> %s · 대표 %s · 사업자등록번호 %s · 통신판매업 신고 %s<br>%s · %s<br>'
            '다른 AI 탐지 서비스의 이름은 각 권리자의 상표이며, %s은 해당 서비스와 제휴 관계가 없습니다. AI 작성률과 판정은 %s 판정 기준으로 계산한 값입니다.<br>© 2026 %s(%s). All rights reserved.</div></div></footer>'
            '<div class="mcta" id="mcta"><a class="btn btn-p" href="/#tool" data-tool>%s무료 검사</a><a class="btn btn-g" href="/pricing/">요금 보기</a></div>') % (
        LOGO_W, kw, c, BIZ["name"], BIZ["ceo"], BIZ["no"], BIZ["ecom"], BIZ["addr"], BIZ["mail"], BRAND, BRAND, BRAND, BRAND_KO, ico("search"))


# ---------------- 구조화 데이터 ----------------
ALT = [BRAND_KO, "에이아이휴먼", "AI Human", "AiHuman AI 휴머나이저", HOST]
ORG = {"@type": "Organization", "@id": SITE + "/#org", "name": BRAND, "alternateName": ALT, "url": SITE + "/",
       "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/logo-512.png", "width": 512, "height": 512},
       "slogan": "AI휴먼 | AI 휴머나이징 전문 서비스",
       "parentOrganization": {"@type": "Organization", "name": BIZ["name"], "taxID": BIZ["no"]},
       "contactPoint": {"@type": "ContactPoint", "contactType": "customer support", "email": BIZ["mail"], "availableLanguage": ["ko"]},
       "address": {"@type": "PostalAddress", "streetAddress": "서부로 2066 성균관대학교 브릿지팩토리", "addressLocality": "수원시 장안구", "addressRegion": "경기도", "postalCode": "16419", "addressCountry": "KR"}}
WEBSITE = {"@type": "WebSite", "@id": SITE + "/#website", "name": BRAND, "alternateName": ALT, "url": SITE + "/", "inLanguage": "ko-KR", "publisher": {"@id": SITE + "/#org"}}
APP = {"@type": "WebApplication", "@id": SITE + "/#app", "name": BRAND + " AI 휴머나이저", "alternateName": [BRAND_KO + " AI 휴머나이징", "AI 작성률 낮추기 도구"], "url": SITE + "/",
       "applicationCategory": "UtilitiesApplication", "operatingSystem": "Web", "inLanguage": "ko-KR",
       "description": "한국어 AI 작성률 검사와 AI 휴머나이징(AI 글 인간화). AI 탐지기에 걸리는 문장만 골라 사람 문장으로 바꾸고, 같은 기준으로 AI 작성률을 다시 잽니다.",
       "featureList": ["AI 작성률 무료 검사(20만 자)", "문장 단위 AI 검출 표시", "AI 휴머나이징(한국어 전용 엔진, 생성 AI 사용 안 함)", "한글 HWP · HWPX · 워드 DOCX · PDF 파일 지원", "말투 자동 맞춤", "숫자 · 이름 · 인용 보존"],
       "offers": {"@type": "AggregateOffer", "priceCurrency": "KRW", "lowPrice": "0", "highPrice": "69900", "offerCount": "5"}, "publisher": {"@id": SITE + "/#org"}}


def ld_faq(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in faq]}


def ld_crumbs(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + "/" + u} for i, (n, u) in enumerate([("홈", "")] + trail)]}


def ld_howto(name, steps):
    return {"@type": "HowTo", "name": name, "inLanguage": "ko-KR", "totalTime": "PT2M", "step": [{"@type": "HowToStep", "position": i + 1, "name": a, "text": b} for i, (a, b) in enumerate(steps)]}


def ld_offers():
    return {"@type": "Product", "@id": SITE + "/pricing/#product", "name": BRAND + " AI 휴머나이징 토큰", "brand": {"@type": "Brand", "name": BRAND},
            "description": "AI 작성률 검사와 AI 휴머나이징에 쓰는 토큰. 월 구독 없이 한 번 충전하고, 남은 토큰은 5년 동안 사라지지 않습니다.",
            "image": [SITE + "/assets/product/ah-pr-1x1.jpg", SITE + "/assets/img/og.png"], "category": "디지털콘텐츠 이용권",
            "offers": [{"@type": "Offer", "name": "%s %s토큰" % (p["name"], "{:,}".format(p["tok"])), "price": str(p["price"]), "priceCurrency": "KRW", "availability": "https://schema.org/InStock",
                        "url": (shop(p["id"]).replace("&kaiec_buy=1", "") if shop(p["id"]) else (SITE + "/pricing/")), "seller": {"@type": "Organization", "name": BIZ["name"]}} for p in PACKS]}


# ---------------- 페이지 틀 ----------------
PAGES = []   # (path, title, desc, lastmod, priority)


def page(path, title, desc, body, *, ld=None, tool=False, og=None, ptype="website", noindex=False, priority="0.7", lastmod=TODAY, extra_head="", keywords=""):
    url = SITE + "/" + path
    ogimg = og or (SITE + "/assets/img/og.png?v=" + VER)
    graph = [ORG, WEBSITE] + (ld or [])
    head = ['<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">',
            '<title>%s</title><meta name="description" content="%s">' % (esc(title), esc(desc)),
            ('<meta name="keywords" content="%s">' % esc(keywords)) if keywords else "",
            '<link rel="canonical" href="%s">' % url,
            '<link rel="alternate" hreflang="ko" href="%s"><link rel="alternate" hreflang="x-default" href="%s">' % (url, url),
            '<meta name="robots" content="%s">' % ("noindex,follow" if noindex else "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"),
            '<meta property="og:type" content="%s"><meta property="og:site_name" content="%s(%s)"><meta property="og:locale" content="ko_KR">' % (ptype, BRAND, BRAND_KO),
            '<meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s">' % (esc(title), esc(desc), url),
            '<meta property="og:image" content="%s"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="%s">' % (ogimg, esc(BRAND + " · AI 작성률 검사와 AI 휴머나이징")),
            '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s"><meta name="twitter:image" content="%s">' % (esc(title), esc(desc), ogimg),
            '<meta name="theme-color" content="#00113a"><meta name="format-detection" content="telephone=no"><meta name="author" content="%s"><meta name="application-name" content="%s">' % (BRAND, BRAND),
            ('<link rel="icon" href="/favicon.ico?v=%s" sizes="any"><link rel="icon" href="/assets/img/favicon.svg?v=%s" type="image/svg+xml"><link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png?v=%s"><link rel="manifest" href="/site.webmanifest?v=%s">' % (VER, VER, VER, VER)),
            '<link rel="alternate" type="application/rss+xml" title="%s 가이드" href="/rss.xml">' % BRAND]
    if NAVER_VERIFY:
        head.append('<meta name="naver-site-verification" content="%s">' % NAVER_VERIFY)
    if GOOGLE_VERIFY:
        head.append('<meta name="google-site-verification" content="%s">' % GOOGLE_VERIFY)
    if BING_VERIFY:
        head.append('<meta name="msvalidate.01" content="%s">' % BING_VERIFY)
    head.append('<script>document.documentElement.className+=" js";setTimeout(function(){if(!window.HZ_SITE){var a=document.querySelectorAll(".rv");for(var i=0;i<a.length;i++)a[i].className+=" in"}},3000)</script>')
    head.append('<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin><link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">')
    if tool:
        head.append('<link rel="stylesheet" href="/assets/tool.css?v=%s">' % VER)
    head.append('<link rel="stylesheet" href="/assets/ah.css?v=%s">' % VER)
    head.append(extra_head)
    head.append('<script type="application/ld+json">%s</script>' % json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")))
    head.append("</head>")
    scripts = ['<script src="/assets/site.js?v=%s" defer></script>' % VER]
    if tool:
        scripts = ['<script>window.HZ_API=%s;</script>' % json.dumps(API),
                   '<script src="/assets/products.js?v=%s" defer></script>' % VER,
                   '<script src="/assets/am.js?v=%s" defer></script>' % VER,
                   '<script src="/assets/textin.js?v=%s" defer></script>' % VER,
                   '<script src="/assets/humanize.js?v=%s" defer></script>' % VER] + scripts
    doc = "".join(head) + '<body data-root="/">' + '<a class="sr" href="#main">본문 바로가기</a>' + header(path) + '<main id="main">' + body + "</main>" + footer() + "".join(scripts) + "</body></html>"
    fp = os.path.join(OUT, path, "index.html") if path else os.path.join(OUT, "index.html")
    if path == "404.html":
        fp = os.path.join(OUT, "404.html")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(doc)
    if not noindex:
        PAGES.append((path, title, desc, lastmod, priority))


# ---------------- 검사 도구(엔진 화면, humanize.js 가 움직임) ----------------
def tool_html():
    packs = []
    for p in PACKS:
        cls = ' class="best"' if p.get("best") else (' class="top"' if p.get("top") else "")
        tag = '<i class="tg">%s</i>' % p["best"] if p.get("best") else ('<i class="tg top">%s</i>' % p["top"] if p.get("top") else "")
        sv = '<i class="hz17-sv">%s</i>' % p["save"] if p.get("save") else ""
        packs.append('<label%s><input type="radio" name="product" value="%s"%s><span>%s<b class="nm">%s</b><b class="tk">%s<small>토큰</small></b><b class="pr">%s<small>토큰당 %s</small></b>%s<small class="ds">%s · 검사와 휴머나이징 %s</small></span></label>' % (
            cls, p["id"], " checked" if p.get("best") else "", tag, p["name"], "{:,}".format(p["tok"]), won(p["price"]), p["per"], sv, p["who"], p["chars"]))
    return P.TOOL_TPL.format(ico_upload=ico("upload"), ico_search=ico("search"), ico_pen=ico("pen"), ico_lock=ico("lock"), ico_x=ico("x"), ico_spark=ico("sparkle"), ico_arrow=ico("arrow"),
                             packs="".join(packs), biz_no=BIZ["no"], mail=BIZ["mail"], brand=BRAND)


# ---------------- 예시 화면(실제 엔진 값) ----------------
DEMO = json.load(open(os.path.join(HERE, "demo.json"), encoding="utf-8"))


def tok(s):
    return re.findall(r"\S+\s*", s)


def sent_split(t):
    return [x for x in re.split(r"(?<=[.!?])\s+", t.strip()) if x]


def _chg(x, y, mode):
    """mode: anim(예시 화면, 바뀔 말에 새 말을 data-n 으로) · src(원문) · dst(다듬은 글)"""
    sx, sy = x.rstrip(), y.rstrip()
    tx, ty = x[len(sx):], y[len(sy):]
    if mode == "src":
        return ('<span class="x">%s</span>%s' % (esc(sx), esc(tx))) if sx else ""
    if mode == "dst":
        return ('<mark>%s</mark>%s' % (esc(sy), esc(ty))) if sy else ""
    return '<span class="x" data-n="%s">%s</span>%s' % (esc(sy + ty), esc(sx), esc(tx)) if (sx or sy) else ""


def _sent_ops(src, dst):
    """원문 문장마다 [(종류, 원래 말, 바뀐 말)] 목록. 휴머나이징이 문장을 잇거나 나눠도 원문 문장 경계로 자름"""
    A, B = tok(src), tok(dst)
    sid, k = [], 0
    for t in A:
        sid.append(k)
        if re.search(r"[.!?]\s*$", t):
            k += 1
    n = (sid[-1] + 1) if sid else 0
    per = [[] for _ in range(n)]
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        y = "".join(B[j1:j2])
        if i1 == i2:   # 넣기만 한 말: 앞 문장 끝에 붙임
            tgt = sid[i1 - 1] if i1 > 0 else 0
            per[tgt].append(("c", "", y))
            continue
        segs = []
        for i in range(i1, i2):
            if not segs or segs[-1][0] != sid[i]:
                segs.append([sid[i], []])
            segs[-1][1].append(A[i])
        for m, (si, toks) in enumerate(segs):
            x = "".join(toks)
            if op == "equal":
                per[si].append(("e", x, x))
            else:
                per[si].append(("c", x, y if m == 0 else ""))
    return per


def demo_samples():
    out = []
    for S in DEMO["samples"]:
        flags, scores = set(S.get("ai", [])), S.get("scores", {})
        bs, as_ = sent_split(S["src"]), sent_split(S["dst"])
        ascores = S.get("after_scores", {}) if len(bs) == len(as_) else {}
        per = _sent_ops(S["src"], S["dst"])
        anim, src, dst, nch = [], [], [], 0
        for i, ops in enumerate(per):
            n = sum(1 for o in ops if o[0] == "c")
            nch += n
            isai = i in flags
            p0, p1 = scores.get(str(i)), ascores.get(str(i))
            tag = ('<i class="demo-tag" data-p0="%s" data-p1="%s">AI 패턴</i>' % (p0, "" if p1 is None else p1)) if (isai and p0 is not None) else ""
            okt = '<i class="demo-tag ok">AI 미검출</i>' if (isai and p0 is not None and n and S["after"].get("n") == 0) else ""
            A_ = "".join(esc(o[1]) if o[0] == "e" else _chg(o[1], o[2], "anim") for o in ops)
            S_ = "".join(esc(o[1]) if o[0] == "e" else _chg(o[1], o[2], "src") for o in ops)
            D_ = "".join(esc(o[2]) if o[0] == "e" else _chg(o[1], o[2], "dst") for o in ops)
            anim.append('<span class="s%s">%s%s</span> ' % (" ai" if isai else "", A_.rstrip(), tag))
            src.append('<span class="s%s">%s%s</span> ' % (" ai" if isai else "", S_.rstrip(), tag.replace("demo-tag", "demo-tag st")))
            dst.append('<span class="s%s">%s%s</span> ' % (" hu" if n else "", D_.rstrip(), okt))
        out.append({"k": S["k"], "label": S["label"], "file": S["file"], "before": S["before"], "after": S["after"], "changes": nch,
                    "doc": '<p class="ai-blk">' + "".join(anim).strip() + "</p>",
                    "src": '<p class="ai-blk">' + "".join(src).strip() + "</p>", "dst": '<p class="hu-blk">' + "".join(dst).strip() + "</p>"})
    return out


SAMPLES = demo_samples()


def demo_json():
    return '<script type="application/json" id="hzDemoData">%s</script>' % json.dumps({"samples": SAMPLES, "measured": DEMO["measured"]}, ensure_ascii=False).replace("</", "<\\/")


def demo_card():
    S = SAMPLES
    tabs = "".join('<button type="button" role="tab" aria-selected="%s">%s</button>' % ("true" if i == 0 else "false", s["label"]) for i, s in enumerate(S))
    first = S[0]
    return ('<div class="demo" id="demo" aria-label="AI 작성률 검사와 휴머나이징 예시(실제 엔진 값)">'
            '<div class="demo-bar"><i></i><i></i><i></i><span class="fn">%s<span>%s</span></span><div class="demo-tabs" role="tablist" aria-label="예시 글 종류">%s</div></div>'
            '<div class="demo-scan" aria-hidden="true"></div>'
            '<div class="demo-meter"><div class="dm from bad"><small>휴머나이징 전 · AI 작성률</small><b>%s<small style="font-size:18px">%%</small> <em>%s</em></b><div class="dm-bar"><i style="width:%s%%"></i></div></div>'
            '<span class="dm-arr" aria-hidden="true">%s</span>'
            '<div class="dm to good wait"><small>휴머나이징 후 · AI 작성률</small><b>– <em>대기</em></b><div class="dm-bar"><i style="width:0"></i></div></div></div>'
            '<div class="demo-legend"><span class="a"><i></i>AI 패턴 검출 문장</span><span class="h"><i></i>사람 문장으로 바꾼 곳</span><span class="demo-state" aria-live="polite"></span></div>'
            '<div class="demo-doc">%s</div>'
            '<div class="demo-ft"><a class="btn btn-p btn-s demo-go" href="#tool" data-hum-go>%s<span>휴머나이징 하기</span><em>내 글 인간화</em></a>'
            '<a class="btn btn-g btn-s" href="#tool" data-tool>무료 검사</a><p class="note">%s</p></div></div>') % (
        ico("file"), esc(first["file"]), tabs, first["before"]["rate"], first["before"]["band"], first["before"]["rate"], ico("arrow"),
        first["doc"], ico("sparkle"), esc(DEMO["measured"]))


def compare_block():
    S = SAMPLES
    tabs = "".join('<button type="button" role="tab" aria-selected="%s">%s</button>' % ("true" if i == 0 else "false", s["label"]) for i, s in enumerate(S))
    return ('<div class="cmp-tabs" role="tablist" aria-label="예시 글 종류">%s</div><div class="cmp" id="cmp">'
            '<div class="cmp-col"><div class="cmp-h"><span>휴머나이징 전</span><span class="pill l bad"></span></div><div class="cmp-t l"></div></div>'
            '<div class="cmp-col"><div class="cmp-h"><span>휴머나이징 후</span><span class="pill r good"></span></div><div class="cmp-t r"></div></div></div>'
            '<div class="cmp-foot"></div><p class="center measured">%s</p>') % (tabs, esc(DEMO["measured"]))


def faq_html(faq):
    return '<div class="faq">' + "".join('<details><summary>%s</summary><div class="a"><p>%s</p></div></details>' % (esc(q), a) for q, a in faq) + "</div>"


REP_LINE = "반복 변환할수록 AI 작성률은 계속 낮아집니다. 여러 번 변환하여 AI 작성 흔적을 극한까지 줄여보세요."   # 형제 사이트 요금 칸 아래 반복 변환 안내와 같게


def pricing_cards(cta_text="충전하기"):
    out = []
    for p in PACKS:
        cls = "pk" + (" best" if p.get("best") else (" top" if p.get("top") else ""))
        tag = '<span class="tg">%s</span>' % p["best"] if p.get("best") else ('<span class="tg top">%s</span>' % p["top"] if p.get("top") else "")
        link, bcls, label = shop(p["id"]), ("btn-p" if p.get("best") else "btn-g"), "%s %s" % (p["name"], cta_text)
        btn = ('<a class="btn %s" href="%s" target="_blank" rel="noopener" data-pack="%s">%s</a>' % (bcls, esc(link), p["id"], label)) if link else \
              ('<a class="btn %s" href="/#buy-%s" data-buy-pack="%s">%s</a>' % (bcls, p["id"], p["id"], label))
        sv = ('<p class="sv2">%s</p>' % p["save"]) if p.get("save") else ""
        out.append('<div class="%s rv">%s<h3>%s</h3><p class="who">%s</p><p class="tk2"><b>%s</b>토큰</p><p class="pr2"><b>%s</b><span>토큰당 %s</span></p>%s'
                   '<p class="use">%s 검사와 휴머나이징 서비스 <b>%s</b></p>%s</div>' % (
                       cls, tag, p["name"], p["sub"], "{:,}".format(p["tok"]), won(p["price"]), p["per"], sv, p["doc"], p["pg"], btn))
    return '<div class="price">' + "".join(out) + "</div>" + '<p class="price-rep">%s</p>' % REP_LINE


def calc_block():
    docs = [("자소서 1문항", 1500), ("레포트", 5000), ("논문 한 장", 15000), ("학위논문 본문", 80000)]
    btns = "".join('<button type="button" data-chars="%d" aria-pressed="%s">%s</button>' % (n, "true" if i == 1 else "false", t) for i, (t, n) in enumerate(docs))
    data = json.dumps({"cost": COST, "packs": [{"id": p["id"], "name": p["name"], "tok": p["tok"], "price": p["price"], "link": shop(p["id"])} for p in PACKS]}, ensure_ascii=False)
    return ('<div class="calc rv" id="calc"><div class="calc-in"><h3>내 글에는 토큰이 얼마나 들까요?</h3><p>글 종류를 고르거나 글자 수를 맞춰 보세요. 서버가 실제로 빼는 값과 같은 셈입니다.</p>'
            '<div class="calc-docs" role="group" aria-label="글 종류">%s</div>'
            '<div class="calc-row"><label class="sr" for="calcN">글자 수</label><input type="range" id="calcN" min="500" max="200000" step="500" value="5000"><output id="calcO" for="calcN">5,000자</output></div>'
            '<div class="calc-opt"><label><input type="checkbox" id="calcC" checked>AI 작성률 검사</label><label><input type="checkbox" id="calcH" checked>AI 휴머나이징</label><label><input type="checkbox" id="calcT">한 번 더 다듬기</label></div></div>'
            '<div class="calc-out" aria-live="polite"><dl><div><dt>AI 작성률 검사</dt><dd id="calcCc">무료</dd></div><div><dt>AI 휴머나이징</dt><dd id="calcHc">20토큰</dd></div>'
            '<div class="sum"><dt>합계</dt><dd id="calcS">20토큰</dd></div></dl><p class="calc-rec" id="calcR"></p><a class="btn btn-p" id="calcB" href="/pricing/">충전하기</a></div>'
            '<script type="application/json" id="calcData">%s</script></div>') % (btns, data)


def cta_band(h="제출 전 30초, AI 작성률부터 확인하세요", p="가입도 카드 등록도 없이 무료로 검사합니다. 걸리는 문장이 있을 때만 휴머나이징하면 됩니다."):
    return ('<section class="sec-s cta-sec"><div class="wrap"><div class="cta rv"><h2>%s</h2><p>%s</p><div class="btns"><a class="btn btn-p btn-l" href="/#tool" data-tool>%s무료로 AI 작성률 검사</a>'
            '<a class="btn btn-g btn-l" href="/pricing/">요금 보기</a></div></div></div></section>') % (h, p, ico("search"))


def crumbs_html(trail):
    return '<nav class="crumb" aria-label="현재 위치"><a href="/">홈</a>' + "".join('<span>›</span>' + ('<a href="/%s">%s</a>' % (u, esc(n)) if i < len(trail) - 1 else '<span>%s</span>' % esc(n)) for i, (n, u) in enumerate(trail)) + "</nav>"


def proof_line():
    S = SAMPLES[0]
    return ('<p class="hero-proof"><span class="hp-n"><s>%d%%</s><i>→</i><em>%d%%</em></span><span><b>%s 예시, 한 번의 휴머나이징</b> · 실제 엔진으로 잰 값입니다. 글마다 결과는 다릅니다.</span></p>' % (
        S["before"]["rate"], S["after"]["rate"], esc(S["label"])))


ORBIT = ('<svg class="orbit" viewBox="0 0 980 760" aria-hidden="true" focusable="false"><defs>'
         '<linearGradient id="og1" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1ca6fe" stop-opacity="0"/><stop offset=".45" stop-color="#64d2ff" stop-opacity=".85"/><stop offset="1" stop-color="#0b63f6" stop-opacity="0"/></linearGradient>'
         '<linearGradient id="og2" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#0b63f6" stop-opacity="0"/><stop offset=".5" stop-color="#3ea6ff" stop-opacity=".55"/><stop offset="1" stop-color="#1ca6fe" stop-opacity="0"/></linearGradient>'
         '<radialGradient id="og3"><stop offset="0" stop-color="#fff"/><stop offset=".35" stop-color="#9fe2ff" stop-opacity=".9"/><stop offset="1" stop-color="#1ca6fe" stop-opacity="0"/></radialGradient></defs>'
         '<g class="o1"><ellipse cx="490" cy="380" rx="430" ry="150" fill="none" stroke="url(#og1)" stroke-width="2.2" transform="rotate(-18 490 380)"/></g>'
         '<g class="o2"><ellipse cx="490" cy="380" rx="360" ry="230" fill="none" stroke="url(#og2)" stroke-width="1.4" transform="rotate(24 490 380)"/></g>'
         '<circle class="spark" cx="690" cy="262" r="26" fill="url(#og3)"/></svg>')


def hero(eyebrow, h1, lead, pts=None):
    """첫 화면: 어두운 바탕(궤도선) 왼쪽 글(알약 · 제목 · 설명 · 파일 상자 · 장점 · 실측 한 줄) + 오른쪽 실제 엔진 예시.
    검사 도구는 바로 아래 떠 있는 흰 판(tool_section). 좁은 화면은 예시를 도구 아래로 옮김(site.js)"""
    pts = pts or ["한국어 전용 엔진", "문장 단위 AI 작성률", "한글 · 워드 · PDF 그대로"]
    return ('<section class="hero" id="top">%s<div class="wrap"><div class="hero-grid">'
            '<div class="hero-copy"><div class="eb-row"><p class="eyebrow">%s</p><p class="eyebrow eb-2"><b>%s</b>AI 작성률 낮추기</p></div><h1 class="h1">%s</h1><p class="lead">%s</p>'
            '<div class="hero-up" data-hero-drop><div class="hu-h"><span class="hu-ic">%s</span><p><b>파일을 올리면 AI 작성률을 바로 검사합니다</b><span>한글(HWP · HWPX) · 워드(DOCX) · PDF · 텍스트, 끌어다 놓아도 됩니다</span></p></div>'
            '<div class="hu-b"><button class="btn btn-p" type="button" data-hero-pick>%s파일 올리기</button><a class="btn btn-g" href="#tool" data-tool>%s글 붙여 넣기</a></div></div>'
            '<ul class="hero-pts">%s</ul>%s</div>'
            '<div class="hero-demo" id="heroDemo">%s</div>'
            '</div></div></section>') % (
        ORBIT, eyebrow, ico("trend_down"), h1, lead, ico("upload"), ico("upload"), ico("pen"), "".join("<li>%s%s</li>" % (ico("check"), t) for t in pts), proof_line(), demo_card())


def tool_section():
    badges = [("lock", "가입 없이 무료"), ("file", "20만 자"), ("check", "한글 · 워드 · PDF"), ("shield", "글은 저장하지 않음")]
    return ('<section class="tool-sec" aria-labelledby="toolH"><div class="wrap"><div class="tool-panel">'
            '<div class="tool-head"><h2 id="toolH"><span class="ic">%s</span>AI 작성률 검사 · AI 휴머나이징</h2><div class="tool-badges">%s</div></div>'
            '<div id="tool" class="tool-w">%s</div></div><div class="demo-slot" id="demoSlot"></div></div></section>') % (
        ico("sparkle"), "".join('<span>%s%s</span>' % (ico(i), t) for i, t in badges), tool_html())


def example_section(h2="AI 휴머나이징 전과 후,<br>실제 엔진으로 잰 결과", alt=False):
    return ('<section class="sec%s" id="example"><div class="wrap"><div class="center"><p class="kick">%s실제 측정 결과</p><h2 class="h2">%s</h2>'
            '<p class="sub">아래 예시는 %s 엔진에 그대로 넣어 잰 실제 값입니다. 보라색은 AI 패턴이 검출된 문장, 초록색은 사람 문장으로 바꾼 곳입니다.</p></div>%s</div></section>') % (
        " alt" if alt else "", ico("eye"), h2, BRAND, compare_block())


def price_section(alt=True):
    return ('<section class="sec%s" id="price"><div class="wrap"><div class="center"><p class="kick">%s요금</p><h2 class="h2">AI 휴머나이징 가격,<br><em>쓴 만큼만</em> 냅니다</h2><p class="sub">월 구독 없이 한 번 충전하면 글자 수만큼만 빠지고, 남은 토큰은 5년 동안 사라지지 않습니다. 검사는 언제나 무료로 먼저 해 보세요.</p></div>%s'
            '<p class="price-note">AI 작성률 검사 무료 · AI 휴머나이징 1,000자 4토큰 · 1토큰 100원 · 부가세 포함 · 결제는 운영사 성균관컨설팅 결제 페이지(가입 없이 카드 · 간편결제)</p>%s</div></section>') % (
        " alt" if alt else "", ico("card"), pricing_cards(), calc_block())


def guides_section():
    G = [guide_by(s) for s in P.HOME_GUIDES]
    cards = "".join('<a class="gcard rv" href="/guide/%s/"><small>%s · %s</small><h3>%s</h3><p>%s</p><span class="go">읽어 보기 →</span></a>' % (g["slug"], g["cat"], esc(g["kw"]), esc(g["h1"]), esc(g["desc"])) for g in G)
    return ('<section class="sec alt" id="guides"><div class="wrap"><div class="center"><p class="kick">%s가이드</p><h2 class="h2">AI 작성률 낮추기 가이드</h2>'
            '<p class="sub">AI 탐지기가 무엇을 보고 AI 작성률을 매기는지, 논문 · 자기소개서별로 어떻게 낮추는지 정리했습니다.</p></div><div class="gcards">%s</div>'
            '<p class="center" style="margin-top:26px"><a class="btn btn-g" href="/guide/">가이드 모두 보기</a></p></div></section>') % (ico("file"), cards)


# ---------------- 홈 ----------------
def build_home():
    H = P.HOME
    body = hero(H["eyebrow"], H["h1"], H["lead"])
    body += tool_section()
    body += demo_json()
    body += P.metrics_strip(ico)
    body += P.why_section(ico)
    body += example_section()
    body += P.scale_section(ico)
    body += P.how_section(ico)
    body += P.features_section(ico, BRAND)
    body += P.compare_table(ico, BRAND)
    body += P.usecases_section(ico)
    body += guides_section()
    body += price_section(alt=False)
    body += '<section class="sec alt" id="faq"><div class="wrap-n"><div class="center"><p class="kick">%s자주 묻는 질문</p><h2 class="h2">AI 휴머나이징, 궁금한 점부터</h2></div>%s<p class="center" style="margin-top:22px"><a class="btn btn-g" href="/faq/">질문 모두 보기</a></p></div></section>' % (ico("chat"), faq_html(H["faq"]))
    body += cta_band()
    ld = [APP, ld_faq(H["faq"]), ld_howto("AI 작성률 낮추기(%s)" % BRAND, P.HOW_STEPS)]
    page("", H["title"], H["desc"], body, ld=ld, tool=True, priority="1.0", keywords=H["keywords"])


def build_pricing():
    trail = [("요금", "pricing/")]
    body = ('<section class="ph"><div class="wrap">%s<h1 class="h1">AI 휴머나이징 가격 · 요금 · 토큰 충전</h1><p class="lead">월 구독 없이 한 번 충전하고 쓴 만큼만 씁니다. AI 작성률 검사는 무료, 휴머나이징 1,000자 4토큰. 남은 토큰은 5년 동안 사라지지 않습니다.</p></div></section>'
            '<section class="sec-s"><div class="wrap">%s<p class="price-note">모든 가격은 부가세 포함입니다. 결제는 운영사 성균관컨설팅 결제 페이지에서 가입 없이 카드 · 간편결제로 합니다. 결제하면 보통 1분 안에, 적은 이메일로 16자리 토큰 코드가 갑니다.</p>%s</div></section>') % (
        crumbs_html(trail), pricing_cards(), calc_block())
    body += P.pricing_detail(ico)
    body += '<section class="sec alt"><div class="wrap-n"><h2 class="h2 center">결제 · 토큰 자주 묻는 질문</h2>%s</div></section>' % faq_html(P.PRICE_FAQ)
    body += cta_band("먼저 무료로 검사해 보세요", "AI 작성률이 높게 나온 문장만 휴머나이징하면 토큰을 아낄 수 있습니다.")
    page("pricing/", "AI 휴머나이징 가격 · 요금 · 토큰 충전 | AiHuman(AI휴먼)", "AiHuman AI 휴머나이징 가격. 라이트 100토큰 9,900원부터 맥스 2,000토큰 69,900원까지. 월 구독 없이 한 번 충전, AI 작성률 검사 무료 · 휴머나이징 1,000자 4토큰.",
         body, ld=[ld_offers(), ld_faq(P.PRICE_FAQ), ld_crumbs(trail)], priority="0.9", keywords="AI 휴머나이징 가격, AI 휴머나이징 요금, AI 작성률 낮추기 가격, AiHuman 요금")


def build_faq():
    trail = [("자주 묻는 질문", "faq/")]
    groups = [("서비스와 사용", P.HOME["faq"] + P.MORE_FAQ), ("결제와 토큰", P.PRICE_FAQ)]
    allq = [x for _, L in groups for x in L]
    gl = "".join('<a href="/guide/%s/">%s</a>' % (g["slug"], esc(g["kw"].split(" · ")[0])) for g in P.GUIDES)
    body = '<section class="ph"><div class="wrap">%s<h1 class="h1">자주 묻는 질문</h1><p class="lead">AI 휴머나이저, AI 작성률, AI 탐지기, 결제와 토큰에 대해 자주 받는 질문을 모았습니다.</p></div></section>' % crumbs_html(trail)
    body += '<section class="sec-s"><div class="wrap-n">%s<h2 class="faq-h">검색어로 찾는 가이드</h2><div class="links">%s</div></div></section>' % ("".join('<h2 class="faq-h">%s</h2>%s' % (h, faq_html(L)) for h, L in groups), gl)
    body += cta_band()
    page("faq/", "자주 묻는 질문 · AI 휴머나이저 FAQ | AiHuman(AI휴먼)", "AI 휴머나이저가 무엇인지, AI 탐지기의 AI 작성률을 낮출 수 있는지, 무료인지, 글이 저장되는지, 결제와 토큰은 어떻게 되는지 답해 드립니다.",
         body, ld=[ld_faq(allq), ld_crumbs(trail)], priority="0.8")


def build_guides():
    trail0 = [("가이드", "guide/")]
    cats = []
    for g in P.GUIDES:
        if g["cat"] not in cats:
            cats.append(g["cat"])
    cards = "".join('<a class="gcard rv" href="/guide/%s/"><small>%s · %s</small><h3>%s</h3><p>%s</p><span class="go">읽어 보기 →</span></a>' % (g["slug"], g["cat"], esc(g["kw"]), esc(g["h1"]), esc(g["desc"])) for g in P.GUIDES)
    body = ('<section class="ph"><div class="wrap">%s<h1 class="h1">AI 휴머나이징 가이드</h1><p class="lead">AI 작성률 낮추기, AI 탐지기 원리, 논문 · 자기소개서 AI 작성률, AI 휴머나이징 사이트 고르는 법까지 정리했습니다.</p></div></section>'
            '<section class="sec-s"><div class="wrap"><div class="gcards">%s</div></div></section>') % (crumbs_html(trail0), cards)
    body += cta_band()
    page("guide/", "AI 휴머나이징 가이드 · AI 작성률 낮추는 법 | AiHuman(AI휴먼)", "AI 작성률 낮추기, 카피킬러 · GPT킬러 AI 작성률, 챗GPT 작성률, AI 탐지기 원리, 논문 · 자기소개서 AI 작성률, AI 휴머나이징 사이트 비교까지 정리한 가이드.",
         body, ld=[ld_crumbs(trail0), {"@type": "CollectionPage", "name": BRAND + " AI 휴머나이징 가이드", "url": SITE + "/guide/", "hasPart": [{"@type": "Article", "headline": g["h1"], "url": SITE + "/guide/%s/" % g["slug"]} for g in P.GUIDES]}], priority="0.8")
    for g in P.GUIDES:
        trail = [("가이드", "guide/"), (g["h1"], "guide/%s/" % g["slug"])]
        toc = re.findall(r'<h2 id="([^"]+)">([^<]+)</h2>', g["body"])
        toc_html = ('<nav class="toc" aria-label="목차"><b>목차</b><ol>%s</ol></nav>' % "".join('<li><a href="#%s">%s</a></li>' % (i, t) for i, t in toc)) if toc else ""
        idx = P.GUIDES.index(g)
        others = [P.GUIDES[(idx + k) % len(P.GUIDES)] for k in (1, 2, 3)]
        rel = "".join('<a class="gcard" href="/guide/%s/"><small>%s</small><h3>%s</h3><p>%s</p></a>' % (o["slug"], o["cat"], esc(o["h1"]), esc(o["desc"])) for o in others)
        faq = ('<h2 id="faq">자주 묻는 질문</h2>' + faq_html(g["faq"])) if g.get("faq") else ""
        body = ('<article><section class="ph"><div class="wrap-n">%s<p class="kick">%s</p><h1 class="h1">%s</h1><p class="meta"><span>%s 편집팀</span><span>%s</span><span>읽는 데 %d분</span></p></div></section>'
                '<section class="sec-s"><div class="wrap-n"><div class="answer">%s</div>%s<div class="prose">%s%s</div>'
                '<div class="gcta"><h2>내 글의 AI 작성률, 지금 바로 확인하세요</h2><p>가입 없이 무료 · 문장마다 AI 검출 여부를 보여 드립니다.</p><a class="btn btn-p btn-l" href="/#tool">%s무료로 AI 작성률 검사</a></div>'
                '</div></section></article><section class="sec-s alt"><div class="wrap"><h2 class="h2">함께 읽으면 좋은 글</h2><div class="gcards">%s</div></div></section>') % (
            crumbs_html(trail), esc(g["cat"] + " · " + g["kw"]), esc(g["h1"]), BRAND, g["date"].replace("-", "."), max(2, len(re.sub(r"<[^>]+>", "", g["body"])) // 650), g["answer"], toc_html, g["body"], faq, ico("search"), rel)
        art = {"@type": "Article", "headline": g["h1"], "description": g["desc"], "inLanguage": "ko-KR", "datePublished": g["date"], "dateModified": g["date"], "keywords": g["kw"].replace(" · ", ", "),
               "author": {"@type": "Organization", "name": BRAND + " 편집팀", "url": SITE + "/about/"}, "publisher": {"@id": SITE + "/#org"},
               "mainEntityOfPage": SITE + "/guide/%s/" % g["slug"], "image": [SITE + "/assets/img/og.png"], "articleSection": g["cat"]}
        ld = [art, ld_crumbs(trail)] + ([ld_faq(g["faq"])] if g.get("faq") else [])
        page("guide/%s/" % g["slug"], g["title"], g["desc"], body, ld=ld, ptype="article", priority="0.7", lastmod=g["date"],
             extra_head='<meta property="article:published_time" content="%sT09:00:00+09:00">' % g["date"], keywords=g["kw"].replace(" · ", ", "))


def build_static():
    for S in P.STATIC:
        trail = [(S["crumb"], S["path"])]
        body = '<section class="ph"><div class="wrap-n">%s<h1 class="h1">%s</h1>%s</div></section><section class="sec-s"><div class="wrap-n prose">%s</div></section>' % (
            crumbs_html(trail), S["h1"], ('<p class="lead">%s</p>' % S["lead"]) if S.get("lead") else "", S["body"])
        page(S["path"], S["title"], S["desc"], body, ld=[ld_crumbs(trail)], priority=S.get("prio", "0.4"))
    body = '<section class="ph"><div class="wrap-n"><h1 class="h1">페이지를 찾을 수 없습니다</h1><p class="lead">주소가 바뀌었거나 없는 페이지입니다.</p><p><a class="btn btn-p" href="/">홈으로</a> <a class="btn btn-g" href="/#tool" data-tool>무료 AI 작성률 검사</a></p></div></section>'
    page("404.html", "페이지를 찾을 수 없습니다 | " + BRAND, "요청한 페이지를 찾을 수 없습니다.", body, noindex=True)


# ---------------- 넘기는 쪽: 토큰 메일의 /humanize/?pass= 단추 · 검색어 주소를 첫 화면으로 ----------------
MERGED = {"humanize/": "/#tool", "ai-humanizer/": "/", "humanizing/": "/", "free/": "/#tool", "results/": "/#example", "check/": "/#tool"}


def build_redirects():
    for path, to in MERGED.items():
        d = os.path.join(OUT, path)
        os.makedirs(d, exist_ok=True)
        base, hsh = to.split("#")[0], (("#" + to.split("#")[1]) if "#" in to else "")
        doc = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>%s · AI 휴머나이저</title><link rel="canonical" href="%s/">'
               '<meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0; url=%s"><meta name="viewport" content="width=device-width,initial-scale=1">'
               '<script>location.replace(%s + (location.search || "") + (location.hash || %s));</script></head>'
               '<body><p><a href="%s">%s 첫 화면으로 이동합니다</a></p></body></html>') % (
            BRAND, SITE, to, json.dumps(base), json.dumps(hsh), to, BRAND)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(doc)


# ---------------- 검색 · AI 검색용 파일 ----------------
def build_seo():
    urls = []
    for path, title, desc, lastmod, pr in PAGES:
        urls.append("<url><loc>%s/%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq><priority>%s</priority></url>" % (SITE, path, lastmod, "weekly" if pr >= "0.8" else "monthly", pr))
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n")
    bots = ["Googlebot", "Yeti", "Daum", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot", "Applebot-Extended", "CCBot", "Meta-ExternalAgent", "cohere-ai", "DuckAssistBot", "MistralAI-User"]
    rob = "# %s(%s) · 검색 엔진과 AI 검색이 모두 읽을 수 있게 엽니다\n" % (BRAND, BRAND_KO) + "".join("User-agent: %s\nAllow: /\n\n" % b for b in bots) + "User-agent: *\nAllow: /\nDisallow: /assets/vendor/\n\nSitemap: %s/sitemap.xml\n" % SITE
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(rob)
    open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8").write(P.llms_txt(SITE, PAGES, PACKS, SAMPLES))
    open(os.path.join(OUT, "llms-full.txt"), "w", encoding="utf-8").write(P.llms_full(SITE, PACKS, SAMPLES))
    items = "".join("<item><title>%s</title><link>%s/guide/%s/</link><guid>%s/guide/%s/</guid><pubDate>%s</pubDate><description>%s</description></item>" % (
        esc(g["h1"]), SITE, g["slug"], SITE, g["slug"], datetime.datetime.strptime(g["date"], "%Y-%m-%d").strftime("%a, %d %b %Y 09:00:00 +0900"), esc(g["desc"])) for g in P.GUIDES)
    open(os.path.join(OUT, "rss.xml"), "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>%s 가이드</title><link>%s/guide/</link><description>AI 작성률 낮추기와 AI 휴머나이징 가이드</description><language>ko</language>%s</channel></rss>' % (BRAND, SITE, items))
    open(os.path.join(OUT, "site.webmanifest"), "w", encoding="utf-8").write(json.dumps({"name": BRAND + " AI 휴머나이저", "short_name": BRAND, "start_url": "/", "display": "standalone", "background_color": "#ffffff", "theme_color": "#00113a", "lang": "ko",
                                                                                         "icons": [{"src": "/assets/img/logo-192.png?v=" + VER, "sizes": "192x192", "type": "image/png"}, {"src": "/assets/img/logo-512.png?v=" + VER, "sizes": "512x512", "type": "image/png"}]}, ensure_ascii=False))
    open(os.path.join(OUT, INDEXNOW_KEY + ".txt"), "w").write(INDEXNOW_KEY)
    for gf in GOOGLE_FILES:
        open(os.path.join(OUT, gf), "w").write("google-site-verification: %s" % gf)
    open(os.path.join(OUT, "CNAME"), "w").write(HOST + "\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("\n")
    prods = {"shop": SHOP, "idx": {k: v for k, v in SHOP_IDX.items()}, "items": {p["id"]: {"name": p["name"], "tok": p["tok"], "price": p["price"]} for p in PACKS}}
    open(os.path.join(OUT, "assets", "products.js"), "w", encoding="utf-8").write("/* %s 상품(빌드가 만듦: _src/build.py SHOP_IDX · PACKS) */\nwindow.AMP = %s;\n" % (BRAND, json.dumps(prods, ensure_ascii=False)))


BANNED = ["충분", "수강", "자격증", "선착순", "민간", "수료"]   # 프로젝트 지침: 사이트 문구에 쓰지 않는 말


def verify():
    bad = []
    for dp, dn, fn in os.walk(OUT):
        if "/assets" in dp:
            continue
        for f in fn:
            if not f.endswith((".html", ".txt", ".xml")):
                continue
            s = open(os.path.join(dp, f), encoding="utf-8").read()
            if "—" in s:
                bad.append("줄표(—) " + os.path.join(dp, f))
            if re.search(r">\s*None\s*<", s):
                bad.append("None 글자 " + os.path.join(dp, f))
            for w in ["한국휴머나이징", "한국휴머나이저", "humanizer.co.kr", "humanizing.ai.kr", "humanai.io.kr", "AIMarker", "aimarker", "Humani(", "휴머나이(Humani"]:
                if w in s:
                    bad.append("다른 브랜드 이름 %s %s" % (w, os.path.join(dp, f)))
            for w in BANNED:
                if w in re.sub(r"<[^>]+>", " ", s):
                    bad.append("쓰지 않는 말 %s %s" % (w, os.path.join(dp, f)))
            if f == "index.html" and dp == OUT and re.search(r"카피킬러|GPT킬러|지피티킬러", re.sub(r"<script[\s\S]*?</script>", "", s)):
                bad.append("첫 화면에 검사기 이름")
            for m in re.finditer(r'href="(/[^"#?]*)', s):
                u = m.group(1)
                if u.startswith("/assets/") or u.endswith((".png", ".svg", ".ico", ".xml", ".webmanifest", ".txt")):
                    continue
                t = os.path.join(OUT, u.lstrip("/"), "index.html") if u.endswith("/") else os.path.join(OUT, u.lstrip("/"))
                if not os.path.exists(t):
                    bad.append("링크 " + u + " in " + f)
            for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
                try:
                    json.loads(m.group(1))
                except Exception as e:
                    bad.append("JSON-LD " + f + " " + str(e))
    return sorted(set(bad))


if __name__ == "__main__":
    build_home()
    build_pricing()
    build_faq()
    build_redirects()
    build_guides()
    build_static()
    build_seo()
    problems = verify()
    print("pages", len(PAGES), "problems", len(problems))
    for p in problems[:40]:
        print(" -", p)
