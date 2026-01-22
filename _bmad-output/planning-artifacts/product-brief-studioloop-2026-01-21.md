---
stepsCompleted: [1, 2, 3, 4, 5, 6]
status: complete
completedAt: 2026-01-21
inputDocuments:
  - brainstorming-session-2026-01-21.md
  - api-brainstorm.md
  - gym-management-app-brainstorm.md
  - consumer-app-brainstorm.md
date: 2026-01-21
author: Ameen
---

# Product Brief: StudioLoop

## Executive Summary

**StudioLoop** is a fitness marketplace and gym management platform targeting Cape Town, South Africa - a market underserved by international solutions like ClassPass.

The platform operates on a "trojan horse" strategy: affordable gym management software (replacing expensive international tools or spreadsheets) gets gyms onto the platform and forces their members to download the StudioLoop consumer app. Once installed, consumers are exposed to the class marketplace - driving cross-gym bookings and platform revenue.

Unlike ClassPass, which has burned goodwill with gym partners through declining payouts and poor support, StudioLoop is designed to be **gym-friendly first**. By solving gyms' operational pain points with affordable SaaS, we earn their trust before asking them to participate in the marketplace.

**Revenue Model:**
- Low-cost monthly SaaS fees from gyms
- Commission on marketplace bookings
- Consumer subscriptions (flat class count per month)
- Pay-per-class bookings

**Target Market:**
- 426+ gyms in Western Cape, 86.93% single-owner operations
- Fitness consumers seeking variety and discounts
- Initial focus: Cape Town boutique and independent gyms

---

## Core Vision

### Problem Statement

**For Gyms:**
Small and independent gyms in Cape Town lack affordable, modern management tools. International solutions (Mindbody, GymMaster) are expensive and over-featured. Most resort to spreadsheets, WhatsApp groups, and manual processes - leading to:
- Missed payments and revenue leakage
- Administrative overload (owners spend 40% of time on admin)
- No visibility into member engagement or churn risk
- 50% member churn rate in year one

**For Consumers:**
Fitness enthusiasts in Cape Town lack a ClassPass-like option to:
- Try different gyms and class types without multiple memberships
- Access discounted off-peak classes
- Manage multiple gym memberships in one place

### Problem Impact

**Gyms suffer from:**
- Revenue leakage from manual payment tracking
- High churn they can't predict or prevent
- Inability to fill off-peak class slots
- Time wasted on admin instead of member experience

**Consumers suffer from:**
- Commitment anxiety (locked into single-gym memberships)
- No way to try before committing
- Managing multiple apps/accounts for different gyms
- Missing out on empty class slots they'd attend if priced right

### Why Existing Solutions Fall Short

| Solution | Gap |
|----------|-----|
| **ClassPass** | Not available in SA; burns gym relationships with low payouts (~40% of class value); poor partner support |
| **Mindbody** | Expensive for small gyms; complex; not localized for SA payment systems |
| **GymMaster** | International pricing; overkill for small operations |
| **Spreadsheets** | No automation; error-prone; no member-facing experience |

**Key Insight:** ClassPass alienated gym partners by prioritizing consumer growth over partner profitability. StudioLoop can win by being gym-friendly first.

### Proposed Solution

**A six-application platform:**

1. **Gym Management Web App (B2B SaaS)** — `manage.studioloop.co.za`
   - Affordable alternative to international solutions
   - Full dashboard, reports, member management, settings
   - Desktop-optimized for detailed operations
   - Development Priority: **1st**

2. **Consumer Web App (B2C)** — `app.studioloop.co.za`
   - Class browsing, booking, membership management
   - QR code display for gym check-in
   - Development Priority: **2nd**

3. **Consumer Mobile App (B2C)** — iOS + Android
   - On-the-go booking, QR code display for check-in
   - Push notifications for reminders
   - Development Priority: **3rd**

4. **Gym Management Mobile App (B2B)** — iOS + Android
   - QR scanner for member check-in (mobile-only feature)
   - Quick dashboard access, schedule view
   - Development Priority: **4th**

5. **Class Marketplace** (integrated across consumer apps)
   - Aggregates discounted off-peak classes across gyms
   - Flat-count subscriptions (e.g., 8 classes/month anywhere)
   - Pay-per-class option for non-subscribers
   - Fills empty gym slots with incremental revenue

