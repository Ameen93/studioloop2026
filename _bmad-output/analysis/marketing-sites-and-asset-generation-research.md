# Marketing Sites & Asset Generation Research

**Date:** 2026-02-18
**Status:** Research complete, ready for implementation

---

## Table of Contents

1. [Marketing Sites Architecture](#1-marketing-sites-architecture)
2. [B2B Site Structure (Gym Owners)](#2-b2b-site-structure-gym-owners)
3. [B2C Site Structure (Consumers)](#3-b2c-site-structure-consumers)
4. [Image Asset Requirements](#4-image-asset-requirements)
5. [ComfyUI Setup & Remote Access](#5-comfyui-setup--remote-access)
6. [ComfyUI API Reference](#6-comfyui-api-reference)
7. [AI Image Generation Models](#7-ai-image-generation-models)
8. [Essential ComfyUI Custom Nodes](#8-essential-comfyui-custom-nodes)
9. [Asset Generation Workflows](#9-asset-generation-workflows)
10. [Design Inspiration & Competitive Analysis](#10-design-inspiration--competitive-analysis)

---

## 1. Marketing Sites Architecture

### Decision: Astro 5 inside the existing Turborepo monorepo

**Why Astro over alternatives:**

| Concern | Astro | Next.js | Vite + react-router |
|---|---|---|---|
| SEO / Core Web Vitals | Excellent — zero JS by default | Good but ships React runtime | Poor — SPA, needs SSR workarounds |
| Bundle size | 0 KB JS for static sections | Ships React runtime even for static | Full React + router |
| Tailwind CSS v4 | Supported via `@astrojs/tailwind` | Supported | Supported |
| Monorepo / pnpm workspaces | Native support | Native support | Native support |
| React component reuse | Via "islands" — import `@sl/ui` selectively | Full React | Full React |
| Static export / CDN deploy | `output: 'static'` — one command | `output: 'export'` — second-class | `vite build` — good |
| Content management | Built-in Content Collections (typed) | Needs external CMS or MDX plugin | No built-in CMS |

Astro ships 40-90% less JavaScript than Next.js for equivalent marketing pages, directly improving LCP and CLS — the Core Web Vitals Google uses for ranking.

### Proposed monorepo structure

```
frontend/apps/
  web/                     # existing React app (authenticated product)
  consumer-mobile/         # existing Expo app
  gym-mobile/              # existing Expo app
  marketing-gyms/          # NEW — B2B landing site (gym owners)
  marketing-consumers/     # NEW — B2C landing site (gym-goers)
```

### Minimal Astro app setup in Turborepo

```json
// apps/marketing-gyms/package.json
{
  "name": "@sl/marketing-gyms",
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview"
  },
  "dependencies": {
    "@sl/ui": "workspace:*",
    "@sl/utils": "workspace:*",
    "astro": "^5.x",
    "@astrojs/react": "^4.x",
    "@astrojs/tailwind": "^5.x",
    "react": "19.1.0",
    "react-dom": "19.1.0"
  }
}
```

The existing `turbo.json` already handles `build`, `dev`, `lint` pipelines — no changes needed. The existing `pnpm-workspace.yaml` already includes `apps/*`.

### Deployment

Static export (`output: 'static'`) to Cloudflare Pages or Vercel. Both support automatic builds from the monorepo with path filtering.

---

## 2. B2B Site Structure (Gym Owners)

**Goal:** Long consideration cycle → demo booking or free trial signup. Visitors evaluate against Glofox, Mindbody, Gymdesk.

### Recommended page sections

```
1. NAV BAR
   - Logo, Features, Pricing, Blog, "Book a Demo" (primary CTA, always visible)

2. HERO
   - Headline: outcome-focused ("Fill every class. Automate the rest.")
   - Sub: one sentence on who it's for and the core mechanism
   - Primary CTA: "Book a free demo"
   - Secondary CTA: "See how it works" (scrolls to video)
   - Visual: animated dashboard screenshot in browser chrome frame,
     OR 30-second looping product video

3. SOCIAL PROOF BAR
   - "Trusted by X gyms across Cape Town"
   - 5-8 gym/studio logos in grayscale

4. PROBLEM AGITATION
   - 2-3 columns showing the "before" state:
     spreadsheet chaos, no-show members, manual billing
   - Short punchy copy — icon + 1 line each

5. FEATURE SHOWCASE (alternating image/text rows)
   - Member management → app screenshot
   - Class scheduling & booking → app screenshot
   - Automated billing & payments → app screenshot
   - Marketing & retention tools → app screenshot
   - Each row: headline, 2-3 bullet benefits, screenshot

6. INTERACTIVE DEMO / VIDEO WALKTHROUGH
   - Embedded product video or Arcade.so interactive demo
   - Huge trust builder

7. METRICS / ROI PROOF
   - "Gyms using StudioLoop see:"
   - 3 big numbers: e.g. "32% fewer no-shows", "4hrs/week saved", "2x faster onboarding"

8. TESTIMONIALS
   - 3-5 cards: gym owner photo, name, gym name, city, quote

9. PRICING
   - 3-tier table (Starter R299 / Growth R499 / Scale R799)
   - Monthly/annual toggle
   - Feature comparison per tier
   - "Most popular" badge on middle tier

10. FAQ
    - 6-10 accordion items: data migration, contracts, support, integrations

11. FINAL CTA
    - Bold headline + "Start your free trial"
    - "No credit card required. 14-day free trial."

12. FOOTER
    - Links: Features, Pricing, Blog, Privacy, Terms
    - Social icons, app store badges
```

### Key design principles for B2B

- Lead with a **business outcome** headline, not features
- Show the **real UI** — dark sidebar, clean tables, calendar views
- Put **pricing on the page** (gym owners hate "contact for pricing")
- Add a **competitor comparison** page targeting "Mindbody alternative", "Gymdesk alternative"

---

## 3. B2C Site Structure (Consumers)

**Goal:** Short intent cycle → app download or class booking. Visitors want to find a gym and book a class now.

### Recommended page sections

```
1. NAV BAR
   - Logo, Find a Gym, How it Works, Pricing, "Get Started Free"

2. HERO
   - Headline: desire-focused ("Thousands of gyms. One membership.")
   - Location search bar OR city selector — immediately useful
   - Background: high-quality fitness photography
   - App store download badges

3. HOW IT WORKS
   - 3-step visual: 1. Find → 2. Book → 3. Go
   - Simple icons + 1-line descriptions

4. CITY / GYM BROWSE
   - Map or grid of available locations (or top cities)
   - Real gym logos + names for credibility

5. WORKOUT VARIETY SHOWCASE
   - Grid of activity types: HIIT, Yoga, Swimming, Strength, Cycling, etc.
   - Each with a photo + label

6. APP SCREENSHOTS
   - iPhone mockup carousel: browse screen, booking screen, class details
   - Emphasize ease of use

7. SOCIAL PROOF
   - Star rating + review count ("4.8/5 from 12,000 members")
   - 3-4 short testimonial quotes with member photos

8. PRICING / PLANS
   - Simple credit-based or tier-based plans
   - "Cancel anytime" prominently displayed

9. PARTNER GYMS LOGOS
   - "Available at 500+ gyms" with logo grid

10. CTA SECTION
    - "Start exploring for free" with email capture
    - App store badges

11. FOOTER
```

### Key design principles for B2C

- Make the **location search** the primary hero interaction
- Show **breadth of gym types** with real photos
- Use **member count and city count** as social proof
- Display **app store rating + review count** near CTAs

---

## 4. Image Asset Requirements

### Priority 1 — Blocking launch

| Asset | Specs | Generation Method |
|---|---|---|
| Hero background (B2C) | 2560x1440px min, 2x | ComfyUI Flux Schnell — gym interior / workout scene |
| Hero background (B2B) | 2560x1440px min, 2x | ComfyUI Flux Schnell — professional gym management scene |
| Dashboard screenshots | 2x/3x retina, PNG | Real UI captures from the app |
| iPhone app mockups | 2x retina | Real screenshots in device frames (Shots.so) |
| Browser chrome mockup | 2x retina | Dashboard screenshot in browser frame |
| Logo (SVG + PNG) | Multiple variants | Recraft.ai for vector SVG |

### Priority 2 — High value (week 2)

| Asset | Generation Method |
|---|---|
| Gym owner testimonial photos | ComfyUI Flux — professional headshots |
| Feature icons (SVG) | Lucide/Phosphor icon set + Recraft for custom |
| "Before/after" problem illustrations | Figma or Recraft |
| Workout type photos (6-8 types) | ComfyUI Flux — HIIT, yoga, swimming, strength, cycling, etc. |

### Priority 3 — Post-launch

| Asset | Generation Method |
|---|---|
| Lifestyle photography | ComfyUI Flux + IPAdapter for style consistency |
| Gym interior variations | ComfyUI Flux — boutique, CrossFit, traditional |
| Video demo/walkthrough | Loom or screen recording |
| Infographic/stats visual | Custom SVG in Figma |

---

## 5. ComfyUI Setup & Remote Access

### Installing ComfyUI on Windows

#### Option A: Portable build (recommended for simplicity)

1. Download the latest release from https://github.com/comfyanonymous/ComfyUI/releases
2. Extract to a folder like `C:\ComfyUI`
3. Run `run_nvidia_gpu.bat` to verify it works locally

#### Option B: Manual install (more control)

```powershell
# Prerequisites: Python 3.12, Git, NVIDIA GPU with CUDA
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt

# For NVIDIA GPUs:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

python main.py
```

#### Option C: Via comfy-cli (recommended for fresh installs)

```powershell
pip install comfy-cli
comfy install
```

This installs ComfyUI and ComfyUI Manager together.

### Enabling Remote (LAN) Access

Edit the launch script to add `--listen 0.0.0.0`:

```bat
# For portable build, edit run_nvidia_gpu.bat:
.\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --listen 0.0.0.0 --port 8188

# For manual install:
python main.py --listen 0.0.0.0 --port 8188
```

### Windows Firewall Configuration (CRITICAL — most common failure point)

1. Open **Windows Defender Firewall with Advanced Security**
2. Click **Inbound Rules** → **New Rule**
3. Rule type: **Port**
4. Protocol: **TCP**, Specific local ports: **8188**
5. Action: **Allow the connection**
6. Profile: Check at minimum **Private** (for LAN access)
7. Name: **ComfyUI**

### Find the Windows machine IP

```powershell
ipconfig
```

Look for the IPv4 address on your LAN adapter (e.g. `192.168.1.100`).

### Access from Linux

```bash
# Web UI
firefox http://192.168.1.100:8188

# Test API
curl http://192.168.1.100:8188/system_stats
```

### Installing ComfyUI Manager

```powershell
cd ComfyUI\custom_nodes
git clone https://github.com/Comfy-Org/ComfyUI-Manager comfyui-manager
```

Restart ComfyUI. A **Manager** button appears in the top menu bar.

---

## 6. ComfyUI API Reference

### Key endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/prompt` | POST | Submit a workflow for execution. Returns `prompt_id` and queue position |
| `/prompt` | GET | Check current queue status |
| `/history` | GET | Full execution history |
| `/history/{prompt_id}` | GET | Status and output for a specific job |
| `/queue` | GET | Running and pending queue state |
| `/queue` | POST | Manipulate queue (cancel, delete) |
| `/interrupt` | POST | Stop current generation |
| `/view` | GET | Fetch generated image by filename/subfolder/type |
| `/upload/image` | POST | Upload an input image |
| `/upload/mask` | POST | Upload a mask image |
| `/system_stats` | GET | VRAM usage, device info |
| `/object_info` | GET | All available node types and parameters |
| `/ws` | WebSocket | Real-time progress, status, preview frames |

### Workflow submission pattern

1. Enable **Dev Mode** in ComfyUI Settings
2. Export workflow as **API format JSON** (Save → API Format)
3. Submit via `POST /prompt` with the workflow JSON
4. Listen on WebSocket for progress and completion
5. Fetch results from `/history/{prompt_id}`
6. Download images via `/view`

### Python client example

```python
import json, uuid, urllib.request, websocket

SERVER = "192.168.1.100:8188"
CLIENT_ID = str(uuid.uuid4())

def queue_prompt(workflow: dict) -> str:
    payload = json.dumps({
        "prompt": workflow,
        "client_id": CLIENT_ID
    }).encode("utf-8")
    req = urllib.request.Request(f"http://{SERVER}/prompt", data=payload)
    response = json.loads(urllib.request.urlopen(req).read())
    return response["prompt_id"]

def get_images(prompt_id: str) -> dict:
    history = json.loads(
        urllib.request.urlopen(f"http://{SERVER}/history/{prompt_id}").read()
    )
    outputs = {}
    for node_id, node_output in history[prompt_id]["outputs"].items():
        if "images" in node_output:
            images = []
            for img in node_output["images"]:
                url = (
                    f"http://{SERVER}/view"
                    f"?filename={img['filename']}"
                    f"&subfolder={img['subfolder']}"
                    f"&type={img['type']}"
                )
                images.append(urllib.request.urlopen(url).read())
            outputs[node_id] = images
    return outputs

def wait_for_completion(prompt_id: str):
    ws = websocket.WebSocket()
    ws.connect(f"ws://{SERVER}/ws?clientId={CLIENT_ID}")
    while True:
        msg = json.loads(ws.recv())
        if msg["type"] == "executing":
            data = msg["data"]
            if data["node"] is None and data["prompt_id"] == prompt_id:
                break
    ws.close()

# Usage
with open("workflow_api.json") as f:
    workflow = json.load(f)

prompt_id = queue_prompt(workflow)
wait_for_completion(prompt_id)
images = get_images(prompt_id)
```

### WebSocket message types

| Type | Purpose |
|---|---|
| `status` | Queue length and server state |
| `execution_start` | A prompt has begun |
| `executing` | Which node is running (`data.node` = ID, or `null` when done) |
| `progress` | Step-by-step sampler progress (value/max) |
| `executed` | A node finished, may contain preview data |
| Binary frames | Live preview images during sampling |

---

## 7. AI Image Generation Models

### Model comparison for fitness/gym marketing

| Use Case | Model | License | Notes |
|---|---|---|---|
| Photorealistic marketing photos | **Flux.1 Schnell** | Apache 2.0 (commercial OK) | Best self-hosted commercial option. Superior anatomy, lighting, text rendering. 4-8 step generation. |
| High-quality final renders | **Flux.1 Dev** | Non-commercial (licensable from BFL) | Better quality than Schnell, but requires commercial license from bfl.ai |
| Cloud API renders | **Flux.1.1 Pro / Flux.2 Pro** | Commercial via BFL API | Highest quality, not self-hosted |
| Fast iteration/concepting | **SDXL Lightning** | Apache 2.0 | 2-8 steps at 1024px. 4x faster than standard SDXL. Great for rapid exploration. |
| Real-time previews | **SDXL Turbo** | Open license | Single-step, very fast, lower quality. For interactive previewing only. |
| Stylized/artistic content | **SD3.5 Large** | Stability AI license | Better for specific art styles than Flux. Higher VRAM (12-16GB+). |
| Logos & icons | **Recraft** (recraft.ai) | Commercial | Native SVG vector output. Diffusion models cannot produce clean logos. |
| Custom brand LoRA | Train on Flux Schnell via FluxGym | Inherits Apache 2.0 | Full commercial rights when trained on your own data. |

### Why Flux for fitness content specifically

- Superior rendering of human anatomy — hands, faces, muscle definition dramatically better than SDXL
- Accurate text rendering (readable signage, equipment labels)
- Strong lighting and shadow handling for dramatic gym environments
- Excellent prompt adherence for complex scene descriptions

### Licensing notes (CRITICAL for commercial use)

- **Flux Schnell** (Apache 2.0) — fully safe for all commercial use
- **Flux Dev** — non-commercial by default. LoRAs trained on Dev inherit the restriction
- **Flux Pro** — commercial via BFL API only, not self-hosted
- **SDXL Lightning** (Apache 2.0) — fully safe for commercial use
- For commercial work: use Flux Schnell or license Flux Dev from Black Forest Labs

### Useful LoRAs (Civitai)

> Note: LoRAs trained on Flux Dev inherit its non-commercial license.

- **"Muscular men and women for Flux"** — physique-focused for athletic builds
- **"Dramatic Lighting Fitness Photography"** — dramatic lighting for fitness shots
- **"XLabs Flux Realism LoRA"** — general photorealism enhancement
- **"UltraRealistic LoRA Project - Flux"** — skin texture booster
- **"Body FLUX FIX"** — corrects body anatomy and proportions

For full commercial rights: train your own LoRA on Flux Schnell using FluxGym with licensed photography.

### Strategic workflow recommendation

1. **SDXL Lightning** for fast iteration — test compositions, layouts, color palettes
2. **Flux Schnell** for final renders — commercial-safe, high quality
3. **Recraft** for logos and vector icons
4. **IPAdapter** for maintaining visual consistency across a set of images

---

## 8. Essential ComfyUI Custom Nodes

Install via ComfyUI Manager after setup:

| Node Pack | Purpose |
|---|---|
| **ComfyUI Impact Pack** | Face detailer, segmentation, refinement — critical for fixing faces in generated photos |
| **ComfyUI ControlNet Auxiliary** | Pose estimation, depth maps, canny edge — control composition precisely |
| **ComfyUI IPAdapter Plus** | Image prompt adapter — maintain style/character consistency across images |
| **ComfyUI SDXL Prompt Styler** | Style templates for consistent aesthetic across batches |
| **ComfyUI WD14 Tagger** | Auto-tagging to understand and replicate styles from reference images |
| **rgthree-comfy** | Better workflow organization nodes |
| **ComfyUI AnimateDiff** | Short video/animation clips for social media content |

---

## 9. Asset Generation Workflows

### Hero Images (Gym Interiors, People Working Out)

- **Model:** Flux.1 Schnell
- **Resolution:** 1024x1024, upscale with Ultimate SD Upscale to 2048x2048+
- **ControlNet:** OpenPose for specific poses (feed a reference pose image)
- **IPAdapter:** Feed reference gym interior photos to lock environment style

**Prompt pattern:**
```
Professional fitness photography, [specific shot description],
dramatic side lighting, 4K commercial photography, sharp focus,
Canon EOS R5, fitness equipment, modern gym, cinematic atmosphere
```

**Negative prompt:**
```
cartoon, illustration, painting, blurry, low quality, watermark
```

### Marketing Banners

1. Generate background scene at banner aspect ratio (e.g. 1920x640)
2. Apply consistent style via ComfyUI workflow
3. Add text, logo, CTA in Figma/Canva — do not rely on AI for text placement
4. For the photographic element: Flux Schnell portrait/action shot, composite in design tool

### App Mockup Backgrounds

- **Model:** Flux Schnell
- **Prompt:** `blurred gym background bokeh, shallow depth of field, dark moody atmosphere, fitness club, out of focus weights and equipment, commercial background, minimalist`
- **Resolution:** Match mockup dimensions (e.g. 390x844 for mobile)

### Team / Lifestyle Photos

1. Generate base image with Flux Dev (commercial license) for best anatomy
2. Use ControlNet OpenPose for group poses
3. IPAdapter for consistent lighting reference
4. Run through Face Detailer (Impact Pack) to sharpen faces
5. Hires Fix (upscale + img2img at 0.4-0.5 denoise) for detail
6. Batch generate 20+ variations, curate the best

### Workout Type Photos (for B2C grid)

Generate a consistent set for: HIIT, Yoga, Swimming, Strength Training, Cycling, Boxing, Pilates, CrossFit.

- Use IPAdapter with a single reference image to maintain consistent lighting and color grading
- Same camera angle / framing pattern across all types
- 1024x1024 square crop for grid display

### Logos

- Use **Recraft** (recraft.ai) for native vector SVG output
- Or use Flux for mood board / concept art showing shapes and color direction
- Hand off concepts to a designer or trace in Inkscape
- Do NOT use diffusion models for production logos

---

## 10. Design Inspiration & Competitive Analysis

### B2B fitness SaaS sites to study

| Competitor | What they do well |
|---|---|
| **Glofox (ABC Glofox)** | Dark/rich palette, large dashboard screenshot hero, metrics bar ("X gyms trust us"), demo CTA on every scroll stop. Headline leads with growth, not features. |
| **Gymdesk** | Lighter, cleaner. Simplicity positioning. Shows actual UI clearly. Transparent pricing front-and-center. |
| **PushPress** | Strong testimonials from real gym owners with photos. "Switch from Mindbody" competitor-conquesting page. |

**Patterns to adopt:**
- Lead with business outcome headline, not feature headline
- Show real UI (dark sidebar, clean tables, calendar views)
- Put pricing on the page (gym owners hate "contact for pricing")
- Add competitor comparison pages ("Mindbody alternative", "Gymdesk alternative")

### B2C fitness membership sites to study

| Competitor | What they do well |
|---|---|
| **ClassPass** | Location-awareness is the hero. Map showing nearby gyms. Sparse copy, big photography, urgency ("5 spots left"). |
| **Gympass/Wellhub** | Bold large typography, real photography of diverse workouts, quick path to action. |

**Patterns to adopt:**
- Make location search the primary hero element
- Show breadth of gym types with real photos
- Use member count and city count numbers as social proof
- Display app store rating + review count near CTA

### 2025-2026 design trends to apply

- Dark mode with light mode toggle (especially B2B)
- Bento grid layouts for feature showcases
- Glassmorphism card effects (frosted-glass, subtle blur)
- Animated hero section (fade-in text, floating dashboard animation)
- Product screenshots in device frames
- Video demos embedded inline (autoplay muted loop in hero)
- Micro-interactions on CTAs (hover pulse, animated checkmarks)

---

## Sources

- [ComfyUI LAN Access — ComfyUI Wiki](https://comfyui-wiki.com/en/faq/how-to-access-comfyui-on-lan)
- [ComfyUI API Routes — docs.comfy.org](https://docs.comfy.org/development/comfyui-server/comms_routes)
- [ComfyUI Manager — GitHub](https://github.com/Comfy-Org/ComfyUI-Manager)
- [Flux.1 Schnell — HuggingFace (Apache 2.0)](https://huggingface.co/black-forest-labs/FLUX.1-schnell)
- [FLUX Licensing — Black Forest Labs](https://bfl.ai/licensing)
- [SDXL Lightning — ByteDance / HuggingFace](https://huggingface.co/ByteDance/SDXL-Lightning)
- [Astro vs Next.js 2025 — makersden.io](https://makersden.io/blog/nextjs-vs-astro-in-2025-which-framework-best-for-your-marketing-website)
- [SaaS Landing Page Trends 2026 — saasframe.io](https://www.saasframe.io/blog/10-saas-landing-page-trends-for-2026-with-real-examples)
- [Official ComfyUI WebSocket API Example — GitHub](https://github.com/comfyanonymous/ComfyUI/blob/master/script_examples/websockets_api_example.py)
