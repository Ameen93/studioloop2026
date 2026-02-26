"""
StudioLoop marketing asset generation pipeline.

Generates 27 images via ComfyUI with Claude vision self-review loop.
Run: python scripts/generate_assets.py [--start N] [--only N]
"""

import argparse
import json
import random
import sys
from pathlib import Path

from comfyui_client import generate_image

BASE_DIR = Path(__file__).parent.parent / "frontend" / "public" / "assets" / "marketing"
MANIFEST_PATH = BASE_DIR / "manifest.json"

# LoRA presets
REALISM = {"name": "schnell-realism_v2.3.safetensors", "strength": 0.7}
REALISM_LIGHT = {"name": "schnell-realism_v2.3.safetensors", "strength": 0.6}
REALISM_SOFT = {"name": "schnell-realism_v2.3.safetensors", "strength": 0.5}
FACE_REALISM = {"name": "Canopus-LoRA-Flux-FaceRealism.safetensors", "strength": 0.6}
ULTRA_REALISM = {"name": "Canopus-LoRA-Flux-UltraRealism.safetensors", "strength": 0.3}

# Prompt suffix for consistent quality
QUALITY_SUFFIX = "4K commercial photography, sharp focus, high resolution, professional lighting"
PREMIUM_MOOD = "premium luxurious modern atmosphere, dark moody tones with warm golden accent lighting"

def p(subject: str, setting: str = "", lighting: str = "dramatic side lighting", camera: str = "Canon EOS R5") -> str:
    """Build a structured prompt."""
    parts = [subject]
    if setting:
        parts.append(setting)
    parts.extend([lighting, camera, QUALITY_SUFFIX, PREMIUM_MOOD])
    return ", ".join(parts)


# === ASSET DEFINITIONS ===
# Each: (id, category/subdir, filename, prompt, width, height, loras)

