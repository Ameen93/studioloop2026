# StudioLoop Gym Management App Specification (Brainstorm)

> Generated from brainstorming session - 2026-01-21

---

## Overview

The Gym Management App is a SaaS solution for Cape Town gyms to replace manual spreadsheet-based operations. It serves as the "hook" to get gyms onto the StudioLoop platform, which in turn forces consumers to download the consumer app - exposing them to the class marketplace.

**Strategic Purpose:**
1. Solve gym's operational pain points (free/cheap software)
2. Require members to use StudioLoop consumer app
3. Build marketplace supply (gyms) and demand (consumers with app installed)

---

## User Roles

| Role | Description | Access Level |
|------|-------------|--------------|
| **Owner** | Gym owner, full access | Everything |
| **Manager** | Day-to-day operations | Most features, limited billing/settings |
| **Front Desk** | Member-facing staff | Check-ins, bookings, basic member lookup |
| **Instructor** | Class teachers | Own schedule, class attendance, create classes (requires approval) |

---

## Core Features by Role

### Owner Dashboard (Action-First Design)

The dashboard surfaces what needs attention immediately, with summary metrics below.

**Action Items (Top of Dashboard):**
- Failed payments needing follow-up
- Members flagged as at-risk (low attendance pattern)
- Classes below minimum attendance threshold
- Expiring memberships this week
- Staff schedule conflicts

**Summary Metrics (Below Actions):**
- Today's revenue
- Active member count
- Today's check-ins
- Class fill rates
- Upcoming payments due

---

### Front Desk Features

**Primary Functions:**
1. Member check-in
2. Walk-in sign-ups
3. Class bookings for members
4. Payment collection
5. Member inquiries

**Check-In System:**

| Method | Type | Description |
|--------|------|-------------|
| QR Code Scan | Primary | Member shows QR code in their app, front desk scans |
| Phone Lookup | Fallback | Search by phone number |
| Name Search | Fallback | Search by member name |

**Walk-In Flow:**
1. Collect member details
2. Select membership tier or day pass
3. Process payment
4. Member downloads app and creates account
5. Membership linked to account

---

### Instructor Features

**View & Manage:**
- Assigned class schedule (calendar view)
- Attendee list per class
- Attendance auto-tracked via QR check-in (no manual marking)
- No-shows auto-flagged (booked but no QR scan)

**Class Creation (Requires Approval):**
- Instructor can propose new class sessions
- Requires manager/owner approval before going live
- Alternatively, admin creates class and instructor approves

**Earnings:**
- View classes taught
- View earnings based on pay rate per class

---

## Spaces Management

Spaces are physical rooms/studios within the gym. Every class must book a space.

**Space Attributes:**

| Field | Description |
|-------|-------------|
| Name | e.g., "Yoga Studio A", "Spin Room", "Main Floor" |
| Capacity | Maximum people allowed |
| Equipment | Available equipment (mats, bikes, weights, TRX, etc.) |
| Amenities | Features (mirrors, sound system, AC, natural light, etc.) |

**Scheduling Logic:**
- Classes require a space for their time slot
- System prevents double-booking (no two classes in same space at same time)
- When scheduling a class:
  - System auto-suggests available spaces based on class type and required capacity
  - Staff can manually override suggestion

---

## Class Scheduling

**Class Creation Flow:**

1. Select class type (yoga, spin, boxing, etc.)
2. Choose date and time
3. System suggests available spaces
4. Select or override space
5. Assign instructor
6. Set capacity (defaults from space, can be lower)
7. Set pricing:
   - Direct booking price
   - Marketplace price (if enabling marketplace listing)
8. Submit for approval (if created by instructor)
9. Goes live once approved

**Approval Workflow:**
- If **Instructor** creates → Owner/Manager approves
- If **Owner/Manager** creates → Instructor confirms availability

**Recurring Classes:**
- Support for creating recurring sessions (weekly, daily)
- Bulk create with single approval
- Individual sessions can be modified/cancelled

---

## Membership Management

Gyms can create fully custom membership tiers with flexible benefits and rules.

### Membership Tier Structure

```
MembershipTier {
  name: string
  description: string
  price: decimal
  billing_period: monthly | quarterly | annually
  benefits: MembershipBenefits
  rules: MembershipRules
  is_active: boolean
}
```

### Available Benefits

| Category | Benefit Options |
|----------|-----------------|
| **Access** | Unlimited gym access, Off-peak only (specific hours), Multi-location (if applicable) |
| **Classes** | X classes per month included, Unlimited classes, Specific class types only |
| **Booking** | Priority booking, Extended advance booking window (e.g., 7 days vs 3 days) |
| **Social** | X guest passes per month, Family member add-ons |
| **Facilities** | Locker access, Towel service, Parking access |
| **Discounts** | % off merchandise, % off personal training, % off extras |
| **Freeze** | X membership pause days per year |

### Membership Rules

| Rule | Description |
|------|-------------|
| Cancellation Notice | Required notice period (e.g., 30 days) |
| Auto-Renewal | Toggle on/off, with notice before renewal |

### Special Pricing

| Type | Description |
|------|-------------|
| Corporate Rates | Discounted rates for company employees |
| Student Discount | Reduced pricing with student verification |
| Senior Discount | Reduced pricing for seniors |
| Founding Member | Locked-in pricing for early adopters |

---

## Staff Management

