---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish', 'step-12-complete']
status: complete
completedAt: 2026-01-21
inputDocuments:
  - product-brief-studioloop-2026-01-21.md
  - api-brainstorm.md
  - gym-management-app-brainstorm.md
  - consumer-app-brainstorm.md
  - brainstorming-session-2026-01-21.md
workflowType: 'prd'
documentCounts:
  briefs: 1
  brainstorming: 4
  research: 0
  projectDocs: 0
projectType: greenfield
classification:
  projectType: saas_platform_mobile
  domain: fitness_wellness_marketplace
  complexity: medium
  projectContext: greenfield
---

# Product Requirements Document - StudioLoop

**Author:** Ameen
**Date:** 2026-01-21

---

## Project Classification

| Aspect | Value |
|--------|-------|
| **Project Type** | SaaS Platform + Web & Mobile Apps |
| **Domain** | Fitness/Wellness Marketplace |
| **Complexity** | Medium-High |
| **Context** | Greenfield |

**Components:**
- FastAPI Backend (shared API layer)
- Gym Management Web App (B2B SaaS - `manage.studioloop.co.za`)
- Gym Management Mobile App (B2B - iOS + Android)
- Consumer Web App (B2C - `app.studioloop.co.za`)
- Consumer Mobile App (B2C - iOS + Android)
- Class Marketplace (two-sided)

**Development Priority:**
1. Gym Management Web — validate all gym features
2. Consumer Web — validate all consumer features
3. Consumer Mobile (iOS + Android) — mobile experience for members
4. Gym Management Mobile (iOS + Android) — on-floor tools for staff

---

## Executive Summary

**StudioLoop** is a fitness marketplace and gym management platform targeting Cape Town, South Africa — a market underserved by international solutions like ClassPass and Mindbody.

### Vision

Become the operating system for independent gyms in South Africa while building a consumer marketplace that fills empty class slots with paying customers.

### Core Differentiator

**Gym-first approach:** Unlike ClassPass (which alienated gym partners with ~40% payouts), StudioLoop solves gyms' operational pain first with affordable SaaS, earning trust before asking them to participate in the marketplace.

### Target Market

- **426+ gyms** in Western Cape, 86.93% single-owner operations
- **Small/medium gyms** currently using spreadsheets for member management
- **Fitness consumers** seeking variety without multiple memberships

### Revenue Model

| Stream | Description |
|--------|-------------|
| **Gym SaaS** | R299-799/month per gym |
| **Marketplace Commission** | % of cross-gym bookings |
| **Consumer Subscriptions** | R699-1,299/month for class packages |
| **Pay-per-class** | Individual class bookings |

### Go-to-Market Strategy

**"Trojan Horse":** Offer affordable gym management software → Gyms require members to use StudioLoop app → Consumers discover marketplace once app is installed → Platform revenue from SaaS + commissions + subscriptions.

---

## Success Criteria

### User Success

**Gym Owner (Thabo)**
| Outcome | Target | Measurement |
|---------|--------|-------------|
| Admin time reduction | 15hrs/week → <5hrs/week | Weekly admin task tracking |
| Payment collection rate | >95% on time (vs ~85% manual) | Automatic payment monitoring |
| Churn prediction accuracy | Catch 70% of at-risk members | At-risk flags vs actual cancellations |
| Off-peak class fill rate | >40% of marketplace-listed slots | Booking analytics |
| Revenue recovered | R5,000+/month per gym | Previously missed payments now collected |

**Aha Moment:** First automatically caught failed payment within 30 days of onboarding

**Consumer (Lerato)**
| Outcome | Target | Measurement |
|---------|--------|-------------|
| Class variety | 3+ unique gyms visited/month | Booking diversity tracking |
| Booking completion | >85% attendance rate | Bookings made vs attended |
| Marketplace discovery | 30% of app users try marketplace | App users → marketplace conversion |
| Subscription value | >80% class utilization | Classes used vs subscription credits |

**Aha Moment:** First marketplace class booked within 14 days of app install

**Staff (Nomsa)**
| Outcome | Target | Measurement |
|---------|--------|-------------|
| Check-in speed | <5 seconds (vs 30+ manual) | QR scan to confirmation time |
| Schedule visibility | 100% of shifts visible in app | Complete shift data in system |
| Earnings clarity | Real-time class pay view | Always-current earnings display |

### Business Success

**Phase 1: Prove the Model (Months 1-6)**
| Metric | Target | Validates |
|--------|--------|-----------|
| Gyms onboarded | 20 gyms | SaaS value proposition |
| Consumer downloads | 2,000 users | Distribution via gyms works |
| Marketplace activation | 10% users book marketplace class | Marketplace demand exists |
| Gym retention | 90% at 3 months | Sticky product |

**Phase 2: Scale (Months 6-12)**
| Metric | Target |
|--------|--------|
| Gyms onboarded | 50 gyms |
| Consumer downloads | 10,000 users |
| Marketplace subscriptions | 500 active subscribers |
| Monthly revenue | R150,000 MRR |

**Phase 3: Market Leadership (Year 2)**
| Metric | Target |
|--------|--------|
| Gym market share | 150+ gyms (35% of Cape Town) |
| Consumer base | 50,000 users |
| Marketplace GMV | R1M/month in bookings |

### Technical Success

