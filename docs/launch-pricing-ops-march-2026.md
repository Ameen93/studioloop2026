# StudioLoop — Launch, Pricing & Ops Notes (March 2026)

_Last updated: 2026-03-03_

This captures the decisions/discussion from #studioloop so we can resume quickly.

---

## 1) Infrastructure + Operating Cost Estimates

### Current stack
- Backend: FastAPI on Railway (Docker)
- Database: Railway Postgres
- Frontend: Vercel deployments
- Payments: Stitch/Capitec VRP flow
- Email/notifications: transactional provider (as needed)

### Cost model (normal studio capacity assumptions)

#### 1 studio
- Estimated monthly infra: **~R105/mo + payment processing fees**
- Practical interpretation: effectively negligible vs studio subscription revenue.

#### 10 studios
- Estimated monthly infra: **~R540–R900/mo**
- Still very high-margin at SaaS pricing.

#### 100 studios
- Estimated monthly infra: **~R4,600/mo**
- Introduce Redis/cache + stronger monitoring; still strong gross margin.

#### 500 studios
- Estimated monthly infra + tooling + part-time support hire: **~R49,000–R64,000/mo**
- Major cost driver becomes people/ops, not compute.

### Core takeaway
Infra scales well; margin remains strong if pricing discipline is maintained.

---

## 2) Proposed StudioLoop Pricing Plans

### Starter — **R499/mo**
Target: solo instructors/micro studios.

Includes:
- Up to 50 active members
- 1 location
- Core scheduling + bookings
- Member management
- Basic check-in + payments
- Basic notifications

Positioning logic:
- “No-brainer” entry price for studios currently using WhatsApp/manual admin.

### Growth — **R999/mo**
Target: established boutique studios.

Includes everything in Starter, plus:
- Up to 200 active members
- Up to 5 staff logins
- Analytics dashboard
- Marketplace listing
- Waitlists + improved automation

Positioning logic:
- Sweet spot tier; marketplace/discovery value helps justify upgrade.

### Pro — **R1,999/mo**
Target: multi-instructor / multi-location operations.

Includes everything in Growth, plus:
- Unlimited members
- Up to 3 locations
- Unlimited staff logins
- Priority listing
- Advanced analytics + stronger support

Positioning logic:
- Still materially below enterprise alternatives while supporting complexity.

---

## 3) Pricing Logic Summary

- Undercut high-end incumbent pricing while keeping healthy unit economics.
- Keep entry barrier low (Starter), monetize growth via operational complexity (Growth/Pro).
- Marketplace/discovery is a strategic differentiator and future pricing lever.

Open items to finalize:
1. Trial policy (recommendation discussed: 30-day Growth trial)
2. Annual discount structure (e.g., 2 months free annual)
3. Whether to add transaction-based take-rate later

---

## 4) March 2026 Day-by-Day Launch Focus (Summary)

Primary phases discussed:
1. **Production hardening** (deploy stability, auth/payment/webhook verification)
2. **Pilot onboarding** (first studios from Cape Town target list)
3. **Consumer activation** (local acquisition + feedback loop)
4. **Scale prep** (pricing finalization, pipeline, app-store readiness)

Success target for month:
- 1+ paying studio
- 3–5 studios onboarded (paid + pilot mix)
- Early consumer traction
- Stable production operations and repeatable onboarding motion

---

## 5) Quick Access URLs (from deployment checks)

- Gym app: https://sl-gym.vercel.app
- Consumer app: https://sl-consumer.vercel.app
- Admin: https://sl-admin-eta.vercel.app
- Marketing (gyms): https://sl-marketing-gyms.vercel.app
- Marketing (consumers): https://sl-marketing-consumers.vercel.app
- Backend API: https://backend-production-e3cc8.up.railway.app
- Health check: https://backend-production-e3cc8.up.railway.app/api/v1/utils/health-check/

---

## 6) Note on Test Accounts

Test accounts were created for live validation during setup.
For security, rotate or replace shared test credentials before external demos.