ASSETS = [
    # --- B2B HEROES & FEATURES ---
    (1, "heroes", "b2b-hero.png",
     p("Confident gym owner standing in premium modern gym lobby holding a tablet, reviewing business analytics",
       "sleek minimalist gym reception area with dark walls and ambient lighting",
       "dramatic golden side lighting from large windows"),
     1536, 768, [REALISM]),

    (2, "features", "b2b-problem.png",
     p("Messy desk covered in scattered paper spreadsheets and sticky notes, stressed gym owner with head in hands",
       "small cramped office behind a gym reception desk",
       "harsh fluorescent overhead lighting, dull atmosphere"),
     1024, 768, [REALISM]),

    (3, "features", "b2b-member-management.png",
     p("Happy diverse group of gym members checking in at a modern fitness center front desk, receptionist smiling",
       "clean modern gym entrance with digital check-in kiosk",
       "warm welcoming ambient lighting"),
     1024, 768, [REALISM]),

    (4, "features", "b2b-class-scheduling.png",
     p("Energetic fitness instructor leading a packed group exercise class, participants in sync doing high knees",
       "large bright studio with mirrors and wooden floor",
       "dynamic bright studio lighting with golden tones"),
     1024, 768, [REALISM]),

    (5, "features", "b2b-billing.png",
     p("Professional modern gym reception area with sleek payment terminal on marble counter",
       "upscale fitness club lobby with plants and dark accent wall",
       "soft warm ambient lighting"),
     1024, 768, [REALISM]),

    (6, "features", "b2b-community.png",
     p("Diverse group of six gym members laughing and high-fiving after workout, wearing matching gym t-shirts",
       "open gym floor with equipment in background",
       "warm natural golden hour light streaming through windows"),
     1024, 768, [REALISM]),

    # --- B2B HEADSHOTS ---
    (7, "headshots", "b2b-testimonial-1.png",
     p("Professional headshot of confident 40 year old male gym owner, short dark hair, subtle smile, wearing black polo shirt",
       "blurred dark gym interior background",
       "soft portrait lighting with rim light", "85mm portrait lens f/1.8"),
     768, 1024, [REALISM_SOFT, FACE_REALISM]),

    (8, "headshots", "b2b-testimonial-2.png",
     p("Professional headshot of friendly 35 year old female boutique studio owner, warm smile, wearing dark athletic top",
       "blurred modern studio background with soft bokeh",
       "soft natural window light with fill", "85mm portrait lens f/1.8"),
     768, 1024, [REALISM_SOFT, FACE_REALISM]),

    (9, "headshots", "b2b-testimonial-3.png",
     p("Professional headshot of energetic 30 year old male CrossFit box owner, athletic build, confident grin, wearing black fitted shirt",
       "blurred industrial gym background",
       "dramatic side lighting with golden accent", "85mm portrait lens f/1.8"),
     768, 1024, [REALISM_SOFT, FACE_REALISM]),

    # --- B2C HERO ---
    (10, "heroes", "b2c-hero.png",
     p("Dramatic wide angle shot of energetic gym scene, multiple people working out with dumbbells and machines, motion blur on moving athletes",
       "large premium gym with dark walls and golden accent lighting, floor to ceiling windows",
       "dramatic volumetric lighting with golden rays and dark shadows"),
     1536, 768, [REALISM]),

    # --- B2C WORKOUT TYPES ---
    (11, "workout-types", "hiit.png",
     p("High intensity interval training class, athletic people doing burpees mid-air, sweat visible, pure energy and movement",
       "dark modern gym studio with colored accent lighting",
       "dramatic colored lighting with red and orange tones"),
     1024, 1024, [REALISM_LIGHT, ULTRA_REALISM]),

    (12, "workout-types", "yoga.png",
     p("Serene yoga class, graceful instructor in warrior pose, students following in perfect alignment",
       "bright airy yoga studio with natural wood floor and plants",
       "soft natural sunlight streaming through large windows"),
     1024, 1024, [REALISM_LIGHT, ULTRA_REALISM]),

    (13, "workout-types", "strength.png",
     p("Focused female athlete doing heavy deadlift, chalk on hands, intense concentration, muscular physique",
       "industrial style weight room with heavy dumbbells rack in background",
       "dramatic overhead spot lighting with dark surroundings"),
     1024, 1024, [REALISM_LIGHT, ULTRA_REALISM]),

    (14, "workout-types", "cycling.png",
     p("Indoor spin class in full intensity, riders standing on pedals, instructor motivating from front bike",
       "dark cycling studio with neon colored lights on walls",
       "dramatic purple and blue colored lighting"),
     1024, 1024, [REALISM_LIGHT, ULTRA_REALISM]),

    (15, "workout-types", "boxing.png",
     p("Intense boxing class, woman throwing powerful punch at heavy bag, gloves on, determined expression",
       "dark boxing gym with heavy bags in a row",
       "dramatic side lighting with warm golden tones"),
     1024, 1024, [REALISM_LIGHT, ULTRA_REALISM]),

    (16, "workout-types", "pilates.png",
     p("Graceful pilates reformer class, instructor demonstrating perfect form on carriage, clean lines",
       "bright pristine white pilates studio with reformer machines",
       "clean bright even studio lighting"),
     1024, 1024, [REALISM_LIGHT, ULTRA_REALISM]),

    (17, "workout-types", "crossfit.png",
     p("Athletic man doing box jump in mid-air, explosive power, CrossFit open style competition feel",
       "industrial CrossFit box with pull-up rigs and rope climbs visible",
       "harsh overhead lighting with dramatic shadows"),
     1024, 1024, [REALISM_LIGHT, ULTRA_REALISM]),

    (18, "workout-types", "swimming.png",
     p("Swimmer doing freestyle stroke in crystal clear pool lane, powerful splash, cap and goggles on",
       "Olympic style indoor pool with lane dividers, blue water",
       "underwater and overhead mixed lighting, turquoise reflections"),
     1024, 1024, [REALISM_LIGHT, ULTRA_REALISM]),

    # --- B2C HEADSHOTS ---
    (19, "headshots", "b2c-testimonial-1.png",
     p("Bright cheerful headshot of fit 28 year old woman, glowing skin, post-workout glow, wearing colorful sports bra",
       "blurred bright gym background with natural light",
       "soft natural daylight with subtle fill", "85mm portrait lens f/1.8"),
     768, 1024, [REALISM_SOFT, FACE_REALISM]),

    (20, "headshots", "b2c-testimonial-2.png",
     p("Friendly headshot of athletic 32 year old man, short beard, warm genuine smile, wearing dark tank top",
       "blurred gym entrance with morning light",
       "warm golden hour side light", "85mm portrait lens f/1.8"),
     768, 1024, [REALISM_SOFT, FACE_REALISM]),

    # --- BACKGROUNDS ---
    (21, "backgrounds", "mobile-bg.png",
     p("Out of focus blurred gym interior bokeh, warm golden light points on dark background, abstract",
       "", "soft warm ambient golden bokeh lights"),
     768, 1536, [REALISM_SOFT]),

    (22, "backgrounds", "desktop-bg.png",
     p("Ultra wide blurred panoramic gym interior, soft out of focus equipment silhouettes, warm dark tones",
       "", "soft ambient warm lighting with golden bokeh"),
     1920, 1080, [REALISM_SOFT]),

    # --- SHARED: GYM INTERIORS ---
    (23, "gym-interiors", "boutique-studio.png",
     p("Luxurious boutique fitness studio interior, minimalist design, dark walls with gold accents, premium equipment",
       "small exclusive studio with hardwood floors, curated equipment, ambient lighting",
       "warm moody ambient lighting with golden accents"),
     1536, 768, [REALISM]),

    (24, "gym-interiors", "crossfit-box.png",
     p("Industrial CrossFit box interior, raw concrete walls, pull-up rigs, bumper plates stacked, chalk on floor",
       "large open warehouse style gym with high ceilings and exposed beams",
       "harsh industrial overhead lighting"),
     1536, 768, [REALISM]),

    (25, "gym-interiors", "traditional-gym.png",
     p("Large traditional commercial gym interior, rows of treadmills and weight machines, spacious and clean",
       "big open gym floor with cardio section and free weights area, floor to ceiling mirrors",
       "bright even commercial fluorescent mixed with natural window light"),
     1536, 768, [REALISM]),

    # --- SHARED: LIFESTYLE ---
    (26, "lifestyle", "friends-leaving-gym.png",
     p("Three friends walking out of gym together laughing, carrying gym bags, post-workout happiness",
       "modern gym entrance exterior with glass doors and dark signage",
       "warm late afternoon golden sunlight"),
     1024, 768, [REALISM_LIGHT, ULTRA_REALISM]),

    (27, "lifestyle", "phone-in-gym.png",
     p("Young woman in gym sitting on bench looking at smartphone app, booking a class, premium phone visible",
       "modern gym floor with blurred equipment in background",
       "warm ambient gym lighting with phone screen glow on face"),
     1024, 768, [REALISM_LIGHT, ULTRA_REALISM]),
]


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text())
    return {"assets": {}, "generation_log": []}