6. **Shared Backend API** — `api.studioloop.co.za`
   - FastAPI backend serving all client applications
   - Multi-tenant architecture with gym data isolation

### Key Differentiators

| Differentiator | Description |
|----------------|-------------|
| **Gym-First Approach** | Unlike ClassPass, we solve gym problems first, earning trust before marketplace participation |
| **Local Focus** | Built for SA market, SA payment systems, SA pricing expectations |
| **Affordable SaaS** | Lower than international competitors, accessible to single-owner gyms |
| **Better Partner Economics** | Higher gym payouts than ClassPass's ~40% model |
| **Forced App Adoption** | Gym management software requires member app usage, building consumer base organically |
| **Dual Revenue Stream** | SaaS fees provide baseline; marketplace provides upside |

---

## Target Users

### Primary Users

#### 1. Gym Owner - "Thabo"

**Profile:**
- 38-year-old owner of a 120-member boutique gym in Woodstock, Cape Town
- Former personal trainer who opened his own gym 3 years ago
- Manages everything himself with one part-time receptionist

**Current Situation:**
- Uses Google Sheets to track members and payments
- WhatsApp groups for class announcements
- Spends 15+ hours/week on admin instead of training clients
- Loses ~R8,000/month from missed payments he doesn't catch in time
- 45% of new members churn within 6 months

**Pain Points:**
- "I became a trainer to help people get fit, not to chase payments"
- No visibility into which members are at risk of leaving
- Can't afford Mindbody (R2,500+/month) for his small operation
- Classes at 2pm and 3pm are always half-empty

**Success Vision:**
- Automated payment collection that just works
- Dashboard showing who needs attention before they quit
- Fill empty class slots with paying customers
- Spend time training, not doing admin

**Why StudioLoop:**
- Affordable SaaS solves his immediate pain
- Marketplace fills his off-peak classes with new revenue
- Doesn't have to become a tech expert

---

#### 2. Fitness Consumer - "Lerato"

**Profile:**
- 29-year-old marketing professional living in Sea Point
- Loves variety - yoga one day, spinning the next, boxing on weekends
- Currently has a Virgin Active membership but wants to try boutique studios

**Current Situation:**
- Pays R899/month for Virgin Active but only goes 2x/week
- Tried a boutique yoga studio but didn't want another R600/month commitment
- Friends rave about different studios but she can't try them all
- Wishes ClassPass existed in Cape Town

**Pain Points:**
- "I don't want 5 different gym memberships to try different things"
- Can't justify boutique prices for occasional visits
- FOMO on great classes at studios she doesn't belong to
- Managing multiple apps and payment methods is a nightmare

**Success Vision:**
- One app to book classes anywhere in Cape Town
- Try boutique studios without long-term commitment
- Affordable way to mix up her fitness routine
- Discover new favorite gyms and instructors

**Why StudioLoop:**
- Flat subscription for classes at any gym
- Pay-per-class option for occasional visits
- One app to manage everything
- Discounted off-peak classes fit her flexible schedule

---

#### 3. Gym Staff - "Nomsa"

**Profile:**
- 24-year-old front desk manager at a CrossFit box in Observatory
- Also teaches 3 classes per week
- First job out of university, tech-savvy

**Current Situation:**
- Checks members in manually on a paper list
- Texts the owner screenshots of who attended each class
- Tracks her own class schedule in her phone calendar
- Calculates her monthly pay manually from class count

**Pain Points:**
- "I never know if someone's membership is actually paid up"
- Awkward confrontations when she has to ask about payment
- Can't see her schedule or earnings in one place
- Paper check-in lists get lost or damaged

**Success Vision:**
- Scan QR code → instant check-in, no questions
- See her class schedule and earnings at a glance
- No more awkward payment conversations
- Know exactly who's coming to her classes

**Why StudioLoop:**
- QR scanner (mobile) + manual check-in (web) eliminates awkward moments
- Clear view of her schedule and pay
- Attendance tracked automatically
- Professional system makes her job easier

---

### Secondary Users

#### 4. Gym Member (Non-Marketplace) - "David"

**Profile:**
- 52-year-old accountant, member at his local gym for 5 years
- Not interested in trying other gyms
- Just wants to manage his membership easily

**Interaction:**
- Downloads app because his gym requires it
- Uses QR code for check-in
- Manages payment method and membership in app
- May discover marketplace later but not primary motivation