| Requirement | Target | Rationale |
|-------------|--------|-----------|
| API response time | <200ms p95 | Smooth booking experience |
| Real-time availability | <1s latency | WebSocket class updates |
| QR scan check-in speed | <2s scan-to-confirm | Frictionless gym entry (Gym Mobile) |
| System uptime | 99.5% | Gyms depend on system daily |
| Concurrent users | Support 5,000+ | Scale for marketplace traffic |
| Data isolation | Multi-tenant secure | Gym data never leaks |

### Measurable Outcomes (Leading Indicators)

| Indicator | Predicts | Action Trigger |
|-----------|----------|----------------|
| Gym login frequency drop | Churn risk | <3 logins/week |
| Consumer booking decline | Subscription cancellation | <2 bookings in 30 days |
| Class fill rate drop | Supply/demand mismatch | <30% avg fill rate |
| Support ticket spike | Product/UX issues | >50% increase week-over-week |

---

## Product Scope

### MVP - Minimum Viable Product

**Must have for launch validation:**

| Component | Core Features |
|-----------|---------------|
| **API** | Multi-tenant auth, gym/consumer CRUD, memberships, class scheduling, bookings with source tracking, waitlist, WebSocket real-time, webhooks, notifications, reports |
| **Gym App** | Action-first dashboard, member check-in (manual on web, QR scanner on mobile), space management, class scheduling + approval workflow, membership tiers, staff management, reporting, communication, gym profile |
| **Consumer App** | Home with bookings, browse/filter classes, booking flow, memberships, QR code display for check-in, history/stats, waitlist, share/invite |
| **Marketplace** | Flat-count subscriptions, pay-per-class, cross-gym discovery, gym payouts tracking |

**MVP Go/No-Go Criteria (Month 6):**
| Criteria | Target |
|----------|--------|
| Active gyms | 15+ daily users |
| Gym retention | 85%+ at 3 months |
| Consumer downloads | 1,500+ |
| Marketplace trials | 10%+ try marketplace |
| Gym owner NPS | >40 |
| Revenue | R30,000+ MRR |

### Growth Features (Post-MVP)

| Feature | Rationale |
|---------|-----------|
| Payment gateway integration | PayFast/Peach - deferred until MVP proven |
| Rating/review system | Collecting data, UI deferred |
| Equipment tracking | Nice-to-have, not core |
| SMS notifications | WhatsApp preferred in SA |
| Personalized recommendations | Needs usage data first |
| Social features | Find friends, follow instructors |
| Achievements/gamification | Streaks, badges, challenges |

### Vision (Future)

**Year 2:** Expand to Johannesburg/Durban, corporate wellness, multi-location gym support

**Year 3+:** "Super app" for SA fitness, personal trainer marketplace, wellness beyond fitness, expand to other African markets

---

## User Journeys

### Journey 1: Thabo's Transformation — From Spreadsheet Chaos to Control

**Opening Scene**
It's 9pm on a Thursday. Thabo sits in his small office at the back of his Woodstock gym, staring at a Google Sheet with 120 rows of member names. Three members are marked "payment pending" in yellow highlighting—but he can't remember when he last followed up. His WhatsApp is blowing up with questions about tomorrow's 6am class, and he still hasn't reconciled last month's payments with his bank statement.

He became a trainer to change lives. Instead, he's drowning in admin.

**Rising Action**
A fellow gym owner mentions StudioLoop at a Cape Town fitness meetup. "It's like R400 a month and does everything. My members love the app."

Thabo signs up for a trial. The onboarding wizard asks for his member spreadsheet—he uploads it, slightly embarrassed by the mess. Within 30 minutes, his 120 members are in the system, each with proper profiles and payment statuses.

He creates three membership tiers: Standard (gym access), Premium (gym + 8 classes), and Unlimited. He sets up his class schedule, assigns spaces (main floor, spin studio, yoga room), and enables the marketplace for his off-peak 2pm and 3pm slots.

**Climax**
Day 12. Thabo's phone pings: "3 failed payments detected. Auto-retry scheduled. Tap to review."

He opens his dashboard and sees something he's never had before: a clear list of at-risk members. Sipho hasn't checked in for 2 weeks. Ayanda's payment failed twice. Thembi is overdue for renewal.

He reaches out to each one personally. Sipho was feeling intimidated in the main gym—Thabo invites him to a beginner class. Ayanda had a card issue, now resolved. Thembi renews with a thank-you for the reminder.

He catches R8,000 in payments he would have missed.

**Resolution**
Two months later, Thabo's 2pm yoga class—previously empty—has 8 people in it, 5 from the marketplace. His admin time dropped from 15 hours to 4 hours a week. He's back to training clients, not chasing spreadsheets.

His gym's churn rate dropped from 45% to 28%.

**Capabilities Revealed:** Dashboard with action items, payment monitoring, at-risk member flagging, membership tier configuration, class scheduling, space management, marketplace listing, staff management

---

### Journey 2: Lerato Discovers Fitness Freedom

**Opening Scene**
Lerato scrolls Instagram in her Sea Point apartment, watching another boutique studio's stories. Hot yoga at Rise. Boxing at FightFit. Reformer pilates at The Movement Lab. She pays R899/month for Virgin Active but only goes twice a week—and all she does is the treadmill.

She wants variety. She wants to try everything. But she can't afford four memberships.