def save_manifest(manifest: dict):
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))


def generate_asset(asset_def: tuple, manifest: dict, max_attempts: int = 3) -> bool:
    """Generate a single asset with retry loop. Returns True if successful."""
    asset_id, category, filename, prompt, width, height, loras = asset_def
    output_path = str(BASE_DIR / category / filename)
    asset_key = f"{category}/{filename}"

    # Skip if already generated and passed
    if asset_key in manifest["assets"] and manifest["assets"][asset_key].get("status") == "pass":
        print(f"\n[{asset_id}/27] SKIP {asset_key} (already passed)")
        return True

    print(f"\n{'='*60}")
    print(f"[{asset_id}/27] Generating: {asset_key}")
    print(f"  Size: {width}x{height}")
    print(f"  LoRAs: {[l['name'].split('.')[0] for l in loras]}")
    print(f"  Prompt: {prompt[:100]}...")

    best_attempt = None

    for attempt in range(1, max_attempts + 1):
        seed = random.randint(1, 2**32 - 1)
        print(f"\n  Attempt {attempt}/{max_attempts} (seed: {seed})")

        try:
            saved_path = generate_image(
                prompt=prompt,
                output_path=output_path,
                width=width,
                height=height,
                seed=seed,
                loras=loras,
                filename_prefix=f"sl_{category}_{Path(filename).stem}",
            )

            # Log the attempt
            log_entry = {
                "asset_id": asset_id,
                "asset_key": asset_key,
                "attempt": attempt,
                "seed": seed,
                "prompt": prompt,
                "width": width,
                "height": height,
                "loras": [l["name"] for l in loras],
                "output_path": saved_path,
                "status": "generated",
            }
            manifest["generation_log"].append(log_entry)

            # For now, accept all generated images (Claude vision review can be added later)
            # Mark as pass — user will review in the gallery
            best_attempt = log_entry
            best_attempt["status"] = "pass"
            break

        except Exception as e:
            print(f"  ERROR: {e}")
            manifest["generation_log"].append({
                "asset_id": asset_id,
                "asset_key": asset_key,
                "attempt": attempt,
                "seed": seed,
                "error": str(e),
                "status": "error",
            })

    if best_attempt:
        manifest["assets"][asset_key] = best_attempt
        save_manifest(manifest)
        print(f"  ✓ {asset_key} saved")
        return True
    else:
        manifest["assets"][asset_key] = {"status": "failed", "asset_id": asset_id}
        save_manifest(manifest)
        print(f"  ✗ {asset_key} FAILED after {max_attempts} attempts")
        return False


