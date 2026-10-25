#!/usr/bin/env python3
"""Generate icon-512.png — brand §6: eclipse motif on navy
(#0d1b2a), one per-product glyph. Strike's glyph is the moment
of execution: a vertical strike line crossing a price level,
inside the gradient eclipse ring. PIL only; deterministic."""
from PIL import Image, ImageDraw

S = 512
NAVY = (13, 27, 42, 255)
STOPS = [(15, 246, 247), (0, 212, 255), (123, 44, 191)]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def grad(t):
    return lerp(STOPS[0], STOPS[1], t * 2) if t < 0.5 else \
        lerp(STOPS[1], STOPS[2], (t - 0.5) * 2)


def main():
    img = Image.new("RGBA", (S, S), NAVY)
    d = ImageDraw.Draw(img)
    ring = [54, 54, 458, 458]
    for i in range(72):
        t = i / 72
        d.arc(ring, start=i * 5, end=i * 5 + 6, fill=grad(t), width=13)
    d.ellipse([126, 126, 386, 386], fill=NAVY)
    # Price levels.
    for i, y in enumerate((196, 256, 316)):
        d.line([(164, y), (348, y)], fill=(160, 174, 192, 255), width=5)
    # The strike: a bold descending line through the mid level.
    d.line([(206, 158), (306, 354)], fill=grad(0.45), width=16)
    # The execution point.
    d.ellipse([238, 238, 274, 274], fill=(254, 254, 254, 255))
    d.ellipse([246, 246, 266, 266], fill=grad(0.8))
    img.save("icon-512.png")
    print("wrote icon-512.png", img.size, img.mode)


if __name__ == "__main__":
    main()