**Rising Action**
Her friend Naledi invites her to a spin class at a new studio in Woodstock. "Download StudioLoop to book," Naledi says. "The studio requires it for membership."

Lerato downloads the app, creates a profile. The studio needs her ID for their records—she uploads it once, done.

After her first spin class, she swipes over to the "Discover" tab out of curiosity. Suddenly, she sees classes across Cape Town: yoga in Camps Bay, boxing in Observatory, HIIT in Green Point. Some are discounted 30% off peak-hour prices.

She books a discounted yoga class at Rise for the next morning. Then a boxing taster at FightFit. Within a week, she's tried three new studios she'd been curious about for months.

**Climax**
Lerato gets the notification: "You've booked 6 classes this month across 4 gyms. Upgrade to StudioLoop Unlimited: 8 classes/month for R699."

She does the math. She was spending R899 at Virgin Active for 8 gym visits. Now she can get 8 classes anywhere—yoga, boxing, spin, pilates—for R699.

She cancels Virgin Active. She subscribes to StudioLoop.

**Resolution**
Three months later, fitness is Lerato's hobby again. Monday yoga in Camps Bay, Wednesday spin in Woodstock, Saturday boxing in Observatory. She's tried 12 different studios. Her QR code works everywhere.

She tells every colleague about it. Four of them download the app.

**Capabilities Revealed:** Consumer onboarding, gym linking, class discovery/browse, filters (type, location, time), class booking, marketplace subscription, QR code display for check-in, payment management, referral/sharing

---

### Journey 3: Nomsa Makes Front Desk Professional

**Opening Scene**
Nomsa started at the CrossFit box three months ago. She runs the front desk 4 days a week and teaches the 5pm beginner class. Her morning starts with a paper check-in list and a highlighter.

Every day, someone shows up who "definitely paid last week"—but Nomsa has no way to verify. She has to text the owner, wait for a reply, then awkwardly ask the member to wait. Some members get frustrated. One complained about her on Google Reviews.

She calculates her class pay manually at month end, matching her personal calendar to a WhatsApp thread with the owner.

**Rising Action**
The owner implements StudioLoop. Nomsa is skeptical—another system to learn.

But the onboarding is quick. She logs in, sees her role (Front Desk + Instructor), and her upcoming shifts. Her three classes this week are already scheduled. Her pay rate is set.

A member walks in. Instead of the paper list, Nomsa scans their QR code. The screen shows green: "Membership Active - Premium Plan. Classes remaining: 5."

Another member walks in, no QR code. Nomsa searches by phone number—finds them instantly. Yellow warning: "Payment 3 days overdue." She politely mentions it; the member updates their card on the spot via the app.

No awkward confrontations. No texting the owner.

**Climax**
End of month. Nomsa opens the app and taps "My Earnings." It shows 14 classes taught, at R150 each, total R2,100. It matches exactly what she calculated—but took 2 seconds instead of 30 minutes.

She sees the attendance for her beginner class has grown from 6 to 11 people over the month. The owner notices too and schedules a second beginner slot.

**Resolution**
Nomsa feels professional for the first time. No more paper lists, no more awkward payment questions, no more calculating pay. She can focus on welcoming members and teaching great classes.

**Capabilities Revealed:** Staff login/roles, QR scanner (Gym Mobile) + manual check-in (Gym Web), membership status display, member search (phone/name), payment status visibility, shift schedule view, earnings tracking, class attendance tracking

---

### Journey 4: David Just Wants His Gym

**Opening Scene**
David, 52, has been a member at his local gym for 5 years. He goes Monday, Wednesday, and Friday at 6:30am. He knows everyone. He has no interest in boutique studios or variety. He just wants to lift weights and chat with his gym friends.

**Rising Action**
The gym implements StudioLoop. David grumbles about "yet another app" but downloads it because it's now required for membership.

The first time, he fumbles with the QR code—but a staff member helps him. The second time, it takes 3 seconds. He realizes it's faster than signing the paper log.

He sets up auto-pay so he never has to think about membership again.

**Climax**
One morning, the app notifies him: "Your membership renews in 7 days. Tap to review."

He checks his membership—sees he's on the basic plan. There's a Premium option with 4 included classes per month. He's been curious about the Thursday yoga class his wife keeps mentioning.

He upgrades. He tries yoga. It's actually not bad.

**Resolution**
David is still David—lifting weights MWF at 6:30am. But now his membership is automatic, check-in is seamless, and he occasionally does Thursday yoga. He didn't ask for change, but he admits the app makes things easier.

**Capabilities Revealed:** Simple consumer onboarding, QR code display for check-in, auto-renewal, membership upgrade path, class booking for members, minimal friction experience

---

### Journey 5: Platform Admin — Maintaining the Marketplace

**Opening Scene**
Sarah works at StudioLoop HQ. Her job: ensure the marketplace runs smoothly for 50 gyms and 8,000 consumers. She monitors gym onboarding, reviews flagged issues, and manages platform health.

**Rising Action**
Monday morning, her dashboard shows:
- 3 new gym applications pending review
- 1 gym with unusually high cancellation rate (42% of bookings)
- 2 consumer complaints flagged for review
- Marketplace revenue up 15% week-over-week

She reviews the gym applications—checks their business registrations, verifies addresses, approves two and requests more info from one.

She investigates the high-cancellation gym: their classes start too late, causing consumers to abandon bookings. She sends the owner a suggestion to adjust class times.

