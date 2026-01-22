# StudioLoop Consumer App Specification (Brainstorm)

> Generated from brainstorming session - 2026-01-21

---

## Overview

The Consumer App serves two purposes:
1. **Membership Management** - Consumers manage their gym memberships (required by gyms using StudioLoop)
2. **Class Marketplace** - Discover and book discounted classes at any gym on the platform

**Strategic Purpose:**
- Gyms require members to use the app for membership management
- Once installed, consumers are exposed to the marketplace
- Marketplace drives cross-gym bookings and platform revenue

---

## Navigation Structure

**Bottom Tab Bar:**

| Tab | Purpose |
|-----|---------|
| **Home** | Upcoming bookings, quick actions |
| **Browse** | Discover marketplace classes |
| **Memberships** | Manage gym + marketplace subscriptions |
| **Profile** | Settings, preferences, account |

---

## Home Screen

### Layout

```
┌─────────────────────────────────┐
│ [BANNER: Membership overdue!]   │  ← Only if applicable
├─────────────────────────────────┤
│ [QR Code Button]    Hi, {name}  │  ← Quick check-in access
├─────────────────────────────────┤
│ Upcoming Bookings               │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ Yoga Flow                   │ │
│ │ FitZone Studio • 2.3km      │ │
│ │ Tomorrow, 9:00 AM • 60 min  │ │
│ │ Instructor: Sarah M.        │ │
│ │ [Cancel] [Share/Invite]     │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ Spin Class                  │ │
│ │ CyclePro • 4.1km            │ │
│ │ Fri, 6:30 PM • 45 min       │ │
│ │ Instructor: Mike T.         │ │
│ │ [Cancel] [Share/Invite]     │ │
│ └─────────────────────────────┘ │
│                                 │
├─────────────────────────────────┤
│ Empty State:                    │
│ "No upcoming bookings"          │
│ [Browse Classes →]              │
└─────────────────────────────────┘
```

### Overdue Membership Banner
- Appears at top when any gym membership has failed payment
- Tapping navigates to Memberships tab with issue highlighted
- Cannot be dismissed until resolved

### QR Code Quick Access
- Always visible button on home screen
- Tapping shows full-screen QR code for gym check-in
- QR regenerates periodically for security

### Booking Card Details
- Class name & type
- Gym name & distance
- Date, time, duration
- Instructor name
- Cancel button
- Share/Invite button

### Share/Invite Button
- Shares class details (name, gym, time)
- Includes referral link to app
- Friend can book same class and sign up via link
- No referral rewards (organic sharing only)

---

## Browse / Discover Screen

### Layout (List-First)

```
┌─────────────────────────────────┐
│ 🔍 Search classes...            │
├─────────────────────────────────┤
│ Filters:                        │
│ [Type ▼] [Date ▼] [Time ▼]     │
│ [Distance ▼] [Price ▼] [More]  │
├─────────────────────────────────┤
│ [List View] [Map View]          │
├─────────────────────────────────┤
│ 24 classes found                │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ 🧘 Vinyasa Yoga      R85    │ │
│ │ Zen Studio • 1.2km          │ │
│ │ Today, 5:30 PM • 3 spots    │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ 🚴 Spin Express      R120   │ │
│ │ CyclePro • 2.8km            │ │
│ │ Today, 6:00 PM • 8 spots    │ │
│ └─────────────────────────────┘ │
│                                 │
│ [Load more...]                  │
└─────────────────────────────────┘
```

### Filters (MVP)

| Filter | Options |
|--------|---------|
| **Class Type** | Yoga, Pilates, Spin, Boxing, HIIT, Strength, Dance, Swimming, Other |
| **Date** | Today, Tomorrow, This Week, Custom date |
| **Time of Day** | Morning (5-12), Afternoon (12-5), Evening (5-10) |
| **Distance** | 1km, 2km, 5km, 10km, Any |
| **Price Range** | Free, Under R100, R100-200, R200+ |
| **Available Only** | Toggle to hide full classes |