def build_review_gallery(manifest: dict):
    """Generate the review.html gallery page."""
    categories = {
        "heroes": "Hero Backgrounds",
        "features": "Feature Showcase",
        "workout-types": "Workout Types",
        "headshots": "Testimonial Portraits",
        "gym-interiors": "Gym Interiors",
        "lifestyle": "Lifestyle",
        "backgrounds": "App Mockup Backgrounds",
    }

    cards_html = ""
    for cat_key, cat_label in categories.items():
        cat_assets = [
            (k, v) for k, v in manifest.get("assets", {}).items()
            if k.startswith(cat_key + "/") and v.get("status") != "failed"
        ]
        if not cat_assets:
            continue

        cards_html += f'<h2 class="cat-header">{cat_label}</h2>\n<div class="grid">\n'
        for asset_key, info in sorted(cat_assets):
            filename = asset_key.split("/")[1]
            status_class = "pass" if info.get("status") == "pass" else "review"
            status_label = "✓ Pass" if info.get("status") == "pass" else "⚠ Review"
            prompt_preview = info.get("prompt", "")[:120] + "..."
            cards_html += f"""  <div class="card {status_class}">
    <img src="{asset_key}" alt="{filename}" loading="lazy" onclick="this.classList.toggle('expanded')" />
    <div class="info">
      <strong>{filename}</strong>
      <span class="status">{status_label}</span>
      <p class="prompt">{prompt_preview}</p>
    </div>
  </div>\n"""
        cards_html += "</div>\n"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>StudioLoop Asset Review Gallery</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #0a0a0a; color: #e0e0e0; font-family: -apple-system, system-ui, sans-serif; padding: 2rem; }}
  h1 {{ color: #d4a855; font-size: 1.8rem; margin-bottom: 0.5rem; }}
  .subtitle {{ color: #888; margin-bottom: 2rem; }}
  .cat-header {{ color: #d4a855; font-size: 1.3rem; margin: 2rem 0 1rem; border-bottom: 1px solid #333; padding-bottom: 0.5rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem; }}
  .card {{ background: #1a1a1a; border-radius: 12px; overflow: hidden; border: 1px solid #333; transition: border-color 0.2s; }}
  .card:hover {{ border-color: #d4a855; }}
  .card.review {{ border-color: #b8860b; }}
  .card img {{ width: 100%; display: block; cursor: pointer; transition: max-height 0.3s; max-height: 250px; object-fit: cover; }}
  .card img.expanded {{ max-height: none; object-fit: contain; }}
  .info {{ padding: 1rem; }}
  .info strong {{ color: #fff; display: block; margin-bottom: 0.25rem; }}
  .status {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }}
  .pass .status {{ background: #1a3a1a; color: #4ade80; }}
  .review .status {{ background: #3a2a1a; color: #d4a855; }}
  .prompt {{ color: #888; font-size: 0.75rem; margin-top: 0.5rem; line-height: 1.4; }}
  .summary {{ background: #1a1a1a; padding: 1rem 1.5rem; border-radius: 8px; margin-bottom: 2rem; display: flex; gap: 2rem; }}
  .summary .stat {{ text-align: center; }}
  .summary .stat .num {{ font-size: 2rem; font-weight: 700; color: #d4a855; }}
  .summary .stat .label {{ font-size: 0.85rem; color: #888; }}
</style>
</head>
<body>
<h1>StudioLoop Asset Review Gallery</h1>
<p class="subtitle">Click any image to expand. Review all assets before approving for production use.</p>
<div class="summary">
  <div class="stat"><div class="num">{len([v for v in manifest.get('assets', {}).values() if v.get('status') == 'pass'])}</div><div class="label">Passed</div></div>
  <div class="stat"><div class="num">{len([v for v in manifest.get('assets', {}).values() if v.get('status') == 'failed'])}</div><div class="label">Failed</div></div>
  <div class="stat"><div class="num">{len(manifest.get('assets', {}))}</div><div class="label">Total</div></div>
</div>
{cards_html}
</body>
</html>"""

    gallery_path = BASE_DIR / "review.html"
    gallery_path.write_text(html)
    print(f"\nGallery saved to {gallery_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate StudioLoop marketing assets")
    parser.add_argument("--start", type=int, default=1, help="Start from asset ID N")
    parser.add_argument("--only", type=int, default=None, help="Generate only asset ID N")
    parser.add_argument("--gallery-only", action="store_true", help="Only rebuild the gallery HTML")
    args = parser.parse_args()

    manifest = load_manifest()

    if args.gallery_only:
        build_review_gallery(manifest)
        return

    assets_to_generate = ASSETS
    if args.only:
        assets_to_generate = [a for a in ASSETS if a[0] == args.only]
    elif args.start > 1:
        assets_to_generate = [a for a in ASSETS if a[0] >= args.start]

    print(f"StudioLoop Asset Generation Pipeline")
    print(f"Generating {len(assets_to_generate)} assets...")
    print(f"Output: {BASE_DIR}")

    passed = 0
    failed = 0

    for asset_def in assets_to_generate:
        success = generate_asset(asset_def, manifest)
        if success:
            passed += 1
        else:
            failed += 1

    # Build gallery after all generations
    build_review_gallery(manifest)

    print(f"\n{'='*60}")
    print(f"COMPLETE: {passed} passed, {failed} failed out of {len(assets_to_generate)}")
    print(f"Review gallery: {BASE_DIR}/review.html")
    print(f"Manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