**Climax**
A consumer complains that a gym marked them as "no show" when they actually attended. Sarah pulls the booking log—sees the check-in timestamp is missing. She reviews CCTV request timestamps with the gym, confirms the consumer did attend. She credits the consumer's account and flags the gym for check-in training.

**Resolution**
The marketplace stays healthy. Gym quality is maintained. Consumer trust is protected. Sarah's dashboard tells her everything she needs to know.

**Capabilities Revealed:** Admin dashboard, gym application review, gym health metrics, complaint handling, consumer credit management, gym performance monitoring, platform analytics

---

### Journey Requirements Summary

| Journey | Key Capabilities Revealed |
|---------|--------------------------|
| **Thabo (Gym Owner)** | Dashboard actions, payment monitoring, at-risk flagging, membership tiers, class scheduling, space management, marketplace listing |
| **Lerato (Consumer)** | Onboarding, gym linking, class discovery, filters, booking flow, subscriptions, QR code display, payments, sharing |
| **Nomsa (Staff)** | Staff roles, QR scanner (mobile) + manual check-in (web), membership verification, member search, payment visibility, shifts, earnings tracking |
| **David (Member)** | Simple onboarding, QR code display, auto-renewal, membership upgrade, minimal friction |
| **Sarah (Platform Admin)** | Admin dashboard, gym review, health metrics, complaints, credits, analytics |

---

## Domain-Specific Requirements

### Regulatory & Compliance

| Requirement | Details | MVP Impact |
|-------------|---------|------------|
| **POPIA Compliance** | SA's Protection of Personal Information Act - requires consent for data collection, right to access/delete, data breach notification | Consumer consent flows, privacy policy, data export capability |
| **Consumer Protection Act** | SA CPA governs subscription cancellations, cooling-off periods, fair terms | Clear cancellation policies, no hidden terms, refund handling |
| **Fitness Liability** | Industry standard waivers for gym access and class participation | Digital waiver acceptance during onboarding, gym-specific waivers |

### Technical Constraints

| Constraint | Requirement | Rationale |
|------------|-------------|-----------|
| **Data Residency** | SA-hosted or POPIA-compliant cloud | Consumer PII must be handled per POPIA |
| **Payment Readiness** | Abstracted payment interface | PayFast/Peach integration when ready |
| **Multi-tenant Isolation** | Gym data strictly separated | Gym A can never see Gym B's members |
| **Offline Capability** | QR code display (consumer) + QR scanner (gym mobile) must work with poor connectivity | SA mobile networks can be unreliable |

### Marketplace-Specific Patterns

| Pattern | Implementation | Why It Matters |
|---------|----------------|----------------|
| **Booking Source Tracking** | Every booking tagged "direct" or "marketplace" | Commission calculation and gym trust |
| **Cancellation Fairness** | Gym-defined policies, consistent enforcement | Prevents consumer abuse, protects gym revenue |
| **Waitlist Integrity** | First-come-first-served with timed confirmation | Fair allocation, no gaming the system |
| **Payout Transparency** | Gyms see exactly how marketplace revenue is calculated | Trust = marketplace participation |

### Risk Mitigations

| Risk | Mitigation |
|------|------------|
| **Gym leaves platform, takes members** | Consumer owns account, gym relationships are portable |
| **No-show epidemic** | Track no-show rate, flag repeat offenders, potential penalties |
| **Gym quality varies** | Collect ratings (even if hidden), monitor complaint rates |
| **Payment disputes** | Clear refund policies, audit trail for all bookings |
| **Data breach** | Encryption at rest and in transit, minimal PII storage, breach notification plan |

### SA Market Considerations

| Factor | Accommodation |
|--------|---------------|
| **Load shedding** | App works offline for check-in, graceful sync when online |
| **WhatsApp preference** | WhatsApp notifications over SMS |
| **Cost sensitivity** | Affordable SaaS pricing, avoid international pricing |
| **Mobile-first** | Many users have smartphones but limited data |

---

## SaaS Platform + Web & Mobile App Specific Requirements

### Project-Type Overview

StudioLoop is a **hybrid platform** consisting of **6 client applications**:

| Application | Platform | URL/Distribution | Purpose |
|-------------|----------|------------------|---------|
| **API Backend** | FastAPI | `api.studioloop.co.za` | Shared service layer |
| **Gym Management Web** | React | `manage.studioloop.co.za` | Full gym operations, reports, settings |
| **Gym Management Mobile** | iOS + Android | App Store / Play Store | On-floor check-in scanner, quick access |
| **Consumer Web** | React | `app.studioloop.co.za` | Class browsing, booking, QR display |
| **Consumer Mobile** | iOS + Android | App Store / Play Store | On-the-go booking, QR code display |

**Platform-Specific Feature Distribution:**

| Feature | Consumer Web | Consumer Mobile | Gym Web | Gym Mobile |
|---------|--------------|-----------------|---------|------------|
| QR code display | ✅ | ✅ | — | — |
| QR scanner | — | — | — | ✅ Only |
| Full reports/analytics | — | — | ✅ | ✅ |
| Class browsing/booking | ✅ | ✅ | — | — |
| Member management | — | — | ✅ | ✅ |
| Dashboard | — | — | ✅ | ✅ |
| Profile/settings | ✅ | ✅ | ✅ | ✅ |

