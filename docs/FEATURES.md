---
project: studioloop2026
type: features
status: parked
stack: FastAPI, SQLModel, PostgreSQL, React 19, Expo, Vite, Tailwind, Turborepo, Stitch, Railway, Vercel
domain: fitness, saas, marketplace
last_analyzed: 2026-03-14
tags: studioloop, features, fitness, saas
---

# Features & Capabilities

## Implemented Features

> Parked April 2026. "Implemented" here means the code exists and its tests pass
> locally — not that it was production-hardened or ever ran against real users. See the
> README for what is half-built.

### Authentication & Identity (Epic 1)
- Email registration/login with JWT (access: 24h, refresh: 7d)
- Google + Apple Sign-In (OAuth)
- Password reset via email
- User profiles + POPIA-compliant account deletion
- 4-tier RBAC: owner > manager > front_desk > instructor

### Gym Onboarding (Epic 2)
- Gym registration with owner account creation
- Gym profile configuration
- Operating hours + holiday closures
- Cancellation policies
- Marketplace participation toggle
- Member spreadsheet import (CSV)

### Staff Management (Epic 3)
- Add/remove staff with role assignment
- Permission matrix enforcement
- Working hours configuration
- Instructor pay rates
- Staff schedule + earnings views

### Membership Management (Epic 4)
- Create membership plans (R299/R499/R699 tiers)
- Configure benefits + rules
- Consumer enrollment + upgrade/downgrade
- Digital waiver acceptance

### Class Scheduling (Epic 5)
- Class template creation (recurring definitions)
- Schedule individual + recurring sessions
- Instructor assignment
- Approval workflow (instructor creates → manager approves)
- Capacity + waitlist configuration
- Marketplace pricing per class
- Calendar UI

### Booking & Check-in (Epic 6)
- Book with membership or pay-per-class
- Cancel with configurable grace period
- Waitlist with auto-promotion (24h expiry)
- QR code generation + mobile scanning
- Manual check-in fallback
- Membership validation on check-in
- Offline QR mode (React Native)

### Marketplace (Epic 7)
- Browse classes from other gyms
- Multi-filter (type, location, date, price)
- Gym profile discovery
- Marketplace subscription plans
- Cross-gym bookings
- Referral invites

### Payments (Epic 8)
- Stitch integration (Pay By Bank, VRP)
- Payment initiation workflow
- Webhook processing + Svix signature verification
- Failed payment detection + auto-retry (3 attempts)
- Gym payment dashboard
- Marketplace payout reports
- Consumer payment history + receipts (VAT 15%)

### Notifications (Epic 9)
- Booking confirmation + reminders
- Waitlist status updates
- Payment failure alerts
- Gym-to-member messaging
- WhatsApp for critical alerts
- Consumer notification preferences
- In-app notification center

### Analytics (Epic 10)
- Revenue reports
- Attendance tracking
- Membership health (at-risk member detection)
- Class performance metrics
- Staff performance reports
- Consumer statistics dashboard
- Gym owner action dashboard

### Admin & Real-time (Epic 11)
- Platform complaints + support
- Credit ledger
- Audit logging (POPIA)
- Webhook endpoint management
- WebSocket real-time updates (disabled on Vercel)

### Design System
- Outfit typeface
- Consumer: dark theme, coral accent (#FF6B4A)
- Gym: light theme, gold accent
- 19 shared UI components
- Dark/light theme toggle via CSS vars

### Deployment
- Backend: Railway (Docker, JNB region, auto-build)
- Frontend: Vercel (5 apps, auto-deploy on push)
- Database: Railway PostgreSQL (JNB, POPIA data residency)
- CI/CD: GitHub Actions (lint, type-check, test, deploy)

## Partial / In Progress
- E2E tests written (Playwright) but not running in CI
- Mobile apps not tested on physical devices
- Domain not registered (studioloop.co.za pending)

## Planned / TODO
- PayFast payment provider (second provider)
- Discovery Vitality integration
- WhatsApp notifications (Epic 9, story 9-8)
- Multi-language support (Afrikaans, Zulu, Xhosa)
- Wallet tab feature (spec in `docs/feature-wallet-tab.md`)
- Become a Member CTA (spec in `docs/feature-become-a-member-cta.md`)
- App store submissions (consumer-mobile, gym-mobile)
- Load/performance testing
- Penetration testing (auth, payments, tenant isolation)

## Known Issues
- Legacy models in `models_legacy.py` (should migrate to `app.models.auth`)
- `FIRST_SUPERUSER_PASSWORD` defaults to "changethis" (warns in local, errors in prod)
- OpenAPI client needs regeneration after Stitch route additions
- WebSocket real-time updates disabled on Vercel (no persistent connections)
