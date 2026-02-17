# StudioLoop API Specification (Brainstorm)

> Generated from brainstorming session - 2026-01-21

---

## Overview

StudioLoop is a multi-tenant platform with shared consumer profiles, enabling:
- Gym management SaaS for Cape Town gyms
- Class marketplace for consumers to book discounted off-peak classes

**Architecture:** Single API serving all gyms (tenants) with shared consumer identity layer.

---

## Core Entities

### Gym (Tenant)
```
Gym {
  id: UUID
  name: string
  slug: string (unique, URL-friendly)
  description: text
  address: string
  location: GeoPoint (lat, lng)
  contact_email: string
  contact_phone: string
  business_hours: JSON
  settings: JSON
  subscription_tier: enum (free, basic, premium)
  is_active: boolean
  created_at: timestamp
  updated_at: timestamp
}
```

### Consumer (Platform-wide)
```
Consumer {
  id: UUID
  email: string (unique)
  phone: string (unique, optional)
  password_hash: string (nullable if social/OTP only)
  first_name: string
  last_name: string
  profile_photo_url: string
  auth_providers: JSON (google, facebook, apple, phone)
  subscription_id: UUID (nullable - marketplace subscription)
  is_active: boolean
  created_at: timestamp
  updated_at: timestamp
}
```

### Staff (Gym-scoped)
```
Staff {
  id: UUID
  gym_id: UUID (FK)
  email: string
  phone: string
  password_hash: string
  first_name: string
  last_name: string
  role: enum (owner, manager, instructor, front_desk)
  certifications: JSON
  bio: text
  profile_photo_url: string
  pay_rate_per_class: decimal (for instructors)
  is_active: boolean
  created_at: timestamp
  updated_at: timestamp
}
```

### StaffShift (Working Hours Tracking)
```
StaffShift {
  id: UUID
  staff_id: UUID (FK)
  gym_id: UUID (FK)
  clock_in: timestamp
  clock_out: timestamp (nullable if currently clocked in)
  total_hours: decimal (computed)
  created_at: timestamp
}
```

### Membership (Consumer <-> Gym relationship)
```
Membership {
  id: UUID
  consumer_id: UUID (FK)
  gym_id: UUID (FK)
  plan_id: UUID (FK)
  status: enum (active, paused, cancelled, expired)
  start_date: date
  end_date: date (nullable for ongoing)
  auto_renew: boolean
  created_at: timestamp
  updated_at: timestamp
}
```

### MembershipPlan (Gym-defined)
```
MembershipPlan {
  id: UUID
  gym_id: UUID (FK)
  name: string
  description: text
  price: decimal
  billing_period: enum (monthly, quarterly, annually)
  benefits: MembershipBenefits (JSON)
  rules: MembershipRules (JSON)
  is_active: boolean
  created_at: timestamp
  updated_at: timestamp
}

MembershipBenefits {
  // Access
  unlimited_gym_access: boolean
  off_peak_only: boolean (if true, specify hours)
  off_peak_hours: { start: time, end: time }

  // Classes
  classes_per_month: integer (null = unlimited, 0 = none)
  unlimited_classes: boolean
  allowed_class_types: array<string> (null = all types)

  // Booking
  priority_booking: boolean
  advance_booking_days: integer (how far ahead can book)

  // Social
  guest_passes_per_month: integer

  // Facilities
  locker_access: boolean
  towel_service: boolean
  parking_access: boolean

  // Discounts
  merchandise_discount_percent: integer
  pt_discount_percent: integer

  // Freeze
  freeze_days_per_year: integer
}

MembershipRules {
  cancellation_notice_days: integer
  auto_renew: boolean
}
```

### Space (Physical Room/Studio)
```
Space {
  id: UUID
  gym_id: UUID (FK)
  name: string
  capacity: integer
  equipment: array<string> (mats, bikes, weights, TRX, etc.)
  amenities: array<string> (mirrors, sound system, AC, natural light, etc.)
  is_active: boolean
  created_at: timestamp
  updated_at: timestamp
}
```