**Development Priority (Web-First Validation Strategy):**
1. **Gym Management Web** — Build and validate all gym features first
2. **Consumer Web** — Build and validate all consumer features
3. **Consumer Mobile** — Port validated features to mobile experience
4. **Gym Management Mobile** — Add mobile-specific tools (QR scanner)

### Multi-Tenancy Model

| Aspect | Design Decision |
|--------|-----------------|
| **Gym Data** | Strictly isolated per gym — Gym A never sees Gym B's data |
| **Consumer Profiles** | Platform-owned, shared across gyms — one profile, many gym relationships |
| **Staff Accounts** | Gym-scoped — staff belong to specific gym(s) |
| **Marketplace** | Cross-tenant by design — consumers browse all participating gyms |

**Data Isolation Rules:**
- Gym financial data: Tenant-isolated
- Member lists: Tenant-isolated (gym sees only their members)
- Consumer profiles: Platform-level (consumer sees all their memberships)
- Class catalog: Aggregated for marketplace, filtered for direct gym view

### Permission Model (RBAC Matrix)

| Role | Gym App Access | Consumer App | API Scope |
|------|----------------|--------------|-----------|
| **Gym Owner** | Full access — all features, billing, staff management | N/A | gym:admin |
| **Manager** | Operations — classes, members, reports (no billing) | N/A | gym:manager |
| **Front Desk** | Check-in, bookings, member lookup | N/A | gym:frontdesk |
| **Instructor** | Own schedule, own class attendance | N/A | gym:instructor |
| **Consumer** | N/A | Full consumer features | consumer:* |
| **Platform Admin** | Admin dashboard — all gyms, all consumers | N/A | platform:admin |

### Subscription & Pricing Tiers

**Gym SaaS Tiers:**
| Tier | Price (est.) | Features |
|------|--------------|----------|
| **Starter** | R299/month | Up to 100 members, 2 staff, basic features |
| **Growth** | R499/month | Up to 300 members, 5 staff, full features |
| **Pro** | R799/month | Unlimited members/staff, priority support, API access |

**Consumer Marketplace:**
| Option | Pricing |
|--------|---------|
| **Pay-per-class** | Gym sets price (typically R80-150) |
| **8-class subscription** | R699/month — 8 classes at any gym |
| **12-class subscription** | R899/month — 12 classes at any gym |
| **Unlimited** | R1,299/month — unlimited classes |

### Integration Architecture

| Integration | Type | MVP Status |
|-------------|------|------------|
| **Payment Gateway** | PayFast/Peach Payments | Interface ready, implementation deferred |
| **WhatsApp** | Business API | MVP — emergency/critical notifications |
| **Email** | SendGrid/Postmark | MVP — transactional emails |
| **Push Notifications** | Firebase/OneSignal | MVP — booking/class alerts |
| **Webhooks** | Outbound events | MVP — gym integrations |
| **Calendar Sync** | Google/Apple Calendar | Post-MVP |

### Web Platform Requirements

| Requirement | Decision |
|-------------|----------|
| **Framework** | React with Vite (or Next.js for SEO on consumer site) |
| **Browsers** | Chrome, Safari, Firefox, Edge (latest 2 versions) |
| **Responsive** | Desktop-first for Gym Management, responsive for Consumer |
| **Domains** | `manage.studioloop.co.za` (Gym), `app.studioloop.co.za` (Consumer) |
| **Authentication** | JWT with secure httpOnly cookies |
| **Real-time** | WebSocket for class availability, booking updates |

### Mobile Platform Requirements

| Requirement | Decision |
|-------------|----------|
| **Platforms** | iOS 14+ and Android 10+ |
| **Framework** | React Native with Expo |
| **Offline Support** | QR code generation/display works offline, syncs when online |
| **Push Notifications** | Required — booking confirmations, class reminders, payment alerts |
| **Deep Linking** | Class sharing, gym profiles, referral links |
| **Background Tasks** | Push handling |

### Device Permissions Required (Mobile Only)

| Permission | Purpose | Consumer App | Gym App |
|------------|---------|--------------|---------|
| **Camera** | QR code scanning | No | Yes (required) |
| **Location** | "Near me" class discovery | Optional | No |
| **Notifications** | Push alerts | Requested | Requested |
| **Contacts** | Referral/invite friends | Optional | No |
| **Calendar** | Add class to calendar | Optional | No |

### Offline Mode Capabilities

| Feature | Offline Behavior |
|---------|------------------|
| **QR Code Display** | Works offline — code generated locally |
| **Check-in (Staff)** | Queue scans, sync when online |
| **Browse Classes** | Cached list, stale indicator |
| **Book Class** | Requires connectivity |
| **View Bookings** | Cached, syncs when online |

### Push Notification Strategy

| Trigger | Content | Timing |
|---------|---------|--------|
| **Booking Confirmed** | "You're booked for Yoga at Rise, tomorrow 8am" | Immediate |
| **Class Reminder** | "Your class starts in 1 hour" | 1 hour before |
| **Waitlist Spot** | "A spot opened! Confirm in 30 mins" | Immediate |
| **Payment Due** | "Membership renews in 3 days" | 3 days before |
| **Payment Failed** | "Payment failed — update your card" | Immediate |
| **New Classes** | "New boxing class added at FightFit" | Daily digest |

### App Store Compliance

