---
name: optimize-gallery-images
description: >-
  Resize and watermark photos for the iosefward.co.uk gallery. Use this whenever
  the user provides one or more images (painted miniatures, photos, screenshots)
  to add to the site or wants images "optimised", "shrunk", "resized for the
  repo", "web-ready", or "watermarked". It downscales to ~1800px on the longest
  edge, stamps an "iosefward.co.uk" watermark in the bottom-right corner, strips
  metadata, and writes web-optimised JPEGs kept under ~500KB so they're light
  enough to commit straight into the Git repo. Reach for this even if the user
  only says "add these to the gallery" — gallery images should always go through
  it first.
---

# Optimise gallery images

This site commits web-optimised images directly into the repo (no Git LFS), so
every gallery photo needs to be downscaled, watermarked, and size-capped before
it lands in `content/gallery/`. The bundled script does all of that in one pass.

## Why each step matters

- **Downscale to 1800px longest edge** — big enough to look sharp on retina
  screens, small enough to keep the repo lean. The script *never upscales*, so a
  smaller source is left at its native size.
- **Watermark bottom-right** — light deterrence against image theft on a public
  gallery. White text with a soft shadow stays legible over light or dark photos.
- **Cap at ~500KB** — the script steps JPEG quality down until the file fits, so
  pages stay fast and the repo stays small.
- **Strip metadata** — re-encoding drops EXIF (location, camera, timestamps),
  which you don't want to publish. EXIF *orientation* is applied first so phone
  photos aren't sideways.

## Usage

Run the script with the images the user gave you. Inputs can be individual files
or whole directories (directories are scanned non-recursively for common image
types).

```bash
python .claude/skills/optimize-gallery-images/scripts/optimize_image.py \
  <inputs...> --out content/gallery/<album-name>
```

**Always point `--out` at the target gallery album folder** so the optimised
files land where they'll be used, e.g. `content/gallery/ork-army`. The script
creates the folder if needed and names each output `<original-stem>.jpg`.

### Options

| Flag | Default | Purpose |
|------|---------|---------|
| `--out DIR` | `optimized` | output directory (set this to the album folder) |
| `--max-edge PX` | `1800` | longest-edge cap; downscale only |
| `--max-kb KB` | `500` | upper size target; quality steps down to fit |
| `--text STR` | `iosefward.co.uk` | watermark text |
| `--no-watermark` | off | skip the watermark (e.g. a non-gallery image) |

## Adding the results to the gallery

After optimising into an album folder, that folder is a Hugo **page bundle**.
To make it show up:

1. Ensure the album folder has an `index.md` (copy the pattern from
   `content/gallery/example-album/index.md`).
2. Reference each optimised image by filename inside the `{{< gallery >}}`
   shortcode, e.g. `<img src="01.jpg" class="grid-w33" />`.
3. Rebuild/preview with `hugo server` and confirm the album renders.

## Example

**Input:** user drops three phone photos of a freshly painted squad in
`~/Downloads` and says "add these to a new Necrons album".

**Action:**
```bash
python .claude/skills/optimize-gallery-images/scripts/optimize_image.py \
  ~/Downloads/IMG_2201.jpg ~/Downloads/IMG_2202.jpg ~/Downloads/IMG_2203.jpg \
  --out content/gallery/necrons
```
Then create `content/gallery/necrons/index.md` from the example-album template,
list the three `IMG_*.jpg` files in the gallery shortcode, and preview.
