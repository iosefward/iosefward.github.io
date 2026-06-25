#!/usr/bin/env python3
"""Resize + watermark images for the iosefward.co.uk gallery.

Downscales each image so its longest edge is at most --max-edge px (never
upscales), stamps a watermark in the bottom-right corner, strips metadata, and
saves a web-optimised progressive JPEG whose size is kept under --max-kb by
stepping the JPEG quality down adaptively.

Usage:
    python optimize_image.py INPUT [INPUT ...] [options]

INPUT may be image files or directories (directories are scanned for common
image types, non-recursively). Examples:
    python optimize_image.py photo1.jpg photo2.png --out content/gallery/orks
    python optimize_image.py ~/Downloads/minis --out content/gallery/orks
"""
import argparse
import io
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}

# Nicer-looking fonts if present on the system; otherwise Pillow's bundled
# scalable default is used (supports sizing + anchor in Pillow >= 10).
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def load_font(size):
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size)
    except TypeError:
        # Very old Pillow: non-scalable bitmap default.
        return ImageFont.load_default()


def collect_inputs(paths):
    files = []
    for raw in paths:
        p = Path(raw).expanduser()
        if p.is_dir():
            files.extend(sorted(c for c in p.iterdir()
                                if c.suffix.lower() in IMAGE_EXTS))
        elif p.is_file():
            files.append(p)
        else:
            print(f"  ! skipping (not found): {p}", file=sys.stderr)
    return files


def add_watermark(img, text):
    """Stamp `text` in the bottom-right, white with a soft shadow so it stays
    legible over both light and dark photos."""
    w, h = img.size
    font_size = max(14, int(w * 0.022))
    font = load_font(font_size)
    margin = max(8, int(w * 0.018))

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    anchor_xy = (w - margin, h - margin)
    try:
        draw.text((anchor_xy[0] + 2, anchor_xy[1] + 2), text, font=font,
                  fill=(0, 0, 0, 150), anchor="rd")
        draw.text(anchor_xy, text, font=font, fill=(255, 255, 255, 215),
                  anchor="rd")
    except ValueError:
        # Bitmap fallback font: no anchor support, position manually.
        tw = draw.textlength(text, font=font)
        x, y = w - margin - tw, h - margin - font_size
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 150))
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 215))

    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def encode_under_limit(img, max_kb):
    """Return (jpeg_bytes, quality) for the highest quality that fits max_kb."""
    limit = max_kb * 1024
    data = None
    for quality in range(88, 39, -3):
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
        data = (buf.getvalue(), quality)
        if buf.tell() <= limit:
            return data
    return data  # smallest we could manage, even if still over the limit


def process(path, out_dir, max_edge, max_kb, text, watermark):
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im)  # honour phone-camera rotation
        if im.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", im.size, (255, 255, 255))
            rgba = im.convert("RGBA")
            bg.paste(rgba, mask=rgba.split()[-1])
            im = bg
        else:
            im = im.convert("RGB")

        orig_w, orig_h = im.size
        scale = min(1.0, max_edge / max(orig_w, orig_h))
        if scale < 1.0:
            im = im.resize((round(orig_w * scale), round(orig_h * scale)),
                           Image.LANCZOS)

        if watermark:
            im = add_watermark(im, text)

        jpeg_bytes, quality = encode_under_limit(im, max_kb)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (path.stem + ".jpg")
    out_path.write_bytes(jpeg_bytes)

    kb = len(jpeg_bytes) / 1024
    flag = "" if kb <= max_kb else "  (still over limit — consider a smaller --max-edge)"
    print(f"  {path.name} -> {out_path.name}  "
          f"{orig_w}x{orig_h} -> {im.size[0]}x{im.size[1]}, "
          f"q{quality}, {kb:.0f} KB{flag}")
    return kb <= max_kb


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="image files and/or directories")
    ap.add_argument("--out", default="optimized",
                    help="output directory (default: ./optimized)")
    ap.add_argument("--max-edge", type=int, default=1800,
                    help="max longest-edge in px, downscale only (default: 1800)")
    ap.add_argument("--max-kb", type=int, default=500,
                    help="target upper size in KB (default: 500)")
    ap.add_argument("--text", default="iosefward.co.uk",
                    help="watermark text (default: iosefward.co.uk)")
    ap.add_argument("--no-watermark", action="store_true",
                    help="skip the watermark")
    args = ap.parse_args()

    files = collect_inputs(args.inputs)
    if not files:
        print("No images found.", file=sys.stderr)
        return 1

    out_dir = Path(args.out).expanduser()
    print(f"Optimising {len(files)} image(s) -> {out_dir}")
    ok = sum(process(f, out_dir, args.max_edge, args.max_kb, args.text,
                     not args.no_watermark) for f in files)
    over = len(files) - ok
    print(f"Done: {ok} within {args.max_kb} KB"
          + (f", {over} over limit" if over else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