### MarketplaceSubscription (Platform-wide consumer subscription)
```
MarketplaceSubscription {
  id: UUID
  consumer_id: UUID (FK)
  plan_type: enum (basic_8, standard_12, premium_20) // classes per month
  classes_remaining: integer
  classes_total: integer
  billing_day: integer (1-28)
  status: enum (active, paused, cancelled)
  current_period_start: date
  current_period_end: date
  created_at: timestamp
  updated_at: timestamp
}
```

### Class (Template)
```
Class {
  id: UUID
  gym_id: UUID (FK)
  name: string
  description: text
  category: enum (yoga, pilates, spin, boxing, hiit, strength, dance, swimming, other)
  duration_minutes: integer
  default_capacity: integer
  default_price: decimal
  is_active: boolean
  created_at: timestamp
  updated_at: timestamp
}
```

### ClassSession (Scheduled instance)
```
ClassSession {
  id: UUID
  class_id: UUID (FK)
  gym_id: UUID (FK)
  space_id: UUID (FK to Space - required)
  instructor_id: UUID (FK to Staff)
  start_time: timestamp
  end_time: timestamp
  capacity: integer (defaults from space, can be lower)
  spots_booked: integer
  spots_available: integer (computed)
  price: decimal (can override class default)
  marketplace_price: decimal (discounted price for marketplace)
  is_marketplace_enabled: boolean
  status: enum (pending_approval, scheduled, cancelled, completed)
  created_by: UUID (FK to Staff - who created the session)
  approved_by: UUID (FK to Staff - who approved, nullable)
  approved_at: timestamp (nullable)
  created_at: timestamp
  updated_at: timestamp
}
```

**Class Approval Workflow:**
- If instructor creates session → status = pending_approval, needs owner/manager approval
- If owner/manager creates session → status = pending_approval, needs instructor to confirm availability
- Once approved → status = scheduled, visible to members

### Booking
```
Booking {
  id: UUID
  consumer_id: UUID (FK)
  session_id: UUID (FK)
  gym_id: UUID (FK)
  source: enum (direct, marketplace)
  booking_type: enum (subscription, pay_per_class, membership_benefit)
  status: enum (confirmed, cancelled, attended, no_show)
  price_paid: decimal
  booked_at: timestamp
  checked_in_at: timestamp (nullable)
  cancelled_at: timestamp (nullable)
  cancellation_reason: string (nullable)
}
```

### Payment
```
Payment {
  id: UUID
  consumer_id: UUID (FK)
  gym_id: UUID (FK, nullable - null for marketplace subscriptions)
  booking_id: UUID (FK, nullable)
  membership_id: UUID (FK, nullable)
  marketplace_subscription_id: UUID (FK, nullable)
  amount: decimal
  currency: string (default: ZAR)
  type: enum (booking, membership, marketplace_subscription)
  status: enum (pending, completed, failed, refunded)
  payment_provider: string (placeholder for future)
  provider_reference: string
  created_at: timestamp
  updated_at: timestamp
}
```

### Waitlist
```
WaitlistEntry {
  id: UUID
  consumer_id: UUID (FK)
  session_id: UUID (FK)
  position: integer
  status: enum (waiting, offered, accepted, expired)
  offered_at: timestamp (nullable)
  expires_at: timestamp (nullable)
  created_at: timestamp
}
```

---

## API Domains & Endpoints

### 1. Authentication & Identity

**Consumers:**
```
POST   /auth/consumer/register          # Email/password registration
POST   /auth/consumer/login             # Email/password login
POST   /auth/consumer/social            # Social login (Google, Facebook, Apple)
POST   /auth/consumer/otp/request       # Request phone OTP
POST   /auth/consumer/otp/verify        # Verify phone OTP
POST   /auth/consumer/refresh           # Refresh access token
POST   /auth/consumer/logout            # Logout / invalidate token
POST   /auth/consumer/password/reset    # Request password reset
POST   /auth/consumer/password/update   # Update password with reset token
```

