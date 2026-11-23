# AIHuman 로고 원본 만들기(2026.11.23 대표 19:05 'AIHuman 으로 모두'): 대표가 준 logo-source.png 의 글자 'AiHuman' 에서
#  ① 소문자 i(파란 점 + 기둥)를 지우고 ② H 왼쪽 기둥과 같은 굵기 · 높이의 대문자 I 를 그 자리에 세우고
#  ③ 'AI' 두 글자는 파랑(#0B63F6, 사이트 주 색), 'Human' 은 원래 남색 그대로 → logo-source-aihuman.png
import numpy as np
from PIL import Image
SRC = '/home/claude/aihuman/_src/brand/logo-source.png'
OUT = '/home/claude/aihuman/_src/brand/logo-source-aihuman.png'
a = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float64)
H, W, _ = a.shape
NAVY = np.array([1, 8, 44], float)
BLUE = np.array([11, 99, 246], float)   # #0B63F6
WHITE = np.array([255, 255, 255], float)

def ink_alpha(px):
    """남색 글자의 덮임 정도(흰 바탕 0 → 남색 1)"""
    return np.clip((WHITE - px).sum(-1) / (WHITE - NAVY).sum(), 0, 1)

out = a.copy()
# ① 소문자 i 지우기(점 y217~265 · 기둥 y264~419, x995~1039 + 안티에일리어싱 여유)
out[210:428, 989:1047] = 255.0
# ② 대문자 I: H 왼쪽 기둥(x1067~1112)의 가로 단면(y=240, 가로줄 위)과 세로 단면(x=1090, 위 · 아래 끝)으로 사각형 만들기
rowp = ink_alpha(a[240, 1062:1118])            # 가로 단면(56px)
colp = ink_alpha(a[224:428, 1090])              # 세로 단면(위 끝 · 아래 끝 포함, 204px)
# 가운데(가로줄 높이)는 세로 단면이 1 이므로 그대로 씀. H 가로줄은 x1113 오른쪽이라 x1090 은 깨끗함
bar = np.outer(colp, rowp)                      # (204, 56)
# i 기둥 가운데(1016.5)에 맞춤: 원래 H 기둥 가운데는 1089.5 → 1016.5 로 73px 왼쪽
x0 = 1062 - 73; y0 = 224
m = bar[..., None]
# ③ 'A'(x750~990) 와 'I' 를 파랑으로
regA = (slice(200, 432), slice(750, 989))
alA = ink_alpha(out[regA])[..., None]
out[regA] = WHITE * (1 - alA) + BLUE * alA
reg = out[y0:y0 + bar.shape[0], x0:x0 + bar.shape[1]]
out[y0:y0 + bar.shape[0], x0:x0 + bar.shape[1]] = reg * (1 - m) + BLUE * m
Image.fromarray(np.clip(np.round(out), 0, 255).astype(np.uint8)).save(OUT, optimize=True)
print('ok', OUT, 'I at x', x0, x0 + bar.shape[1] - 1, 'bar max', round(float(bar.max()), 3))