### Map View Toggle
- Switch between list and map view
- Map shows pins for gyms with available classes
- Tapping pin shows class summary

---

## Class Detail Screen

```
┌─────────────────────────────────┐
│ ← Back                          │
├─────────────────────────────────┤
│ [Gym Photo/Banner]              │
├─────────────────────────────────┤
│ Vinyasa Yoga                    │
│ 🧘 Yoga • 60 minutes            │
├─────────────────────────────────┤
│ 📍 Zen Studio                   │
│    123 Main Rd, Cape Town       │
│    2.3 km away                  │
├─────────────────────────────────┤
│ 📅 Tomorrow                     │
│    Wednesday, 22 Jan 2026       │
│    9:00 AM - 10:00 AM           │
├─────────────────────────────────┤
│ 👤 Instructor                   │
│    Sarah Mitchell               │
│    "Certified yoga instructor   │
│    with 8 years experience..."  │
├─────────────────────────────────┤
│ 🎫 3 spots remaining            │
├─────────────────────────────────┤
│ 💰 R85                          │
│    or 1 class from subscription │
├─────────────────────────────────┤
│ About this class                │
│ "A flowing yoga practice that   │
│ links breath with movement..."  │
├─────────────────────────────────┤
│ Gym Amenities                   │
│ 🚿 Showers  🔒 Lockers          │
│ 🅿️ Parking  ❄️ AC               │
├─────────────────────────────────┤
│ Cancellation Policy             │
│ Free cancellation up to 12      │
│ hours before class              │
├─────────────────────────────────┤
│                                 │
│ [     Book This Class     ]     │
│                                 │
└─────────────────────────────────┘
```

### Class Details Shown
- Class name, type, duration
- Gym name, address, distance
- Date and time
- Instructor name & bio
- Spots remaining
- Price OR "included in subscription"
- Class description
- Gym amenities
- Cancellation policy
- Book button

### Booking Options
Consumers can book classes at ANY gym (not just where they have membership):
- **Pay-per-class** - One-time payment for this class
- **Subscription credit** - Use 1 class from monthly allocation

---

## Booking Confirmation Flow

### Step 1: Select Payment Method
```
┌─────────────────────────────────┐
│ Book Vinyasa Yoga               │
├─────────────────────────────────┤
│ How would you like to pay?      │
│                                 │
│ ○ Use subscription credit       │
│   (4 classes remaining)         │
│                                 │
│ ○ Pay R85                       │
│   Visa •••• 4521                │
├─────────────────────────────────┤
│ [    Confirm Booking    ]       │
└─────────────────────────────────┘
```

### Step 2: Confirmation Screen
```
┌─────────────────────────────────┐
│         ✓ Booked!               │
├─────────────────────────────────┤
│ Vinyasa Yoga                    │
│ Zen Studio                      │
│ Wed, 22 Jan • 9:00 AM           │
├─────────────────────────────────┤
│ [Add to Calendar]               │
│ [Share / Invite Friend]         │
├─────────────────────────────────┤
│ [Browse More Classes]           │
│ [View My Bookings →]            │
└─────────────────────────────────┘
```

### Post-Booking Actions
- Add to phone calendar (iOS/Android native)
- Share class with invite link
- Browse more classes
- Return to home (bookings list)

---

## My Memberships Tab

### Layout