**Gym Staff:**
```
POST   /auth/staff/login                # Email/password login
POST   /auth/staff/otp/request          # Request phone OTP
POST   /auth/staff/otp/verify           # Verify phone OTP
POST   /auth/staff/refresh              # Refresh access token
POST   /auth/staff/logout               # Logout
POST   /auth/staff/password/reset       # Request password reset
POST   /auth/staff/password/update      # Update password
```

### 2. Gym Management

```
# Gym CRUD (owner/manager only)
GET    /gyms/:gym_id                    # Get gym details
PUT    /gyms/:gym_id                    # Update gym details
PATCH  /gyms/:gym_id/settings           # Update gym settings
GET    /gyms/:gym_id/dashboard          # Dashboard analytics (action items + metrics)

# Staff management
GET    /gyms/:gym_id/staff              # List staff
POST   /gyms/:gym_id/staff              # Add staff member
GET    /gyms/:gym_id/staff/:staff_id    # Get staff details
PUT    /gyms/:gym_id/staff/:staff_id    # Update staff
DELETE /gyms/:gym_id/staff/:staff_id    # Remove staff

# Staff shifts (working hours)
POST   /gyms/:gym_id/staff/:staff_id/clock-in   # Clock in
POST   /gyms/:gym_id/staff/:staff_id/clock-out  # Clock out
GET    /gyms/:gym_id/staff/:staff_id/shifts     # Get shift history

# Spaces (rooms/studios)
GET    /gyms/:gym_id/spaces             # List spaces
POST   /gyms/:gym_id/spaces             # Create space
GET    /gyms/:gym_id/spaces/:space_id   # Get space details
PUT    /gyms/:gym_id/spaces/:space_id   # Update space
DELETE /gyms/:gym_id/spaces/:space_id   # Deactivate space
GET    /gyms/:gym_id/spaces/:space_id/availability  # Check space availability for date range

# Check-in
POST   /gyms/:gym_id/checkin            # Check in member (QR code scan)
POST   /gyms/:gym_id/checkin/lookup     # Lookup member by phone/name (fallback)
```

### 3. Membership Management

```
# Membership plans (gym-defined)
GET    /gyms/:gym_id/plans              # List membership plans
POST   /gyms/:gym_id/plans              # Create plan
PUT    /gyms/:gym_id/plans/:plan_id     # Update plan
DELETE /gyms/:gym_id/plans/:plan_id     # Deactivate plan

# Member memberships
GET    /gyms/:gym_id/memberships        # List gym's members
POST   /gyms/:gym_id/memberships        # Create membership for consumer
GET    /gyms/:gym_id/memberships/:id    # Get membership details
PATCH  /gyms/:gym_id/memberships/:id    # Update membership (pause, cancel, etc.)

# Consumer's own memberships
GET    /consumer/memberships            # List my memberships across gyms
GET    /consumer/memberships/:id        # Get specific membership
PATCH  /consumer/memberships/:id        # Cancel/pause my membership

# Consumer QR code (for gym check-in)
GET    /consumer/qr-code                # Get my check-in QR code (regenerates periodically)
```

### 4. Classes & Scheduling

```
# Class templates
GET    /gyms/:gym_id/classes            # List class types
POST   /gyms/:gym_id/classes            # Create class type
PUT    /gyms/:gym_id/classes/:class_id  # Update class type
DELETE /gyms/:gym_id/classes/:class_id  # Deactivate class type

# Class sessions (scheduled instances)
GET    /gyms/:gym_id/sessions           # List sessions (filterable by date range, status)
POST   /gyms/:gym_id/sessions           # Create session (status=pending_approval)
POST   /gyms/:gym_id/sessions/bulk      # Create recurring sessions
GET    /gyms/:gym_id/sessions/:id       # Get session details + attendees
PUT    /gyms/:gym_id/sessions/:id       # Update session
DELETE /gyms/:gym_id/sessions/:id       # Cancel session
PATCH  /gyms/:gym_id/sessions/:id/marketplace  # Enable/disable marketplace listing

# Session approval workflow
GET    /gyms/:gym_id/sessions/pending   # List sessions pending approval
POST   /gyms/:gym_id/sessions/:id/approve   # Approve session (owner/manager or instructor)
POST   /gyms/:gym_id/sessions/:id/reject    # Reject session with reason

# Space availability check (for scheduling UI)
GET    /gyms/:gym_id/spaces/available   # Get available spaces for time slot
       ?date=2026-01-22
       ?start_time=09:00
       ?end_time=10:00
       ?min_capacity=20
```