---

### User Journeys

#### Gym Owner Journey (Thabo)

| Stage | Experience |
|-------|------------|
| **Discovery** | Hears about StudioLoop from another gym owner, or sees targeted Facebook ad about "affordable gym software" |
| **Evaluation** | Signs up for free trial, impressed by how much simpler it is than spreadsheets |
| **Onboarding** | Imports member list, sets up membership tiers, configures class schedule |
| **Aha Moment** | First month: catches 3 failed payments automatically that he would have missed |
| **Value Realization** | Sees dashboard showing "at risk" members, reaches out before they cancel |
| **Marketplace** | Enables off-peak classes on marketplace, fills 2pm slots with new paying customers |
| **Advocacy** | Tells other gym owners about the system |

#### Consumer Journey (Lerato)

| Stage | Experience |
|-------|------------|
| **Discovery** | Joins a boutique gym, required to download StudioLoop app for membership |
| **First Use** | Uses app to manage her gym membership, check-in with QR |
| **Aha Moment** | Sees "Discover Classes" tab, realizes she can book at other gyms |
| **Exploration** | Tries a discounted yoga class at a studio she'd been curious about |
| **Subscription** | Signs up for 8-class/month subscription after trying 3 different studios |
| **Habit** | Becomes her go-to for mixing up her routine - yoga Monday, spin Wednesday, boxing Saturday |
| **Advocacy** | Shares classes with friends, invites them to join her |

---

## Success Metrics

### User Success Metrics

#### Gym Owner Success (Thabo)
| Metric | What It Measures | Target |
|--------|------------------|--------|
| **Admin Time Saved** | Hours/week spent on admin tasks | Reduce from 15hrs to <5hrs |
| **Payment Collection Rate** | % of memberships paid on time | >95% (vs ~85% manual) |
| **Churn Prediction Accuracy** | At-risk members flagged before cancelling | Catch 70% before they leave |
| **Off-Peak Fill Rate** | % of marketplace-listed slots booked | >40% of empty slots filled |
| **Revenue Recovered** | Previously missed payments now collected | R5,000+/month per gym |

**Aha Moment:** First automatically caught failed payment within 30 days of onboarding.

#### Consumer Success (Lerato)
| Metric | What It Measures | Target |
|--------|------------------|--------|
| **Class Variety** | Unique gyms visited per month | 3+ different gyms |
| **Booking Completion** | Bookings made → attended | >85% attendance rate |
| **Discovery Rate** | Non-member trying marketplace classes | 30% of app users try marketplace |
| **Subscription Value** | Classes used vs subscription cost | >80% credit utilization |

**Aha Moment:** First marketplace class booked within 14 days of app install.

#### Staff Success (Nomsa)
| Metric | What It Measures | Target |
|--------|------------------|--------|
| **Check-in Time** | Seconds to check in a member | <5 seconds (vs 30+ manual) |
| **Schedule Visibility** | Can see full schedule in app | 100% of shifts visible |
| **Earnings Clarity** | Real-time view of class pay | Always current |

---

### Business Objectives

#### Phase 1: Prove the Model (Months 1-6)
| Objective | Target | Rationale |
|-----------|--------|-----------|
| **Gyms Onboarded** | 20 gyms in Cape Town | Validate SaaS value prop |
| **Consumer App Downloads** | 2,000 users | Build initial user base |
| **Marketplace Activation** | 10% of users book marketplace class | Prove marketplace demand |
| **Gym Retention** | 90% at 3 months | Validate sticky product |

#### Phase 2: Scale (Months 6-12)
| Objective | Target | Rationale |
|-----------|--------|-----------|
| **Gyms Onboarded** | 50 gyms | Expand supply |
| **Consumer App Downloads** | 10,000 users | Network effects kick in |
| **Marketplace Subscriptions** | 500 active subscribers | Prove subscription model |
| **Monthly Revenue** | R150,000 MRR | Path to sustainability |

#### Phase 3: Dominate Cape Town (Year 2)
| Objective | Target | Rationale |
|-----------|--------|-----------|
| **Gyms Onboarded** | 150+ gyms (35% of market) | Market leadership |
| **Consumer App Downloads** | 50,000 users | Household name in CT fitness |
| **Marketplace GMV** | R1M/month in bookings | Significant revenue stream |