```
┌─────────────────────────────────┐
│ My Memberships                  │
├─────────────────────────────────┤
│ MARKETPLACE SUBSCRIPTION        │
│ ┌─────────────────────────────┐ │
│ │ StudioLoop Premium          │ │
│ │ 12 classes/month            │ │
│ │                             │ │
│ │ 7 classes remaining         │ │
│ │ Resets: 1 Feb 2026          │ │
│ │                             │ │
│ │ [Manage Subscription]       │ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│ GYM MEMBERSHIPS                 │
│ ┌─────────────────────────────┐ │
│ │ FitZone Studio        ✓    │ │
│ │ Premium Monthly             │ │
│ │ Active • Renews 15 Feb      │ │
│ │ [View Details]              │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ YogaLife            ⚠️     │ │
│ │ Unlimited Classes           │ │
│ │ Payment Failed              │ │
│ │ [Update Payment →]          │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

### Membership Card Details
- Gym name and logo
- Membership tier name
- Status (Active, Paused, Expiring, Payment Failed)
- Renewal date
- View details button

### Membership Detail View
- Full benefits list
- Payment history
- Pause membership option
- Cancel membership option
- Update payment method

### Marketplace Subscription Section
- Current plan name
- Classes per month
- Classes remaining
- Reset date
- Manage subscription button

### Subscription Management
- View available plans
- Subscribe (if not subscribed)
- Upgrade/downgrade plan
- Pause subscription
- Cancel subscription

---

## Profile / Settings Tab

### Layout

```
┌─────────────────────────────────┐
│ Profile                         │
├─────────────────────────────────┤
│ [Photo]                         │
│ John Smith                      │
│ john@email.com                  │
├─────────────────────────────────┤
│ ACCOUNT                         │
│ > Personal Details              │
│ > Payment Methods               │
│ > Linked Accounts               │
├─────────────────────────────────┤
│ PREFERENCES                     │
│ > Notification Settings         │
│ > Favorite Gyms                 │
│ > Favorite Class Types          │
├─────────────────────────────────┤
│ HISTORY                         │
│ > Class History                 │
│ > My Stats                      │
├─────────────────────────────────┤
│ PRIVACY & SECURITY              │
│ > Privacy Settings              │
│ > Change Password               │
├─────────────────────────────────┤
│ [Log Out]                       │
│ [Delete Account]                │
└─────────────────────────────────┘
```

### Personal Details
- Name
- Email
- Phone number
- Profile photo

### Payment Methods
- Add/remove cards
- Set default payment method
- View payment history

### Linked Accounts
- Google
- Facebook
- Apple
- Phone (OTP)

### Notification Settings
- Per channel toggles (In-app, Email, WhatsApp)
- Per type toggles:
  - Booking confirmations
  - Class reminders
  - Waitlist updates
  - Payment notifications
  - Membership alerts
  - New classes at favorites
  - Gym announcements

### Favorites
- Favorite gyms (quick filter in browse)
- Favorite class types (personalized recommendations)

### Class History
- List of past classes attended
- Filter by gym, class type, date range
- Rebook button on each past class

### My Stats
- Total classes attended
- Classes this month
- Favorite class type
- Most visited gym
- Streak (consecutive weeks with classes)

### Privacy Settings
- Profile visibility
- Data sharing preferences

---

## QR Code Check-In

### Access Points
1. **Home screen** - Quick access button always visible
2. **Booking card** - Tap to show QR for that specific booking

### QR Code Screen
```
┌─────────────────────────────────┐
│ ← Close                         │
├─────────────────────────────────┤
│                                 │
│     ┌─────────────────────┐     │
│     │                     │     │
│     │    [QR CODE]        │     │
│     │                     │     │
│     └─────────────────────┘     │
│                                 │
│     John Smith                  │
│                                 │
│     Show this code at           │
│     the front desk              │
│                                 │
├─────────────────────────────────┤
│ Today's Booking:                │
│ Vinyasa Yoga @ Zen Studio       │
│ 9:00 AM                         │
└─────────────────────────────────┘
```

### QR Code Behavior
- Regenerates periodically for security
- Works for gym entry (membership check-in)
- Works for class check-in (booking verification)
- Front desk scans to record attendance

---

## Waitlist

### Joining Waitlist
When class is full:
```
┌─────────────────────────────────┐
│ Class is Full                   │
│                                 │
│ 0 spots available               │
│ 3 people on waitlist            │
│                                 │
│ [Join Waitlist]                 │
│                                 │
│ You'll be notified if a         │
│ spot opens up                   │
└─────────────────────────────────┘
```

### Waitlist Flow
1. Consumer joins waitlist
2. When someone cancels → spot opens
3. Top person on waitlist gets push notification
4. They have 30 minutes to confirm booking
5. If no response → moves to next person
6. Repeat until spot is filled or waitlist exhausted

### Waitlist Notification
```
┌─────────────────────────────────┐
│ 🎉 Spot Available!              │
│                                 │
│ A spot opened up for:           │
│ Vinyasa Yoga @ Zen Studio       │
│ Tomorrow, 9:00 AM               │
│                                 │
│ You have 30 minutes to confirm  │
│                                 │
│ [Confirm Booking]  [Pass]       │
└─────────────────────────────────┘
```

---

## Cancellation Policy

### How It Works
- Each gym sets their own cancellation window
- Displayed on class detail screen before booking
- Examples: 2 hours, 6 hours, 12 hours, 24 hours

### Cancellation Outcomes

| Timing | Result |
|--------|--------|
| Within policy window | Full refund / credit returned |
| Outside policy window | No refund, credit lost |
| No-show | No refund, credit lost |

### Cancel Flow
```
┌─────────────────────────────────┐
│ Cancel Booking?                 │
│                                 │
│ Vinyasa Yoga @ Zen Studio       │
│ Tomorrow, 9:00 AM               │
│                                 │
│ ⚠️ This gym requires 12 hours   │
│ notice for free cancellation.   │
│                                 │
│ Cancelling now will forfeit     │
│ your class credit.              │
│                                 │
│ [Keep Booking]                  │
│ [Cancel Anyway]                 │
└─────────────────────────────────┘
```

---

## Notifications

### Push Notification Triggers

| Trigger | Timing | Priority |
|---------|--------|----------|
| Booking confirmation | Immediate | High |
| Class reminder | X hours before (configurable) | High |
| Waitlist spot available | Immediate | High |
| Payment due | 3 days before | Medium |
| Payment failed | Immediate | High |
| Membership expiring | 7 days before | Medium |
| New classes at favorites | Daily digest | Low |
| Gym announcements | As sent | Varies |

### Notification Channels

| Type | In-App | Email | WhatsApp |
|------|--------|-------|----------|
| Booking confirmation | ✓ | ✓ | - |
| Class reminder | ✓ | - | - |
| Waitlist available | ✓ | ✓ | - |
| Payment due | ✓ | ✓ | - |
| Payment failed | ✓ | ✓ | - |
| Membership expiring | ✓ | ✓ | - |
| New classes | ✓ | - | - |
| Gym emergency | ✓ | - | ✓ |

---

## MVP Feature Summary

### Must Have (MVP)
- Home screen with bookings + overdue banner
- QR code check-in (home + booking card)
- Browse classes (list-first + map toggle)
- All filters (type, date, time, distance, price, availability)
- Class detail screen with full info
- Booking flow (subscription or pay-per-class)
- Post-booking confirmation + calendar add
- Share/invite functionality
- My Memberships (gym + marketplace)
- Subscription management (view, subscribe, upgrade, pause, cancel)
- Profile & settings (all listed features)
- Class history + stats
- Waitlist with timed confirmation
- Cancellation (gym-defined policy)
- Full notification suite

### Deferred (Post-MVP)
- Social features (find friends)
- Class ratings/reviews
- Personalized recommendations
- Achievements/gamification
- In-app messaging with gyms

---

## Technical Notes

- Native mobile app (iOS + Android)
- Offline support for viewing bookings and QR code
- Push notification integration (FCM/APNs)
- Deep linking for share/invite functionality
- Calendar integration (iOS EventKit / Android Calendar Provider)
- Location services for distance calculation
- Real-time updates via WebSocket (class availability, waitlist)