### 5. Bookings

```
# Gym-side booking management
GET    /gyms/:gym_id/bookings           # List bookings (filterable)
POST   /gyms/:gym_id/bookings           # Create booking (walk-in)
GET    /gyms/:gym_id/bookings/:id       # Get booking details
PATCH  /gyms/:gym_id/bookings/:id       # Update booking status
POST   /gyms/:gym_id/bookings/:id/checkin  # Check in attendee

# Consumer bookings
GET    /consumer/bookings               # My bookings (upcoming + past)
POST   /consumer/bookings               # Book a class
DELETE /consumer/bookings/:id           # Cancel booking
GET    /consumer/bookings/:id           # Get booking details

# Waitlist
POST   /sessions/:session_id/waitlist   # Join waitlist
DELETE /sessions/:session_id/waitlist   # Leave waitlist
POST   /sessions/:session_id/waitlist/accept  # Accept offered spot
```

### 6. Marketplace

```
# Discovery & Search
GET    /marketplace/search              # Search classes
       ?category=yoga,spin
       ?lat=-33.9&lng=18.4&radius=10km
       ?date=2026-01-22
       ?time_from=06:00&time_to=12:00
       ?price_max=150
       ?available=true

GET    /marketplace/gyms                # List gyms on marketplace
GET    /marketplace/gyms/:gym_id        # Gym public profile
GET    /marketplace/sessions/:id        # Session details for booking

# Marketplace subscriptions
GET    /marketplace/plans               # Available subscription plans
POST   /consumer/marketplace-subscription  # Subscribe to marketplace
GET    /consumer/marketplace-subscription  # My subscription details
PATCH  /consumer/marketplace-subscription  # Pause/cancel subscription
```

### 7. Payments (Interface - Implementation Deferred)

```
# Payment provider abstraction
POST   /payments/initiate               # Start payment flow
POST   /payments/webhook                # Provider webhook callback
GET    /payments/:id                    # Get payment status

# Consumer payment history
GET    /consumer/payments               # My payment history

# Gym payment/revenue
GET    /gyms/:gym_id/payments           # Gym's received payments
GET    /gyms/:gym_id/revenue            # Revenue analytics
```

### 8. Webhooks (For Gym Integrations)

```
# Webhook management
GET    /gyms/:gym_id/webhooks           # List registered webhooks
POST   /gyms/:gym_id/webhooks           # Register webhook endpoint
PUT    /gyms/:gym_id/webhooks/:id       # Update webhook
DELETE /gyms/:gym_id/webhooks/:id       # Remove webhook
GET    /gyms/:gym_id/webhooks/:id/logs  # View delivery logs
POST   /gyms/:gym_id/webhooks/:id/test  # Send test event
```

**Available Events:**
```
booking.created
booking.cancelled
booking.checked_in
booking.no_show
membership.created
membership.renewed
membership.cancelled
membership.expired
payment.completed
payment.failed
session.created
session.cancelled
waitlist.spot_available
```

### 9. Notifications (Internal)

```
# Notification preferences
GET    /consumer/notifications/preferences
PUT    /consumer/notifications/preferences

# Notification history
GET    /consumer/notifications          # My notifications
PATCH  /consumer/notifications/:id/read # Mark as read
```

**Notification Channels:**
- Email (transactional)
- Push notifications (mobile app)
- WhatsApp Business API

### 10. Reports (Gym Analytics)

