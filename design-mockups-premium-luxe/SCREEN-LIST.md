# StudioLoop Screen List

Design Style: **Premium Luxe** (Black & Gold)

---

## Consumer Mobile App (iOS/Android)

### Authentication
1. **Splash Screen** - Logo animation, loading
2. **Onboarding** - 3-4 slides introducing the app
3. **Login** - Email/password, social login options
4. **Register** - Create account form
5. **Forgot Password** - Email reset flow

### Main Navigation
6. **Home** - Upcoming bookings, stats, recommendations ✅ (done)
7. **Discover** - Browse all classes with filters
8. **My Classes** - Upcoming and past bookings
9. **Profile** - Account settings, memberships

### Class Booking Flow
10. **Class Detail** - Full class info, instructor, book button
11. **Booking Confirmation** - Success state with details
12. **Waitlist Joined** - Waitlist confirmation

### Check-in
13. **QR Code** - Large QR for gym check-in
14. **Check-in Success** - Confirmation after scan

### Memberships
15. **My Memberships** - List of gym memberships
16. **Membership Detail** - Single membership info
17. **Marketplace Plans** - Subscribe to class packages

### Account
18. **Edit Profile** - Update personal info
19. **Payment Methods** - Manage cards
20. **Notification Settings** - Preferences
21. **Settings** - App settings, logout

### Other
22. **Notifications** - Notification center/inbox
23. **Gym Profile** - View gym details
24. **Instructor Profile** - View instructor info

---

## Consumer Web App

Same screens as mobile, with responsive layouts:
- **Mobile View** (< 768px) - Similar to app
- **Desktop View** (≥ 1024px) - Expanded layout

### Desktop-Specific
- Sidebar navigation
- Multi-column layouts
- Larger class cards with more info

---

## Gym Management Mobile App (iOS/Android)

### Authentication
1. **Splash Screen** - Logo, gym branding
2. **Login** - Staff/owner login

### Main Navigation
3. **Dashboard** - Today's overview, quick stats
4. **Today's Classes** - List of today's sessions
5. **Members** - Search and view members

### Core Features
6. **QR Scanner** - Camera view for check-in
7. **Check-in Success** - Confirmation after scan
8. **Manual Check-in** - Search by name/phone
9. **Member Detail** - Quick member view

### Classes
10. **Class Detail** - Session info, attendees
11. **Attendance List** - Who's coming/checked-in

### Quick Actions
12. **Notifications** - Alerts and messages
13. **My Schedule** - Instructor's own classes (if applicable)
14. **Settings** - App preferences

---

## Gym Management Web App

### Authentication
1. **Login** - Owner/staff login
2. **Forgot Password** - Reset flow

### Dashboard
3. **Dashboard** - KPIs, alerts, today's overview

### Classes & Schedule
4. **Class Calendar** - Monthly/weekly view
5. **Class List** - All classes table view
6. **Class Detail** - Single class with attendees
7. **Create/Edit Class** - Class form
8. **Class Templates** - Manage templates

### Members
9. **Member List** - All members table
10. **Member Detail** - Full member profile
11. **Add Member** - New member form
12. **Import Members** - CSV upload

### Staff
13. **Staff List** - All staff table
14. **Staff Detail** - Staff profile, schedule
15. **Add/Edit Staff** - Staff form
16. **Instructor Schedule** - Teaching calendar

### Bookings & Check-in
17. **Today's Check-ins** - Live check-in view
18. **Booking List** - All bookings
19. **Waitlist Management** - Current waitlists

### Memberships
20. **Membership Plans** - Configure plans
21. **Plan Detail** - Edit plan
22. **Active Memberships** - Current subscriptions

### Reports
23. **Revenue Report** - Income overview
24. **Attendance Report** - Class attendance
25. **Membership Report** - Member health
26. **Staff Report** - Performance metrics

### Settings
27. **Gym Profile** - Edit gym info
28. **Operating Hours** - Set hours
29. **Spaces** - Manage rooms/studios
30. **Policies** - Cancellation, etc.
31. **Marketplace Settings** - Toggle, pricing
32. **Notifications** - Configure alerts
33. **Account Settings** - Admin account

### Communication
34. **Messages** - Member messaging
35. **Announcements** - Broadcast messages

---

## Screen Count Summary

| App | Screens |
|-----|---------|
| Consumer Mobile | 23 |
| Consumer Web | 23 (× 2 viewports) |
| Gym Mobile | 14 |
| Gym Web | 35 |
| **Total Unique** | ~95 screens |

---

## Priority Order

### Phase 1: Consumer Mobile (Core Flow)
1. Home ✅
2. Discover
3. Class Detail
4. My Classes
5. QR Code
6. Profile
7. Login/Register

### Phase 2: Gym Web (Core Flow)
1. Dashboard
2. Class Calendar
3. Member List
4. Today's Check-ins
5. Login

### Phase 3: Consumer Web
1. Desktop versions of Phase 1

### Phase 4: Gym Mobile
1. QR Scanner
2. Dashboard
3. Today's Classes

---

_Design System: Premium Luxe_
_Colors: Black (#0a0a0a), Charcoal (#1a1a1a), Gold (#d4a855)_