---

### Key Performance Indicators

#### Gym-Side KPIs
| KPI | Definition | Target | Frequency |
|-----|------------|--------|-----------|
| **Gym Activation Rate** | % of signed gyms actively using after 30 days | >80% | Monthly |
| **Gym Net Revenue Retention** | Revenue from existing gyms YoY | >110% | Quarterly |
| **Gym NPS** | Net Promoter Score from gym owners | >50 | Quarterly |
| **Support Ticket Volume** | Tickets per gym per month | <2 | Monthly |

#### Consumer-Side KPIs
| KPI | Definition | Target | Frequency |
|-----|------------|--------|-----------|
| **Day 7 Retention** | % of users active 7 days after install | >40% | Weekly |
| **Day 30 Retention** | % of users active 30 days after install | >25% (beats 8-12% avg) | Monthly |
| **Marketplace Conversion** | % of app users who book marketplace class | >15% | Monthly |
| **Subscription Conversion** | % of marketplace users who subscribe | >20% | Monthly |
| **Monthly Active Users (MAU)** | Unique users with activity | Track growth | Monthly |

#### Financial KPIs
| KPI | Definition | Target | Frequency |
|-----|------------|--------|-----------|
| **Monthly Recurring Revenue (MRR)** | SaaS fees + active subscriptions | Track growth | Monthly |
| **Gross Merchandise Value (GMV)** | Total marketplace booking value | Track growth | Monthly |
| **Take Rate** | Commission revenue / GMV | 15-20% | Monthly |
| **Customer Acquisition Cost (CAC)** | Marketing spend / new customers | <R150/gym, <R25/consumer | Monthly |
| **Lifetime Value (LTV)** | Revenue per customer over lifetime | LTV:CAC > 3:1 | Quarterly |

#### Leading Indicators (Early Warning)
| Indicator | What It Predicts | Action Trigger |
|-----------|------------------|----------------|
| **Gym login frequency drop** | Churn risk | <3 logins/week |
| **Consumer booking decline** | Subscription cancellation | <2 bookings in 30 days |
| **Class fill rate drop** | Supply/demand mismatch | <30% avg fill rate |
| **Support ticket spike** | Product/UX issues | >50% increase week-over-week |

---

## MVP Scope

### Core Features (Must Have)

#### API Layer
| Feature | Description | Rationale |
|---------|-------------|-----------|
| **Multi-tenant Architecture** | Single API serving all gyms with shared consumer profiles | Foundation for everything |
| **Authentication** | Email, social login, phone OTP for all user types | Essential for access |
| **Gym Management** | CRUD for gyms, staff, spaces, settings | Core SaaS value |
| **Membership Management** | Custom tiers, benefits, rules, payment tracking | Primary gym pain point |
| **Class Scheduling** | Class templates, sessions, space booking, approval workflow | Core functionality |
| **Booking System** | Consumer bookings with source tracking (direct vs marketplace) | Revenue attribution |
| **Waitlist** | Join, auto-fill with timed confirmation | User experience |
| **Real-time (WebSocket)** | Live class availability, booking confirmations | Prevents frustration |
| **Webhooks** | Events for gym integrations | Extensibility |
| **Notifications** | Email, push, WhatsApp triggers | Engagement |
| **Reports** | Revenue, membership, attendance, staff | Gym visibility |

#### Gym Management (Web + Mobile)

**Gym Web** (`manage.studioloop.co.za`) — Priority 1:
| Feature | Description | Rationale |
|---------|-------------|-----------|
| **Action-First Dashboard** | Tasks needing attention + key metrics | Immediate value |
| **Manual Check-in** | Search member by phone/name, verify status | Fallback when no scanner |
| **Space Management** | Rooms with capacity, equipment, amenities | Class scheduling foundation |
| **Class Scheduling** | Create sessions, require space, approval workflow | Core functionality |
| **Membership Tiers** | Fully customizable benefits and rules | Flexibility gyms need |
| **Staff Management** | Roles, permissions, hours, instructor pay | Operational control |
| **Reporting Suite** | All reports (revenue, attendance, churn, etc.) | Business intelligence |
| **Communication** | In-app, email, WhatsApp messaging | Member engagement |
| **Gym Profile** | Branding, hours, policies, marketplace listing | Identity + marketplace |

