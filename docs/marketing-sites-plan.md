# StudioLoop Marketing Sites Plan

Date: 2026-02-18

## Architecture Decision
Use **Astro 5** in the existing Turborepo monorepo for both marketing sites.

Implemented apps:
- `frontend/apps/marketing-gyms` -> `manage.studioloop.co.za` (B2B)
- `frontend/apps/marketing-consumers` -> `app.studioloop.co.za` (B2C)

Why this stack:
- Static-first output for strong Core Web Vitals and SEO
- Lightweight by default (minimal client JavaScript)
- Fits existing pnpm workspace and static hosting targets (Cloudflare Pages/Vercel)

## Funnel Strategy
### B2B: Gym Owners (`marketing-gyms`)
- Goal: **demo request**
- Intent: longer consideration cycle
- Core sections: Hero + product snapshot, pain/problem framing, feature blocks, ROI metrics, pricing context, FAQ, demo form
- SEO intent: `gym management software South Africa`, `Mindbody alternative South Africa`

### B2C: Gym-Goers (`marketing-consumers`)
- Goal: **app waitlist/download**
- Intent: short decision cycle
- Core sections: Hero + local search cue, 3-step flow, neighborhood browse, class variety, pricing teaser, waitlist form
- SEO intent: `class booking app Cape Town`, `try different gyms Cape Town`

## Measurement and Quality Gates
- Track events: `hero_cta_click`, `pricing_view`, `demo_request_submit`, `waitlist_submit`
- Targets: `LCP < 2.5s`, `INP < 200ms`, `CLS < 0.1`
- Accessibility: WCAG 2.2 AA pass on headings, contrast, focus states, form labels

## Next Build Steps
1. Add page routes (`/pricing`, `/faq`, `/features`, `/case-studies`) for both apps.
2. Wire form submissions to backend lead endpoints + anti-spam (honeypot + rate limiting).
3. Add analytics instrumentation (PostHog/Plausible/GA4).
4. Add Lighthouse CI checks to prevent regression before deploy.