| Requirement | Handling |
|-------------|----------|
| **In-App Purchases** | Marketplace subscriptions via app store billing (iOS) or direct (Android) |
| **Privacy Policy** | POPIA-compliant policy linked in app |
| **Data Deletion** | Account deletion flow per app store requirements |
| **Content Rating** | 4+ / Everyone — fitness content only |
| **Permissions Justification** | Clear explanation for camera, location, notifications |

### Implementation Considerations

| Consideration | Approach |
|---------------|----------|
| **API Versioning** | URL-based (v1, v2) with deprecation policy |
| **Rate Limiting** | Per-user/per-gym limits to prevent abuse |
| **Real-time Updates** | WebSocket for class availability, booking confirmations |
| **Caching Strategy** | Redis for sessions, class availability; CDN for static assets |
| **Error Handling** | Consistent error codes, user-friendly messages |
| **Logging/Monitoring** | Structured logging, APM for performance tracking |

---

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Dual-Track Problem-Solving MVP

| Track | Philosophy | Goal |
|-------|------------|------|
| **Gym SaaS** | "Replace spreadsheets" | Prove gyms will pay for affordable management software |
| **Consumer App** | "Required for membership" | Build user base through forced adoption via gyms |
| **Marketplace** | "Discovery layer" | Validate cross-gym booking demand once users are installed |

**Why This Works:**
1. Gym SaaS solves an immediate pain (admin chaos) — standalone value
2. Consumer app is required by gyms — guaranteed distribution
3. Marketplace is exposed once app is installed — organic discovery

**Resource Requirements:**
- Solo founder (Ameen) + potential contractor support
- Cape Town focus reduces complexity
- Cross-platform mobile (Flutter/RN) reduces dev effort

### MVP Feature Set (Phase 1)

**Core User Journeys Supported:**

| Journey | MVP Support |
|---------|-------------|
| Thabo (Gym Owner) | Full — dashboard, payments, memberships, classes, staff |
| Lerato (Consumer) | Full — discovery, booking, subscription, QR code display |
| Nomsa (Staff) | Full — check-in (manual + QR scanner), schedule, earnings |
| David (Member) | Full — QR code display, membership management |
| Sarah (Admin) | Partial — basic gym review, consumer support |

**Must-Have Capabilities:**

| Component | MVP Features |
|-----------|--------------|
| **API** | Multi-tenant auth, gym CRUD, consumer profiles, memberships, class scheduling, bookings (with source tracking), waitlist, WebSocket real-time, webhooks, notifications (email + push + WhatsApp), reports |
| **Gym App** | Action-first dashboard, member check-in (manual on web, QR scanner on mobile), space management, class scheduling + approval, membership tiers, staff roles + permissions, reporting suite, in-app/email/WhatsApp messaging, gym profile |
| **Consumer App** | Bookings home + overdue banner, class browse with filters, booking flow (subscription + pay-per-class), membership management, QR code display for check-in, class history, waitlist, share/invite |
| **Marketplace** | Flat-count subscriptions (8/12/unlimited), pay-per-class, cross-gym discovery, gym payout tracking |

**Explicitly Deferred from MVP:**

| Feature | Reason | When |
|---------|--------|------|
| Payment gateway integration | Research needed, interface abstracted | Pre-launch |
| Rating/review system UI | Collecting data, need design system | V2 |
| Equipment tracking | Nice-to-have, not core value | V2 |
| SMS notifications | WhatsApp preferred in SA, cost | V2 if needed |
| Social features | Find friends, follow | V2 |
| Personalized recommendations | Needs usage data | V2 |
| Gamification | Streaks, badges | V2 |
| Multi-location gyms | Target is single-location | When chains request |
| Corporate wellness | B2B2C channel | Phase 3 |

### Post-MVP Features

**Phase 2: Growth (After MVP Validation)**

| Feature | Value Add |
|---------|-----------|
| Payment gateway integration | Complete commerce flow |
| Rating/review system | Consumer confidence, gym quality signals |
| Calendar sync | Convenience |
| Equipment tracking | Gym operational efficiency |
| Personalized recommendations | Retention, discovery |
| Enhanced admin dashboard | Platform operations at scale |

**Phase 3: Expansion (Year 2)**

| Feature | Value Add |
|---------|-----------|
| Multi-city expansion | Johannesburg, Durban |
| Corporate wellness portal | B2B2C revenue stream |
| Multi-location gym support | Enterprise gym chains |
| Personal trainer marketplace | New supply category |
| Advanced analytics/AI | Churn prediction, demand forecasting |
| API marketplace | Third-party integrations |

### Risk Mitigation Strategy

**Technical Risks:**

| Risk | Mitigation |
|------|------------|
| Real-time scalability | Start with simple WebSocket, upgrade if needed |
| Offline sync complexity | MVP: offline QR only, expand later |
| Cross-platform bugs | Use mature framework (Flutter), thorough testing |
| Payment integration | Abstracted interface, can swap providers |

**Market Risks:**

| Risk | Mitigation |
|------|------------|
| Gyms won't adopt | Free trial, price lower than competition, demo spreadsheet savings |
| Consumers don't discover marketplace | Prominent in-app placement, onboarding prompt |
| ClassPass enters SA | First-mover advantage, gym-friendly economics |
| Low marketplace supply | Start with gyms already using SaaS, incentivize marketplace opt-in |