**Features:**

| Feature | Description |
|---------|-------------|
| Permission Levels | Owner, Manager, Front Desk, Instructor - each with defined access |
| Working Hours | Track clock-in/clock-out for staff |
| Instructor Pay Rates | Configure per-class rates for instructors |
| Schedule Management | Assign staff to shifts and classes |

**Permission Matrix:**

| Feature | Owner | Manager | Front Desk | Instructor |
|---------|-------|---------|------------|------------|
| Dashboard (full) | ✓ | ✓ | - | - |
| Member check-in | ✓ | ✓ | ✓ | - |
| Create bookings | ✓ | ✓ | ✓ | - |
| Manage memberships | ✓ | ✓ | Limited | - |
| Create classes | ✓ | ✓ | - | ✓ (needs approval) |
| Approve classes | ✓ | ✓ | - | ✓ (if admin created) |
| Manage staff | ✓ | ✓ | - | - |
| View reports | ✓ | ✓ | Limited | Own only |
| Gym settings | ✓ | Limited | - | - |
| Billing/payments | ✓ | ✓ | ✓ | - |

---

## Reporting

All reports available to owners/managers with date range filtering.

### Revenue Reports
- Daily revenue breakdown
- Weekly revenue summary
- Monthly revenue with trends
- Revenue by source (memberships, classes, merchandise)
- Revenue by payment method

### Membership Reports
- Active member count over time
- New sign-ups per period
- Churn rate (cancellations)
- Membership tier breakdown
- Expiring memberships forecast

### Attendance Reports
- Class attendance rates (per class type)
- Class fill rates (booked vs capacity)
- Peak hours/days (when gym is busiest)
- No-show rates
- Member visit frequency

### Staff Reports
- Classes taught per instructor
- Instructor attendance rates (how full are their classes)
- Staff hours worked
- Instructor earnings

### Financial Health
- Payment failure rate
- Outstanding balances
- Collection rate
- Average revenue per member

---

## Communication

Gyms can communicate with members through multiple channels.

### Communication Types & Channels

| Communication Type | In-App | Email | WhatsApp |
|--------------------|--------|-------|----------|
| General announcements | ✓ | - | - |
| Class reminders | ✓ | - | - |
| Individual messages | ✓ | - | - |
| Payment reminders | ✓ | ✓ | - |
| Account updates | ✓ | ✓ | - |
| Emergency announcements | ✓ | - | ✓ |

### Message Templates
- Pre-built templates for common messages
- Custom message creation
- Schedule messages for future delivery

### Automated Messages
- Class reminder (X hours before)
- Payment due reminder
- Payment failed notification
- Membership expiring soon
- Welcome message (new member)

---

## Gym Profile & Settings

### Public Profile (Marketplace Listing)
- Gym name and logo
- Description
- Photos/gallery
- Address and map
- Business hours
- Class types offered
- Amenities list

### Operational Settings
- Business hours (per day)
- Holiday closures
- Default booking cancellation policy (how late members can cancel)
- Check-in grace period
- Waitlist settings (auto-promote when spot opens)

### Branding
- Logo upload
- Brand colors (for consumer app integration)
- Custom welcome message

---

## Key Workflows

### Member Sign-Up (Walk-In)
1. Front desk collects details (name, phone, email)
2. Select membership tier
3. Process payment
4. System creates account invitation
5. Member downloads app, creates account with same email
6. Membership auto-linked

### Class Booking (Direct)
1. Member opens app → selects gym → browses classes
2. Selects class session
3. If membership includes classes → confirm booking
4. If pay-per-class → process payment → confirm
5. Booking confirmation sent (in-app + email)
6. Reminder sent X hours before class

### Class Check-In
1. Member arrives at gym
2. Opens app → shows QR code
3. Front desk scans QR
4. System records check-in
5. If member has class booking → marks as attended

### Payment Failed Recovery
1. Payment fails → member notified (in-app + email)
2. Appears on owner dashboard as action item
3. Gym can send manual reminder
4. Member updates payment method in app
5. Retry payment

---

## Integration Points

### With Consumer App
- Member accounts shared across platform
- Bookings sync in real-time
- Check-in QR code generated in consumer app
- Push notifications for gym communications

### With Marketplace
- Gym profile displayed on marketplace
- Classes marked "marketplace enabled" appear in search
- Marketplace bookings appear in gym's booking list (marked as source: marketplace)
- Gym receives settlement for marketplace bookings

### With API
- All features accessible via API
- Webhooks for real-time event notifications
- Third-party integration support (access control, accounting, etc.)

---

## MVP Feature Summary

### Must Have (MVP)
- Owner dashboard (action-first)
- Member check-in (QR + fallback)
- Class scheduling with space booking
- Approval workflow for classes
- Custom membership tier creation
- Full benefits configuration
- Staff management with permissions
- Instructor pay tracking
- All reports listed above
- In-app, email, WhatsApp communication
- Gym profile and settings

### Deferred (Post-MVP)
- Equipment tracking/maintenance
- Advanced marketing tools
- Multi-location management
- POS for merchandise
- Integration marketplace (third-party apps)

---

## Technical Notes

- Gym management app can be web-based (responsive) for desktop/tablet use at front desk
- Owner/manager likely access via desktop
- Front desk via tablet or desktop
- Instructors may use mobile app variant
- Real-time sync with consumer app via WebSocket