```
# Revenue reports
GET    /gyms/:gym_id/reports/revenue    # Revenue summary
       ?period=daily|weekly|monthly
       ?start_date=2026-01-01
       ?end_date=2026-01-31

# Membership reports
GET    /gyms/:gym_id/reports/memberships  # Membership analytics
       ?period=daily|weekly|monthly       # Growth, churn, tier breakdown

# Attendance reports
GET    /gyms/:gym_id/reports/attendance   # Class attendance & fill rates
GET    /gyms/:gym_id/reports/peak-hours   # Popular times analysis

# Staff reports
GET    /gyms/:gym_id/reports/staff        # Staff performance
       ?staff_id=uuid                      # Optional filter to single staff

# Financial health
GET    /gyms/:gym_id/reports/payments     # Payment failures, outstanding balances
```

### 11. Gym Communication

```
# Send messages to members
POST   /gyms/:gym_id/messages           # Send message/announcement
       {
         "type": "announcement|individual|reminder",
         "recipient_ids": [...] | "all",
         "channels": ["in_app", "email", "whatsapp"],
         "subject": "...",
         "body": "...",
         "scheduled_at": timestamp (optional)
       }

GET    /gyms/:gym_id/messages           # Message history
GET    /gyms/:gym_id/messages/:id       # Message details + delivery status

# Message templates
GET    /gyms/:gym_id/message-templates  # List templates
POST   /gyms/:gym_id/message-templates  # Create template
PUT    /gyms/:gym_id/message-templates/:id  # Update template
DELETE /gyms/:gym_id/message-templates/:id  # Delete template
```

---

## Real-Time (WebSocket)

**Connection:**
```
WSS /ws?token={access_token}
```

**Subscriptions:**
```json
// Subscribe to session availability
{"action": "subscribe", "channel": "session:availability", "session_id": "uuid"}

// Subscribe to waitlist updates
{"action": "subscribe", "channel": "waitlist", "session_id": "uuid"}

// Subscribe to booking confirmations
{"action": "subscribe", "channel": "consumer:bookings"}
```

**Events:**
```json
// Spots updated
{"event": "session.spots_updated", "session_id": "uuid", "spots_available": 3}

// Waitlist position changed
{"event": "waitlist.position_updated", "session_id": "uuid", "position": 2}

// Spot offered from waitlist
{"event": "waitlist.spot_offered", "session_id": "uuid", "expires_at": "timestamp"}

// Booking confirmed
{"event": "booking.confirmed", "booking_id": "uuid", "session_id": "uuid"}
```

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Tenancy** | Shared consumer profiles | Platform owns consumer relationship, enables cross-gym booking |
| **Marketplace model** | Flat class count + pay-per-class | Simple for consumers, low barrier to entry |
| **Booking source** | Track direct vs marketplace | Enables commission calculation, shows gym ROI |
| **Payments** | Abstracted interface | Deferred implementation, will integrate SA gateways later |
| **Real-time** | WebSocket support | Better UX for availability, prevents double-booking frustration |
| **Webhooks** | Included in MVP | Makes platform extensible for gym integrations |
| **Equipment tracking** | Deferred | Not core to MVP value proposition |
| **Auth methods** | Email, social, phone OTP | Maximum flexibility for both user types |
| **Notifications** | Email, push, WhatsApp | High engagement channels popular in SA |
| **Search primary** | Class type, then distance | Core discovery pattern for marketplace |
| **Ratings** | Collect but hide UI | Build data now, design rating system later |

---

## MVP Scope Summary

**In MVP:**
- Multi-tenant gym management
- Shared consumer identity
- Class scheduling & booking
- Marketplace search & discovery
- Flat-rate subscriptions + pay-per-class
- Real-time availability (WebSocket)
- Webhooks for gym integrations
- Email, push, WhatsApp notifications
- Booking source tracking

**Deferred:**
- Payment gateway integration (interface ready)
- Equipment tracking
- Rating system UI
- SMS notifications

---

## Technical Notes

- **Database:** PostgreSQL (relational data, geo queries)
- **Framework:** FastAPI (Python)
- **Auth:** JWT tokens with refresh rotation
- **Real-time:** WebSocket with Redis pub/sub for scaling
- **Geo:** PostGIS for location-based queries
- **Queue:** Background jobs for notifications, webhooks