**Resource Risks:**

| Risk | Mitigation |
|------|------------|
| Solo founder bandwidth | Prioritize ruthlessly, hire contractors for mobile |
| Feature creep | Strict MVP boundaries, defer everything non-essential |
| Launch delays | Public commitment to 15 gym target, iterate not perfection |

### MVP Go/No-Go Criteria

**Decision Point: Month 6**

| Metric | Target | Validates |
|--------|--------|-----------|
| Active gyms | 15+ using daily | SaaS PMF |
| Gym retention | 85%+ at 3 months | Sticky product |
| Consumer downloads | 1,500+ | Distribution works |
| Marketplace trials | 10%+ of users | Demand exists |
| Gym owner NPS | >40 | Value creation |
| MRR | R30,000+ | Business viability |

**If Met:** Proceed to Phase 2, seek funding if needed
**If Not Met:** Analyze failure modes, pivot or refine

---

## Functional Requirements

### Account & Authentication

- **FR1:** Users can register using email, social login (Google, Facebook, Apple), or phone OTP
- **FR2:** Users can authenticate and maintain secure sessions across devices
- **FR3:** Users can reset their password via email
- **FR4:** Users can manage their profile information (name, photo, contact details)
- **FR5:** Users can delete their account and associated data (POPIA compliance)
- **FR6:** Platform can enforce role-based access control per user type

### Gym Management

- **FR7:** Gym owners can register their gym and complete onboarding
- **FR8:** Gym owners can configure gym profile (name, logo, description, photos, location)
- **FR9:** Gym owners can set operating hours and holiday closures
- **FR10:** Gym owners can configure cancellation policies and booking rules
- **FR11:** Gym owners can enable/disable marketplace participation for their gym
- **FR12:** Gym owners can view and manage their SaaS subscription tier
- **FR13:** Gym owners can import existing member data from spreadsheets

### Consumer Profile & Membership

- **FR14:** Consumers can link to multiple gyms from a single profile
- **FR15:** Consumers can view all their gym memberships in one place
- **FR16:** Consumers can manage payment methods for each membership
- **FR17:** Consumers can upgrade or downgrade their membership tier
- **FR18:** Consumers can view membership benefits and usage limits
- **FR19:** Consumers can accept digital waivers required by gyms
- **FR20:** Gyms can view their members and membership statuses

### Staff Management

- **FR21:** Gym owners can add staff members and assign roles (Manager, Front Desk, Instructor)
- **FR22:** Gym owners can configure permissions per role
- **FR23:** Gym owners can manage staff working hours and shifts
- **FR24:** Gym owners can set instructor pay rates per class
- **FR25:** Instructors can view their scheduled classes and earnings
- **FR26:** Staff can access features appropriate to their assigned role

### Space & Facility Management

- **FR27:** Gym owners can create and manage spaces (rooms, studios, areas)
- **FR28:** Gym owners can set capacity limits per space
- **FR29:** Gym owners can define amenities and equipment per space
- **FR30:** System prevents double-booking of spaces

### Class Scheduling

- **FR31:** Gym staff can create class templates with recurring schedules
- **FR32:** Gym staff can schedule individual class sessions
- **FR33:** Gym staff can assign instructors to classes
- **FR34:** Gym staff can assign spaces to classes
- **FR35:** Classes can require approval before becoming visible (configurable workflow)
- **FR36:** Gym staff can cancel classes and notify affected members
- **FR37:** Gym staff can set class capacity and waitlist limits
- **FR38:** Gym owners can set marketplace pricing for classes

### Booking & Check-in

- **FR39:** Consumers can book classes (direct membership or marketplace)
- **FR40:** Consumers can cancel bookings subject to gym cancellation policy
- **FR41:** Consumers can join waitlists for full classes
- **FR42:** System automatically offers waitlist spots when availability opens
- **FR43:** Consumers have a time window to confirm waitlist offers
- **FR44:** Consumers can display QR code for gym check-in
- **FR45:** Staff can scan QR codes to check in members
- **FR46:** Staff can search and check in members by phone or name (fallback)
- **FR47:** System validates membership status during check-in
- **FR48:** System tracks booking source (direct vs marketplace) for each booking

### Marketplace & Discovery

- **FR49:** Consumers can browse classes from all marketplace-enabled gyms
- **FR50:** Consumers can filter classes by type, location, date/time, price, and availability
- **FR51:** Consumers can view gym profiles and class details before booking
- **FR52:** Consumers can subscribe to marketplace class packages (8/12/unlimited)
- **FR53:** Consumers can book individual classes without subscription (pay-per-class)
- **FR54:** System tracks marketplace class credits and usage
- **FR55:** Consumers can share class details with others
- **FR56:** Consumers can invite friends via referral links

### Payments & Billing

- **FR57:** System supports abstracted payment interface for future gateway integration
- **FR58:** Gyms can view pending and completed payments
- **FR59:** System detects and flags failed payments
- **FR60:** System supports automatic payment retry
- **FR61:** Gyms can view marketplace booking revenue and payout reports
- **FR62:** Consumers can view their payment history

### Notifications & Communication

- **FR63:** System sends booking confirmations via push and email
- **FR64:** System sends class reminders before scheduled classes
- **FR65:** System sends waitlist notifications when spots become available
- **FR66:** System sends payment reminders and failure alerts
- **FR67:** Gym staff can send messages to individual members or groups
- **FR68:** System supports WhatsApp for critical/emergency notifications
- **FR69:** Consumers can configure notification preferences

