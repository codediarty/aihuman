# -*- coding: utf-8 -*-
"""AiHuman 로고(대표가 준 그림 2026.11.22: A 리본 표지 + AiHuman 글자 + 'AI휴먼 | AI 휴머나이징 전문 서비스')로 사이트 그림 만들기
logo-source.png(흰 바탕) -> 흰색을 투명으로 바꿔
  docs/assets/img/logo.png        표지 + 글자(머리글, 높이 120px · 화면에서는 40px 안팎)
  docs/assets/img/logo-w.png      어두운 바탕용(글자만 흰색, i 점 · 표지 색은 그대로)
  docs/assets/img/logo-mark.png   A 표지만
  docs/assets/img/logo-full.png   표지 + 글자 + 아래 줄(공유 그림 · 상품 그림용, 너비 1200)
  favicon.ico · favicon.svg · apple-touch-icon.png · logo-192/512.png  A 표지를 흰 바탕 정사각에
python3 _src/brand/make_brand.py"""
import os, io, base64
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
IMG = os.path.join(ROOT, "docs", "assets", "img")
os.makedirs(IMG, exist_ok=True)
src = Image.open(os.path.join(HERE, "logo-source.png")).convert("RGB")

# 그림 속 자리(2172x724): 표지 x150~746 · y160~566, 글자 AiHuman x756~1993 · y217~424, 아래 줄 y462~522
MARK = (138, 148, 758, 578)
WORD = (750, 205, 2004, 436)
LOGO = (138, 148, 2004, 578)   # 아래 줄(AI휴먼 | …)은 흰색으로 지우고 씀(no_sub)
FULL = (138, 148, 2004, 578)


def white_to_alpha(im):
    """흰 바탕을 투명으로(색은 흰 바탕 위에서와 똑같이 보이게 되돌림)"""
    a = np.asarray(im).astype(np.float32) / 255.0
    alpha = np.max(1.0 - a, axis=-1)
    alpha = np.clip((alpha - 0.035) / 0.965, 0, 1)          # 바탕의 아주 옅은 얼룩은 0으로
    safe = np.maximum(alpha, 1e-4)[..., None]
    rgb = np.clip(1.0 - (1.0 - a) / safe, 0, 1)
    out = np.concatenate([rgb, alpha[..., None]], -1)
    return Image.fromarray((out * 255).round().astype(np.uint8), "RGBA")


def tight(im, th=10):
    return im.crop(im.getchannel("A").point(lambda v: 255 if v > th else 0).getbbox())


def to_h(im, h):
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


def light(im, x_from):
    """어두운 바탕용: 글자(AiHuman · 아래 줄)의 남색 · 회색만 흰색으로. 표지(x_from 왼쪽)와 파란 i 점은 그대로"""
    a = np.asarray(im).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    cols = np.zeros(r.shape, bool); cols[:, x_from:] = True
    dark = cols & ~((b > 170) & (r < 120) & (b - r > 90))   # 파란 점(#0386FF 쪽)이 아닌 글자
    for c in (0, 1, 2):
        a[..., c] = np.where(dark, 255, a[..., c])
    return Image.fromarray(a.round().astype(np.uint8), "RGBA")


def no_sub(im):
    """아래 줄(x 752 오른쪽 · y 440 아래)을 흰 바탕으로 지움: 표지(왼쪽)는 y 566 까지 내려와 그대로 둠"""
    a = np.asarray(im).copy()
    a[440:, 752:] = 255
    return Image.fromarray(a, "RGB")


XW = 752 - LOGO[0]          # 글자가 시작하는 곳(잘라 낸 그림 안 x)
logo0 = white_to_alpha(no_sub(src).crop(LOGO))
logo, logo_w = tight(logo0), None
bb = logo0.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox()
logo_w = light(logo0, XW).crop(bb)
logo.save(os.path.join(HERE, "logo-cut.png"), optimize=True)
to_h(logo, 120).save(os.path.join(IMG, "logo.png"), optimize=True)
to_h(logo_w, 120).save(os.path.join(IMG, "logo-w.png"), optimize=True)

full0 = white_to_alpha(src.crop(FULL))
bb = full0.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox()
full = full0.crop(bb)
full.save(os.path.join(HERE, "logo-full.png"), optimize=True)
w = 1200
full.resize((w, round(full.height * w / full.width)), Image.LANCZOS).save(os.path.join(IMG, "logo-full.png"), optimize=True)
light(full0, XW).crop(bb).save(os.path.join(HERE, "logo-full-w.png"), optimize=True)

mark = tight(white_to_alpha(src.crop(MARK)))
mark.save(os.path.join(HERE, "logo-mark.png"), optimize=True)
to_h(mark, 240).save(os.path.join(IMG, "logo-mark.png"), optimize=True)
word = tight(white_to_alpha(src.crop(WORD)))
word.save(os.path.join(HERE, "logo-word.png"), optimize=True)


def square(size, pad, bg=(255, 255, 255, 255)):
    inner = round(size * (1 - 2 * pad))
    r = mark.copy(); r.thumbnail((inner, inner), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), bg)
    out.alpha_composite(r, ((size - r.width) // 2, (size - r.height) // 2))
    return out


square(192, .1).convert("RGB").save(os.path.join(IMG, "logo-192.png"), optimize=True)
square(512, .1).convert("RGB").save(os.path.join(IMG, "logo-512.png"), optimize=True)
square(180, .08).convert("RGB").save(os.path.join(IMG, "apple-touch-icon.png"), optimize=True)
square(256, .02, (0, 0, 0, 0)).save(os.path.join(ROOT, "docs", "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
b = io.BytesIO(); square(96, .02, (0, 0, 0, 0)).save(b, "PNG", optimize=True)
open(os.path.join(IMG, "favicon.svg"), "w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><image width="96" height="96" href="data:image/png;base64,%s"/></svg>' % base64.b64encode(b.getvalue()).decode())
print("ok logo", logo.size, "full", full.size, "mark", mark.size, "word", word.size)
