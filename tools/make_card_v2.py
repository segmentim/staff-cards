"""SEGMENT staff cue-card generator V2 — photo card-news style (1080x1350 JPEG, Korean).

V2 layout (matches cards/sample-v2-photo-style.jpg):
  실사진 배경(cover crop) + 하단 그라디언트 + 큰 타이포 + 악센트 키워드 컬러
  + 서브텍스트 + 출처 라인 + SEGMENT 워드마크(하단 중앙).

Usage:
    python3 make_card_v2.py --photo bg.jpg \
        --title "도면 없이 받은 견적서는 비교할 기준이 없습니다" \
        --kw "기준" \
        --sub "판단 근거는 계약 전에 준비할 수 있습니다" \
        --source "MATLOGIC · segment.im" --out card.jpg

사진 확보 불가 시에는 make_card.py(flat 텍스트 렌더)를 최후 수단으로 사용.
Requires: Pillow + Korean font (fonts-noto-cjk).
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 60
ACCENT_DEFAULT = (128, 192, 214)   # soft blue-teal (sample 기준 컬러)
WHITE = (245, 244, 240)
SUBTLE = (216, 214, 208)

FONT_BOLD = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKkr-Bold.otf",
    str(Path.home() / "fonts/NotoSansKR-Bold.ttf"),
]
FONT_REG = [p.replace("Bold", "Regular") for p in FONT_BOLD]


def load_font(cands, size):
    for p in cands:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    raise SystemExit("한글 폰트를 찾지 못했습니다 — fonts-noto-cjk 필요")


def cover(img, w, h):
    """Scale+center-crop to fill w x h."""
    src_r, dst_r = img.width / img.height, w / h
    if src_r > dst_r:
        nh = h; nw = int(h * src_r)
    else:
        nw = w; nh = int(w / src_r)
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return img.crop((left, top, left + w, top + h))


def wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur.rstrip()); cur = ""; continue
        if draw.textlength(cur + ch, font=font) <= max_w:
            cur += ch
        else:
            lines.append(cur.rstrip()); cur = ch.lstrip()
    if cur:
        lines.append(cur.rstrip())
    return lines


def draw_line_with_kw(draw, x, y, line, font, kw, base, accent):
    """Draw one line, coloring any occurrence of kw with accent."""
    if not kw or kw not in line:
        draw.text((x, y), line, font=font, fill=base)
        return
    cx = x
    idx = 0
    while idx < len(line):
        if line.startswith(kw, idx):
            draw.text((cx, y), kw, font=font, fill=accent)
            cx += draw.textlength(kw, font=font)
            idx += len(kw)
        else:
            draw.text((cx, y), line[idx], font=font, fill=base)
            cx += draw.textlength(line[idx], font=font)
            idx += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photo", required=True, help="배경 실사진 경로")
    ap.add_argument("--title", required=True)
    ap.add_argument("--kw", default="", help="타이틀 내 악센트 컬러를 줄 키워드")
    ap.add_argument("--sub", default="")
    ap.add_argument("--source", default="segment.im")
    ap.add_argument("--wordmark", default="SEGMENT")
    ap.add_argument("--accent", default="", help="R,G,B (기본 teal)")
    ap.add_argument("--out", default="card_v2.jpg")
    a = ap.parse_args()

    accent = ACCENT_DEFAULT
    if a.accent:
        accent = tuple(int(x) for x in a.accent.split(","))

    bg = Image.open(a.photo).convert("RGB")
    im = cover(bg, W, H)

    # 하단 그라디언트(가독성): 위 40%는 투명 → 아래로 갈수록 어둡게.
    grad = Image.new("L", (1, H), 0)
    for y in range(H):
        t = max(0.0, (y - H * 0.35) / (H * 0.65))
        grad.putpixel((0, y), int(205 * (t ** 1.25)))
    grad = grad.resize((W, H))
    dark = Image.new("RGB", (W, H), (18, 18, 20))
    im = Image.composite(dark, im, grad)

    d = ImageDraw.Draw(im)
    f_title = load_font(FONT_BOLD, 74)
    f_sub = load_font(FONT_REG, 40)
    f_src = load_font(FONT_REG, 30)
    f_mark = load_font(FONT_BOLD, 46)

    max_w = W - MARGIN * 2
    title_lines = wrap(d, a.title, f_title, max_w)
    sub_lines = wrap(d, a.sub, f_sub, max_w) if a.sub else []

    # 하단 정렬 블록 계산 (워드마크/출처 위로 타이틀·서브).
    mark_h = 56
    src_h = 44 if a.source else 0
    sub_h = len(sub_lines) * 54
    title_h = len(title_lines) * 88
    block_h = title_h + (24 + sub_h if sub_lines else 0)
    y = H - 90 - mark_h - src_h - block_h

    for line in title_lines:
        lw = d.textlength(line, font=f_title)
        draw_line_with_kw(d, (W - lw) / 2, y, line, f_title, a.kw, WHITE, accent)
        y += 88
    if sub_lines:
        y += 24
        for line in sub_lines:
            sw = d.textlength(line, font=f_sub)
            d.text(((W - sw) / 2, y), line, font=f_sub, fill=SUBTLE)
            y += 54

    if a.source:
        y += 18
        srcw = d.textlength(a.source, font=f_src)
        d.text(((W - srcw) / 2, y), a.source, font=f_src, fill=SUBTLE)

    # SEGMENT 워드마크 — 하단 중앙.
    mw = d.textlength(a.wordmark, font=f_mark)
    d.text(((W - mw) / 2, H - 96), a.wordmark, font=f_mark, fill=WHITE)

    im.save(a.out, "JPEG", quality=90)
    print(f"saved {a.out}")


if __name__ == "__main__":
    main()