### Reporting & Analytics

- **FR70:** Gym owners can view revenue reports (membership + marketplace)
- **FR71:** Gym owners can view attendance and check-in reports
- **FR72:** Gym owners can view membership health reports (active, at-risk, churned)
- **FR73:** Gym owners can view class performance reports (fill rate, attendance)
- **FR74:** Gym owners can view staff performance reports
- **FR75:** Consumers can view their class history and statistics
- **FR76:** System flags at-risk members based on engagement patterns

### Platform Administration

- **FR77:** Platform admins can review and approve new gym applications
- **FR78:** Platform admins can view and manage all gyms on the platform
- **FR79:** Platform admins can view and manage consumer complaints
- **FR80:** Platform admins can issue credits to consumer accounts
- **FR81:** Platform admins can monitor platform health metrics
- **FR82:** Platform admins can access gym-level data for support purposes

### Real-time & Integration

- **FR83:** System provides real-time class availability updates
- **FR84:** System supports webhook events for gym integrations
- **FR85:** QR code display (consumer) and QR scanner (gym mobile) function offline and sync when connectivity restored

---

## Non-Functional Requirements

### Performance

| Requirement | Target | Context |
|-------------|--------|---------|
| **NFR1:** API response time | <200ms p95 | Core CRUD operations |
| **NFR2:** Class availability updates | <1s latency | WebSocket real-time |
| **NFR3:** QR code scan to confirmation | <2s | Gym entry experience |
| **NFR4:** Class browse/filter response | <500ms | Consumer discovery |
| **NFR5:** Mobile app cold start | <3s | First screen visible |
| **NFR6:** Image/asset loading | Lazy load, <1MB initial bundle | SA mobile data constraints |

### Security

| Requirement | Target | Context |
|-------------|--------|---------|
| **NFR7:** Data encryption at rest | AES-256 | All PII and sensitive data |
| **NFR8:** Data encryption in transit | TLS 1.2+ | All API communications |
| **NFR9:** Multi-tenant data isolation | Zero cross-tenant data leakage | Gym A never sees Gym B data |
| **NFR10:** Authentication tokens | JWT with <24h expiry, refresh rotation | Session management |
| **NFR11:** Password storage | bcrypt/argon2, minimum 12 rounds | No plaintext passwords |
| **NFR12:** API rate limiting | Per-user/per-gym limits | Prevent abuse/scraping |
| **NFR13:** POPIA compliance | Data export, deletion within 30 days | Consumer rights |
| **NFR14:** Audit logging | All admin actions, data access logged | Compliance, debugging |

### Scalability

| Requirement | Target | Context |
|-------------|--------|---------|
| **NFR15:** Concurrent users | Support 5,000+ simultaneous | Phase 2 growth |
| **NFR16:** WebSocket connections | 10,000 concurrent connections | Real-time class updates |
| **NFR17:** Database scaling | Horizontal read replicas | Report queries don't impact ops |
| **NFR18:** Booking throughput | 100 bookings/minute peak | Popular class release times |
| **NFR19:** Growth handling | 10x user growth with <10% performance degradation | Phase 2→3 transition |

### Reliability

| Requirement | Target | Context |
|-------------|--------|---------|
| **NFR20:** System uptime | 99.5% (22 hours downtime/month max) | Gyms depend daily |
| **NFR21:** Data durability | 99.99% (no data loss) | Member and booking data |
| **NFR22:** Offline QR functionality | Check-in works without connectivity | SA network reliability |
| **NFR23:** Graceful degradation | Core features work if secondary services fail | Notifications down ≠ bookings down |
| **NFR24:** Backup frequency | Daily backups, 30-day retention | Disaster recovery |
| **NFR25:** Recovery time objective | <4 hours from major failure | Business continuity |

### Accessibility

| Requirement | Target | Context |
|-------------|--------|---------|
| **NFR26:** Color contrast | WCAG 2.1 AA minimum | Readable in bright gym environments |
| **NFR27:** Touch targets | Minimum 44x44px | Mobile usability |
| **NFR28:** Screen reader support | Core flows navigable | VoiceOver/TalkBack |
| **NFR29:** Text scaling | Support up to 200% | Accessibility settings |

### Integration

| Requirement | Target | Context |
|-------------|--------|---------|
| **NFR30:** Email delivery | 99% within 5 minutes | Transactional notifications |
| **NFR31:** Push notification delivery | 95% within 30 seconds | Time-sensitive alerts |
| **NFR32:** WhatsApp API reliability | Fallback to email if unavailable | Critical notifications |
| **NFR33:** Webhook delivery | At-least-once with retry (3 attempts) | Gym integrations |
| **NFR34:** Payment interface | Abstracted, provider-swappable | PayFast/Peach flexibility |

### Data & Compliance

| Requirement | Target | Context |
|-------------|--------|---------|
| **NFR35:** Data residency | SA-based or POPIA-compliant hosting | Consumer PII |
| **NFR36:** Data retention | Configurable per data type | Compliance flexibility |
| **NFR37:** Consent tracking | Record all consumer consents with timestamps | POPIA audit trail |
| **NFR38:** Data export | Consumer data exportable within 48 hours | POPIA right of access |
