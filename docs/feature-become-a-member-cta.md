# Feature Plan: "Become a Member" CTA (Explore → Studio Membership)

**Status:** Planned  
**Priority:** P1 — enables organic membership conversion from marketplace  
**Author:** Nick Fury  
**Date:** 2026-03-10  

---

## Overview

Add a **"Become a Member"** flow to the Explore/Discover tab that allows marketplace-only users (those without an existing studio membership) to browse a studio's membership plans and enroll directly through the app.

This closes the loop on the flywheel: user discovers a studio via tokens → loves it → converts to a paying studio member without leaving the app.

---

## User Stories

1. As a token user browsing Explore, I can view a studio's membership plans on their profile
2. As a token user, I can enroll in a studio membership plan from the Explore tab
3. As an existing studio member viewing Explore, I can see that I already have a membership at a studio (no duplicate enroll CTA)
4. As a new member, after enrolling, the studio appears in my Home (My Studio) tab
5. As a studio, my membership plans are visible to all StudioLoop users in my public profile

---

## Screens / Changes

### 1. Studio Profile Page (already exists via `GymProfileResponse`)
**Add new section: "Memberships"**
- List of active membership plans from `GET /gyms/{gym_slug}/membership-plans`
- Each plan card shows: name, price, billing cycle, tier (Basic/Premium/Unlimited), key benefits
- CTA button: **"Become a Member"** (if user has no active membership at this gym)
- If user already has a membership: show **"You're a member ✓"** badge (no CTA)

### 2. Membership Plan Detail Sheet (bottom sheet)
Triggered by tapping a plan card or "Become a Member" button.

**Shows:**
- Plan name, price, billing cycle
- Full benefits list
- Usage limits (classes/week, guest access, etc.)
- Waiver text (if required — must be accepted before enrolling)
- **"Enroll — R[price]/month"** confirm button

### 3. Waiver Acceptance Screen (if `waiver_text` is set on the plan)
- Displays the studio's waiver/T&Cs
- Checkbox: "I agree to the terms"
- "Continue to Payment" CTA
- On acceptance: calls `POST /consumer/memberships/waiver_acceptance`

### 4. Payment Screen
- Shows: plan name, price, billing cycle
- Payment method: Stitch/card
- On success: membership created, user redirected to Home tab (My Studio now shows the new studio)

### 5. Enrollment Success State
- Confirmation screen: "You're now a member of [Studio Name]! 🎉"
- "Go to My Studio" CTA → navigates to Home tab
- "Keep Exploring" CTA → back to Discover

---

## Where the CTA Surfaces

| Location | CTA | Condition |
|---|---|---|
| Studio Profile (Explore) | "Become a Member" | No active membership at this gym |
| Class Detail page | "Join [Studio] to book regularly" | No membership, after token booking |
| Post-booking confirmation | "Love this studio? Become a member" | First time booking at a studio |
| Studio Profile (Explore) | "You're a member ✓" badge | Active membership exists |

---

## API Endpoints (all exist — frontend only)

| Endpoint | Purpose |
|---|---|
| `GET /gyms/{gym_slug}/membership-plans` | List public plans for a studio |
| `POST /consumer/memberships` | Enroll in a plan |
| `GET /consumer/memberships` | Check if user already has membership at gym |
| `POST /consumer/memberships/waiver_acceptance` | Accept digital waiver |

---

## Logic: Already a Member Check

Before showing the "Become a Member" CTA on any studio page:
1. Fetch `GET /consumer/memberships`
2. Check if any returned membership has `gym_id` matching the current studio and `status == "active"`
3. If yes → show "You're a member ✓"
4. If no → show "Become a Member" CTA

This should be cached per session to avoid repeated calls.

---

## Implementation Scope

### Consumer Mobile (React Native / Expo)
- Update `app/class/[id].tsx` — add studio membership CTA section
- Update marketplace gym profile screen (if it exists) or create `app/studio/[slug].tsx`
- New screens:
  - `app/studio/membership-plans.tsx` — plan list
  - `app/studio/membership-enroll.tsx` — plan detail + enroll flow
  - `app/studio/waiver.tsx` — waiver acceptance
  - `app/studio/membership-success.tsx` — success state

### Consumer Web (React / Vite)
- Update `routes/discover/ClassDetail.tsx` — add membership CTA
- New route: `routes/discover/StudioProfile.tsx` — studio public profile with memberships
- New route: `routes/discover/MembershipEnroll.tsx` — enrollment flow

### Shared
- New API client methods (generated from OpenAPI spec via hey-api):
  - `getPublicMembershipPlans(gymSlug)`
  - `enrollMembership(gymId, planId, paymentMethod)`
  - `acceptWaiver(membershipId, waiverText)`
- Shared UI: `MembershipPlanCard` component in `packages/ui`

---

## Edge Cases to Handle

| Scenario | Handling |
|---|---|
| User already has active membership | Show "Member" badge, hide enroll CTA |
| Plan has no waiver | Skip waiver screen, go straight to payment |
| Plan is free (R0) | Skip payment screen, enroll immediately |
| Payment fails | Show error, stay on payment screen, retry |
| Gym has no active plans | Hide "Become a Member" section entirely |
| User cancels mid-flow | No membership created, return to studio profile |

---

## Acceptance Criteria

- [ ] Studio profile in Explore shows active membership plans
- [ ] "Become a Member" CTA visible when user has no active membership at that gym
- [ ] "You're a member ✓" badge shown when user already has a membership
- [ ] Tapping a plan opens the plan detail sheet with full benefits and pricing
- [ ] Waiver acceptance screen shown if studio has waiver text set
- [ ] Successful enrollment creates a `GymMembership` record and redirects user to Home tab
- [ ] Enrolled studio appears in Home (My Studio) tab after enrollment
- [ ] Post-booking CTA ("Love this studio? Become a member") visible after first token booking
- [ ] Works on both consumer-mobile and consumer-web

---

## Dependencies

- Studio profile screen must exist or be created in consumer-mobile Explore tab
- Payment integration (Stitch) must handle recurring billing for membership plans
- Gym must have at least one active membership plan configured (via gym-web dashboard)

---

## Estimated Effort

| Area | Estimate |
|---|---|
| Consumer mobile (enroll flow + screens) | 2-3 days |
| Consumer web (studio profile + enroll flow) | 1-2 days |
| Shared UI components | 0.5 day |
| **Total** | **~4-5 days** |