**Gym Mobile** (iOS + Android) — Priority 4:
| Feature | Description | Rationale |
|---------|-------------|-----------|
| **QR Scanner Check-in** | Scan member QR codes (mobile-only) | Fast on-floor check-in |
| **Quick Dashboard** | Today's metrics and urgent items | At-a-glance info |
| **Schedule View** | Today's classes and attendance | Quick reference |
| **Reports** | Full reports accessible on mobile | Review on-the-go |

#### Consumer (Web + Mobile)

**Consumer Web** (`app.studioloop.co.za`) — Priority 2:
| Feature | Description | Rationale |
|---------|-------------|-----------|
| **Home Screen** | Bookings list, overdue banner | Daily utility |
| **Browse Classes** | List-first discovery with all filters | Marketplace core |
| **Class Detail + Booking** | Full info, subscription or pay-per-class | Conversion |
| **My Memberships** | Gym memberships + marketplace subscription management | Account control |
| **Profile & Settings** | Personal details, notifications, payment methods, favorites | Personalization |
| **QR Code Display** | Show QR for gym check-in | Web access to check-in |
| **Class History + Stats** | Past classes, totals, rebook | Retention |
| **Waitlist** | Join, notification, 30-min confirmation | Full booking flow |
| **Share/Invite** | Class details + referral link | Growth |

**Consumer Mobile** (iOS + Android) — Priority 3:
| Feature | Description | Rationale |
|---------|-------------|-----------|
| All Consumer Web features | Same functionality as web | Feature parity |
| **Push Notifications** | Booking reminders, waitlist alerts | Mobile-native engagement |
| **Offline QR Display** | QR code works without network | Reliable check-in |

#### Marketplace
| Feature | Description | Rationale |
|---------|-------------|-----------|
| **Flat-Count Subscriptions** | X classes/month at any gym | Simple pricing |
| **Pay-Per-Class** | One-off bookings without subscription | Low barrier |
| **Cross-Gym Discovery** | Search any gym's marketplace classes | Core value prop |
| **Gym Payouts** | Track marketplace bookings for settlement | Business model |

---

### Out of Scope for MVP

| Feature | Rationale | When to Add |
|---------|-----------|-------------|
| **Payment Gateway Integration** | Interface ready, implementation deferred until payment research complete | Before public launch |
| **Equipment Tracking** | Nice-to-have, not core to value prop | V2 |
| **Rating/Review System** | Collecting data in background, UI deferred until system designed | V2 |
| **SMS Notifications** | Cost vs WhatsApp popularity in SA | V2 if needed |
| **Social Features** | Find friends, follow, etc. | V2 |
| **Personalized Recommendations** | "Classes you might like" | V2 with usage data |
| **Achievements/Gamification** | Streaks, badges, challenges | V2 |
| **Multi-Location Gym Support** | Single-location gyms are target | When chains request |
| **POS for Merchandise** | Outside core value | Future |
| **Corporate Wellness Portal** | B2B2C channel | Phase 3 |

---

### MVP Success Criteria

**Go/No-Go Decision Point:** End of Month 6

| Criteria | Target | Validates |
|----------|--------|-----------|
| **Gyms Active** | 15+ gyms using daily | SaaS product-market fit |
| **Gym Retention** | 85%+ at 3 months | Sticky product |
| **Consumer Downloads** | 1,500+ users | Distribution via gyms works |
| **Marketplace Trials** | 10%+ of users try a marketplace class | Marketplace demand exists |
| **Gym Owner NPS** | >40 | Value creation |
| **Revenue** | R30,000+ MRR | Business viability |

**If criteria met:** Proceed to Phase 2 (scale)
**If not met:** Pivot or refine based on learnings

---

### Future Vision

#### V2 Enhancements (Post-MVP)
- Payment gateway integration (PayFast, Peach)
- Rating and review system
- Personalized class recommendations
- Equipment tracking for gyms
- Enhanced analytics and insights

#### V3 Expansion (Year 2)
- Expand beyond Cape Town (Johannesburg, Durban)
- Corporate wellness partnerships
- Personal trainer marketplace
- Nutrition and wellness add-ons
- Multi-location gym support

#### Long-Term Vision (Year 3+)
- Become the "super app" for fitness in South Africa
- Expand to other African markets
- Platform ecosystem (integrations, API partners)
- Wellness beyond fitness (spa, beauty, recovery)
