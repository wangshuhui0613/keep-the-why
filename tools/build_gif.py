#!/usr/bin/env python3
"""Assemble docs/demo.gif from scene screenshots.

Pipeline (both steps needed):

    NODE_PATH=<node_modules> node tools/gif_shots.js docs/_gif-scenes.html <shots-dir>
    python tools/build_gif.py --shots <shots-dir> --out docs/demo.gif
"""
import argparse
import os

from PIL import Image

SCENES = ["s1", "s2", "s3", "s4", "s5", "s6"]
W, H = 1000, 625
FPS = 10
HOLD = 16        # frames a scene stays on screen
FADE = 4         # crossfade frames between scenes
LAST_HOLD = 26   # end card stays longer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", required=True, help="directory containing s1.png ... s6.png")
    ap.add_argument("--out", default="docs/demo.gif")
    a = ap.parse_args()

    imgs = []
    for s in SCENES:
        p = os.path.join(a.shots, s + ".png")
        im = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
        imgs.append(im)

    frames = []
    for i, im in enumerate(imgs):
        hold = LAST_HOLD if i == len(imgs) - 1 else HOLD
        for _ in range(hold):
            frames.append(im.copy())
        if i < len(imgs) - 1:
            nxt = imgs[i + 1]
            for f in range(1, FADE + 1):
                frames.append(Image.blend(im, nxt, f / (FADE + 1)))

    out_dir = os.path.dirname(a.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    frames[0].save(
        a.out,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),
        loop=0,
        optimize=True,
    )
    print("wrote %s (%d frames, %.1f KB)" % (a.out, len(frames), os.path.getsize(a.out) / 1024))


if __name__ == "__main__":
    main()
