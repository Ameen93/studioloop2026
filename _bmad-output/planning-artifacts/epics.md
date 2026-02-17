---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - prd.md
  - architecture.md
  - api-brainstorm.md
  - consumer-app-brainstorm.md
  - gym-management-app-brainstorm.md
status: 'validated_complete'
epicCount: 17
totalFRs: 85
totalNFRs: 38
totalARCHs: 30
totalStories: 169
validatedAt: '2026-01-22'
platformStrategy: 'local-first-then-deploy'
developmentApproach: 'Build and test entire system locally before production deployment'
appEpics:
  - epic: 12
    name: 'Gym Web Application'
    priority: 1
    stories: 11
  - epic: 13
    name: 'Consumer Web Application'
    priority: 2
    stories: 9
  - epic: 14
    name: 'Consumer Mobile Application'
    priority: 3
    stories: 9
  - epic: 15
    name: 'Gym Mobile Application'
    priority: 4
    stories: 11
---

# StudioLoop - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for StudioLoop, decomposing the requirements from the PRD, Architecture, and brainstorming documents into implementable stories.

## Requirements Inventory

### Functional Requirements

**Account & Authentication (6 FRs)**

- **FR1:** Users can register using email, social login (Google, Facebook, Apple), or phone OTP
- **FR2:** Users can authenticate and maintain secure sessions across devices
- **FR3:** Users can reset their password via email
- **FR4:** Users can manage their profile information (name, photo, contact details)
- **FR5:** Users can delete their account and associated data (POPIA compliance)
- **FR6:** Platform can enforce role-based access control per user type

**Gym Management (7 FRs)**

- **FR7:** Gym owners can register their gym and complete onboarding
- **FR8:** Gym owners can configure gym profile (name, logo, description, photos, location)
- **FR9:** Gym owners can set operating hours and holiday closures
- **FR10:** Gym owners can configure cancellation policies and booking rules
- **FR11:** Gym owners can enable/disable marketplace participation for their gym
- **FR12:** Gym owners can view and manage their SaaS subscription tier
- **FR13:** Gym owners can import existing member data from spreadsheets

**Consumer Profile & Membership (7 FRs)**

- **FR14:** Consumers can link to multiple gyms from a single profile
- **FR15:** Consumers can view all their gym memberships in one place
- **FR16:** Consumers can manage payment methods for each membership
- **FR17:** Consumers can upgrade or downgrade their membership tier
- **FR18:** Consumers can view membership benefits and usage limits
- **FR19:** Consumers can accept digital waivers required by gyms
- **FR20:** Gyms can view their members and membership statuses

**Staff Management (6 FRs)**

- **FR21:** Gym owners can add staff members and assign roles (Manager, Front Desk, Instructor)
- **FR22:** Gym owners can configure permissions per role
- **FR23:** Gym owners can manage staff working hours and shifts
- **FR24:** Gym owners can set instructor pay rates per class
- **FR25:** Instructors can view their scheduled classes and earnings
- **FR26:** Staff can access features appropriate to their assigned role

**Space & Facility Management (4 FRs)**

- **FR27:** Gym owners can create and manage spaces (rooms, studios, areas)
- **FR28:** Gym owners can set capacity limits per space
- **FR29:** Gym owners can define amenities and equipment per space
- **FR30:** System prevents double-booking of spaces

**Class Scheduling (8 FRs)**

- **FR31:** Gym staff can create class templates with recurring schedules
- **FR32:** Gym staff can schedule individual class sessions
- **FR33:** Gym staff can assign instructors to classes
- **FR34:** Gym staff can assign spaces to classes
- **FR35:** Classes can require approval before becoming visible (configurable workflow)
- **FR36:** Gym staff can cancel classes and notify affected members
- **FR37:** Gym staff can set class capacity and waitlist limits
- **FR38:** Gym owners can set marketplace pricing for classes

**Booking & Check-in (10 FRs)**

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

**Marketplace & Discovery (8 FRs)**

- **FR49:** Consumers can browse classes from all marketplace-enabled gyms
- **FR50:** Consumers can filter classes by type, location, date/time, price, and availability
- **FR51:** Consumers can view gym profiles and class details before booking
- **FR52:** Consumers can subscribe to marketplace class packages (8/12/unlimited)
- **FR53:** Consumers can book individual classes without subscription (pay-per-class)
- **FR54:** System tracks marketplace class credits and usage
- **FR55:** Consumers can share class details with others
- **FR56:** Consumers can invite friends via referral links

**Payments & Billing (6 FRs)**

- **FR57:** System supports abstracted payment interface for future gateway integration
- **FR58:** Gyms can view pending and completed payments
- **FR59:** System detects and flags failed payments
- **FR60:** System supports automatic payment retry
- **FR61:** Gyms can view marketplace booking revenue and payout reports
- **FR62:** Consumers can view their payment history

**Notifications & Communication (7 FRs)**

- **FR63:** System sends booking confirmations via push and email
- **FR64:** System sends class reminders before scheduled classes
- **FR65:** System sends waitlist notifications when spots become available
- **FR66:** System sends payment reminders and failure alerts
- **FR67:** Gym staff can send messages to individual members or groups
- **FR68:** System supports WhatsApp for critical/emergency notifications
- **FR69:** Consumers can configure notification preferences

**Reporting & Analytics (7 FRs)**

- **FR70:** Gym owners can view revenue reports (membership + marketplace)
- **FR71:** Gym owners can view attendance and check-in reports
- **FR72:** Gym owners can view membership health reports (active, at-risk, churned)
- **FR73:** Gym owners can view class performance reports (fill rate, attendance)
- **FR74:** Gym owners can view staff performance reports
- **FR75:** Consumers can view their class history and statistics
- **FR76:** System flags at-risk members based on engagement patterns

**Platform Administration (6 FRs)**

- **FR77:** Platform admins can review and approve new gym applications
- **FR78:** Platform admins can view and manage all gyms on the platform
- **FR79:** Platform admins can view and manage consumer complaints
- **FR80:** Platform admins can issue credits to consumer accounts
- **FR81:** Platform admins can monitor platform health metrics
- **FR82:** Platform admins can access gym-level data for support purposes

**Real-time & Integration (3 FRs)**

- **FR83:** System provides real-time class availability updates
- **FR84:** System supports webhook events for gym integrations
- **FR85:** QR code display (consumer) and QR scanner (gym mobile) function offline and sync when connectivity restored

### NonFunctional Requirements

**Performance (6 NFRs)**

- **NFR1:** API response time <200ms p95 for core CRUD operations
- **NFR2:** Class availability updates <1s latency via WebSocket
- **NFR3:** QR code scan to confirmation <2s for gym entry experience
- **NFR4:** Class browse/filter response <500ms for consumer discovery
- **NFR5:** Mobile app cold start <3s to first screen visible
- **NFR6:** Image/asset loading: lazy load, <1MB initial bundle for SA mobile data constraints

**Security (8 NFRs)**

- **NFR7:** Data encryption at rest using AES-256 for all PII and sensitive data
- **NFR8:** Data encryption in transit using TLS 1.2+ for all API communications
- **NFR9:** Multi-tenant data isolation with zero cross-tenant data leakage
- **NFR10:** Authentication tokens: JWT with <24h expiry, refresh rotation
- **NFR11:** Password storage: bcrypt/argon2, minimum 12 rounds
- **NFR12:** API rate limiting per-user/per-gym to prevent abuse/scraping
- **NFR13:** POPIA compliance: data export, deletion within 30 days
- **NFR14:** Audit logging for all admin actions and data access

**Scalability (5 NFRs)**

- **NFR15:** Support 5,000+ concurrent users for Phase 2 growth
- **NFR16:** Support 10,000 concurrent WebSocket connections for real-time class updates
- **NFR17:** Database scaling via horizontal read replicas so reports don't impact ops
- **NFR18:** Booking throughput of 100 bookings/minute at peak (popular class release)
- **NFR19:** Handle 10x user growth with <10% performance degradation

**Reliability (6 NFRs)**

- **NFR20:** System uptime 99.5% (22 hours downtime/month max)
- **NFR21:** Data durability 99.99% (no data loss) for member and booking data
- **NFR22:** Offline QR functionality: check-in works without connectivity
- **NFR23:** Graceful degradation: core features work if secondary services fail
- **NFR24:** Daily backups with 30-day retention for disaster recovery
- **NFR25:** Recovery time objective <4 hours from major failure

**Accessibility (4 NFRs)**

- **NFR26:** Color contrast WCAG 2.1 AA minimum for bright gym environments
- **NFR27:** Touch targets minimum 44x44px for mobile usability
- **NFR28:** Screen reader support for core flows (VoiceOver/TalkBack)
- **NFR29:** Text scaling support up to 200% for accessibility settings

**Integration (5 NFRs)**

- **NFR30:** Email delivery 99% within 5 minutes for transactional notifications
- **NFR31:** Push notification delivery 95% within 30 seconds for time-sensitive alerts
- **NFR32:** WhatsApp API reliability with fallback to email if unavailable
- **NFR33:** Webhook delivery at-least-once with retry (3 attempts) for gym integrations
- **NFR34:** Payment interface abstracted and provider-swappable (PayFast/Ozow flexibility)

**Data & Compliance (4 NFRs)**

- **NFR35:** Data residency in SA-based or POPIA-compliant hosting for consumer PII
- **NFR36:** Data retention configurable per data type for compliance flexibility
- **NFR37:** Consent tracking: record all consumer consents with timestamps for POPIA audit
- **NFR38:** Data export: consumer data exportable within 48 hours for POPIA right of access

### Additional Requirements

**From Architecture - Starter Template & Infrastructure:**

- **ARCH-1: Starter Template** - Use FastAPI Full Stack Template (`copier copy https://github.com/fastapi/full-stack-fastapi-template backend --trust`) for backend initialization
- **ARCH-2: Frontend Monorepo** - Initialize Turborepo + pnpm workspace with apps (gym-web, consumer-web, consumer-mobile, gym-mobile) and packages (api-client, ui, utils)
- **ARCH-3: Hosting** - Deploy to Fly.io Johannesburg (`jnb`) region for POPIA data residency compliance
- **ARCH-4: Database** - PostgreSQL 16 with PostGIS on Fly Postgres (Johannesburg), SQLModel async ORM
- **ARCH-5: Caching** - Redis self-hosted on Fly.io for sessions, real-time pub/sub, booking locks
- **ARCH-6: API Client Generation** - Hey API (@hey-api/openapi-ts) for TypeScript client + TanStack Query hooks from OpenAPI schema
- **ARCH-7: Mobile Builds** - EAS Build (Expo) for cloud builds, OTA updates, and app store submission
- **ARCH-8: Monitoring** - Sentry for error tracking + Fly Metrics for performance monitoring
- **ARCH-9: CI/CD** - GitHub Actions with Turborepo caching, deploy on merge to main

**From Architecture - Authentication & Security:**

- **ARCH-10: Auth Strategy** - Custom JWT with FastAPI native implementation (no external auth provider)
- **ARCH-11: Password Hashing** - Argon2 via pwdlib (memory-hard algorithm)
- **ARCH-12: Token Management** - JWT access tokens (<24h expiry) + refresh token rotation
- **ARCH-13: RBAC** - Role claims in JWT: Owner, Manager, Front Desk, Instructor, Consumer, Platform Admin
- **ARCH-14: Social Login** - Authlib for Google, Apple integration (add when needed)

**From Architecture - Frontend Patterns:**

- **ARCH-15: State Management** - TanStack Query v5 for server state, Zustand for client-only state
- **ARCH-16: Offline Storage (KV)** - MMKV for auth tokens, user preferences (30x faster than AsyncStorage)
- **ARCH-17: Offline Storage (Relational)** - Expo SQLite for cached classes, pending bookings, check-in queue
- **ARCH-18: Styling** - NativeWind v4 for mobile, Tailwind CSS v4 for web (shared design tokens)
- **ARCH-19: Navigation** - Expo Router for file-based routing and deep linking

**From Architecture - Payment Integration:**

- **ARCH-20: Primary Payment Gateway** - Ozow (80% SA instant EFT market, 1.5% fees)
- **ARCH-21: Secondary Payment Gateway** - PayFast (cards, SnapScan, Zapper)
- **ARCH-22: Payment Architecture** - Strategy pattern with abstracted interface for easy provider swapping
- **ARCH-23: Payment Implementation** - Deferred to pre-launch, interface ready in MVP

**From Architecture - Naming Conventions (CRITICAL):**

- **ARCH-24: Database Naming** - snake_case for tables (plural), columns, foreign keys
- **ARCH-25: API Naming** - snake_case for endpoints, path params, query params, request/response JSON
- **ARCH-26: TypeScript Naming** - camelCase for functions/variables, PascalCase for components/types
- **ARCH-27: ID Format** - UUIDs (v4) for all primary keys, never auto-increment integers

**From Architecture - Multi-Tenancy (CRITICAL):**

- **ARCH-28: Gym Data Isolation** - Strictly isolated per gym, row-level security on all gym tables
- **ARCH-29: Consumer Profiles** - Platform-owned shared identity, one profile many gym relationships
- **ARCH-30: Tenant Filtering** - Every gym-scoped query MUST include gym_id filter

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1 | Epic 1 | User registration (email, social, OTP) |
| FR2 | Epic 1 | Session management across devices |
| FR3 | Epic 1 | Password reset via email |
| FR4 | Epic 1 | Profile management |
| FR5 | Epic 1 | Account deletion (POPIA) |
| FR6 | Epic 1 | Role-based access control |
| FR7 | Epic 2 | Gym registration and onboarding |
| FR8 | Epic 2 | Gym profile configuration |
| FR9 | Epic 2 | Operating hours and closures |
| FR10 | Epic 2 | Cancellation policies |
| FR11 | Epic 2 | Marketplace participation toggle |
| FR12 | Epic 2 | SaaS subscription management |
| FR13 | Epic 2 | Member data import |
| FR14 | Epic 4 | Consumer multi-gym linking |
| FR15 | Epic 4 | Membership overview |
| FR16 | Epic 4 | Payment method management |
| FR17 | Epic 4 | Membership tier changes |
| FR18 | Epic 4 | Benefits and usage display |
| FR19 | Epic 4 | Digital waiver acceptance |
| FR20 | Epic 4 | Gym member list view |
| FR21 | Epic 3 | Staff creation and roles |
| FR22 | Epic 3 | Permission configuration |
| FR23 | Epic 3 | Working hours management |
| FR24 | Epic 3 | Instructor pay rates |
| FR25 | Epic 3 | Instructor schedule and earnings |
| FR26 | Epic 3 | Role-based feature access |
| FR27 | Epic 2 | Space creation and management |
| FR28 | Epic 2 | Space capacity limits |
| FR29 | Epic 2 | Space amenities and equipment |
| FR30 | Epic 2 | Double-booking prevention |
| FR31 | Epic 5 | Class templates with recurring schedules |
| FR32 | Epic 5 | Individual session scheduling |
| FR33 | Epic 5 | Instructor assignment |
| FR34 | Epic 5 | Space assignment |
| FR35 | Epic 5 | Approval workflow |
| FR36 | Epic 5 | Class cancellation with notifications |
| FR37 | Epic 5 | Capacity and waitlist limits |
| FR38 | Epic 5 | Marketplace pricing |
| FR39 | Epic 6 | Class booking |
| FR40 | Epic 6 | Booking cancellation |
| FR41 | Epic 6 | Waitlist joining |
| FR42 | Epic 6 | Automatic waitlist offers |
| FR43 | Epic 6 | Waitlist confirmation window |
| FR44 | Epic 6 | QR code display |
| FR45 | Epic 6 | QR code scanning |
| FR46 | Epic 6 | Phone/name lookup fallback |
| FR47 | Epic 6 | Membership validation |
| FR48 | Epic 6 | Booking source tracking |
| FR49 | Epic 7 | Cross-gym class browsing |
| FR50 | Epic 7 | Class filtering |
| FR51 | Epic 7 | Gym profile and class details |
| FR52 | Epic 7 | Marketplace subscriptions |
| FR53 | Epic 7 | Pay-per-class bookings |
| FR54 | Epic 7 | Credit tracking |
| FR55 | Epic 7 | Class sharing |
| FR56 | Epic 7 | Friend invites |
| FR57 | Epic 8 | Abstracted payment interface |
| FR58 | Epic 8 | Gym payment dashboard |
| FR59 | Epic 8 | Failed payment detection |
| FR60 | Epic 8 | Automatic payment retry |
| FR61 | Epic 8 | Marketplace payout reports |
| FR62 | Epic 8 | Consumer payment history |
| FR63 | Epic 9 | Booking confirmations |
| FR64 | Epic 9 | Class reminders |
| FR65 | Epic 9 | Waitlist notifications |
| FR66 | Epic 9 | Payment alerts |
| FR67 | Epic 9 | Gym-to-member messaging |
| FR68 | Epic 9 | WhatsApp notifications |
| FR69 | Epic 9 | Notification preferences |
| FR70 | Epic 10 | Revenue reports |
| FR71 | Epic 10 | Attendance reports |
| FR72 | Epic 10 | Membership health reports |
| FR73 | Epic 10 | Class performance reports |
| FR74 | Epic 10 | Staff performance reports |
| FR75 | Epic 10 | Consumer class history |
| FR76 | Epic 10 | At-risk member flagging |
| FR77 | Epic 11 | Gym application review |
| FR78 | Epic 11 | Platform gym management |
| FR79 | Epic 11 | Consumer complaint handling |
| FR80 | Epic 11 | Account credit issuance |
| FR81 | Epic 11 | Platform health monitoring |
| FR82 | Epic 11 | Gym-level data access |
| FR83 | Epic 11 | Real-time class availability |
| FR84 | Epic 11 | Webhook events |
| FR85 | Epic 6 | Offline QR sync |

---

## Epic List

### Epic 0: Project Foundation & Developer Experience
**Goal:** Development team has a fully working local development environment with all tooling configured.

**FRs covered:** None (infrastructure-only)
**ARCHs covered:** ARCH-1 through ARCH-9, ARCH-24 through ARCH-30

**Strategy:** Local-first development. Build and test the entire system locally before deploying to production infrastructure. Production deployment is deferred to Epic 16.

**Delivers:**
- FastAPI backend initialized from Full Stack Template
- Turborepo monorepo with gym-web, consumer-web, consumer-mobile, gym-mobile apps
- PostgreSQL 16 + Redis running locally via Docker Compose
- Local CI (linting + tests on push)
- Hey API codegen configured
- Naming conventions and multi-tenancy patterns established
- Seed data scripts for testing
- Local E2E testing setup

**Development Priority:**
1. Gym Web (validate gym features first)
2. Consumer Web (validate consumer features)
3. Consumer Mobile (port validated features)
4. Gym Mobile (add QR scanner)

**Stories:**
| ID | Story | Description |
|----|-------|-------------|
| 0-1 | Initialize backend with FastAPI template | Set up FastAPI Full Stack Template with project structure |
| 0-2 | Initialize frontend monorepo with Turborepo | Create pnpm workspace with all 4 apps and shared packages |
| 0-3 | Configure shared UI package with NativeWind/Tailwind | Set up design system that works across web and mobile |
| 0-4 | Setup local development environment | Docker Compose for Postgres + Redis, environment configuration |
| 0-5 | Configure local CI (lint and tests) | GitHub Actions for linting, type-checking, and tests (no deployment) |
| 0-6 | Configure Hey API for client generation | Generate TypeScript API client from OpenAPI schema |
| 0-7 | Establish multi-tenancy patterns and base models | SQLModel base classes, gym_id filtering, row-level security |
| 0-8 | Create seed data scripts | Scripts to populate database with realistic test data |
| 0-9 | Configure local E2E testing setup | Playwright for web, Detox for mobile E2E tests |

---

### Epic 1: Authentication & Identity Platform
**Goal:** All users can securely register, login, and manage their accounts across all apps.

**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6
**ARCHs covered:** ARCH-10 through ARCH-14

**Delivers:**
- Consumer registration (email, Google, Apple, phone OTP)
- Staff authentication (email, OTP)
- JWT tokens with refresh rotation
- RBAC with role claims
- Profile management
- POPIA-compliant account deletion

---

### Epic 2: Gym Onboarding & Configuration
**Goal:** Gym owners can register their gym, configure spaces, and set up operational settings.

**FRs covered:** FR7, FR8, FR9, FR10, FR11, FR12, FR13, FR27, FR28, FR29, FR30

**Delivers:**
- Gym registration and onboarding wizard
- Gym profile (name, logo, photos, location)
- Operating hours and holiday closures
- Space/studio management with capacity
- Cancellation policies
- Marketplace participation toggle
- Member data spreadsheet import

---

### Epic 3: Staff Management & Permissions
**Goal:** Gym owners can add staff members with role-appropriate permissions.

**FRs covered:** FR21, FR22, FR23, FR24, FR25, FR26

**Delivers:**
- Staff creation with roles (Manager, Front Desk, Instructor)
- Permission configuration per role
- Working hours and shift management
- Instructor pay rates
- Staff earnings visibility

---

### Epic 4: Membership Plans & Consumer Enrollment
**Goal:** Gyms can create membership plans; consumers can enroll and manage their memberships.

**FRs covered:** FR14, FR15, FR16, FR17, FR18, FR19, FR20

**Delivers:**
- Membership plan creation with benefits
- Consumer multi-gym linking
- Membership tier upgrades/downgrades
- Payment method management
- Digital waiver acceptance
- Gym member list view

---

### Epic 5: Class Scheduling System
**Goal:** Gym staff can create, schedule, and manage classes with approval workflows.

**FRs covered:** FR31, FR32, FR33, FR34, FR35, FR36, FR37, FR38

**Delivers:**
- Class template creation
- Individual session scheduling
- Recurring schedule support
- Instructor and space assignment
- Approval workflow (instructor ↔ manager)
- Class cancellation with notifications
- Marketplace pricing configuration

---

### Epic 6: Booking & Check-in
**Goal:** Consumers can book classes and check in at gyms via QR code.

**FRs covered:** FR39, FR40, FR41, FR42, FR43, FR44, FR45, FR46, FR47, FR48, FR85

**Delivers:**
- Class booking (membership or pay-per-class)
- Booking cancellation with policy enforcement
- Waitlist with timed confirmation
- QR code generation and display
- Staff QR scanner
- Phone/name lookup fallback
- Membership validation on check-in
- Booking source tracking (direct vs marketplace)
- Offline QR sync (CRITICAL for SA)

---

### Epic 7: Marketplace Discovery & Subscriptions
**Goal:** Consumers can discover classes across gyms and subscribe to marketplace packages.

**FRs covered:** FR49, FR50, FR51, FR52, FR53, FR54, FR55, FR56

**Delivers:**
- Cross-gym class browsing
- Filters (type, location, date/time, price, availability)
- Gym profile and class detail views
- Marketplace subscriptions (8/12/unlimited classes)
- Pay-per-class bookings
- Credit tracking and usage
- Share and invite functionality

---

### Epic 8: Payments & Billing
**Goal:** Payments flow seamlessly for memberships, bookings, and marketplace subscriptions.

**FRs covered:** FR57, FR58, FR59, FR60, FR61, FR62
**ARCHs covered:** ARCH-20 through ARCH-23

**Delivers:**
- Abstracted payment interface (Ozow + PayFast ready)
- Gym payment dashboard
- Failed payment detection and retry
- Marketplace payout reports
- Consumer payment history

---

### Epic 9: Notifications & Communication
**Goal:** Users receive timely, configurable notifications via push, email, and WhatsApp.

**FRs covered:** FR63, FR64, FR65, FR66, FR67, FR68, FR69

**Delivers:**
- Booking confirmations (push + email)
- Class reminders
- Waitlist notifications
- Payment alerts
- Gym-to-member messaging
- WhatsApp for critical notifications
- Consumer preference configuration

---

### Epic 10: Reporting & Analytics
**Goal:** Gym owners have full visibility into business health and can identify at-risk members.

**FRs covered:** FR70, FR71, FR72, FR73, FR74, FR75, FR76

**Delivers:**
- Revenue reports (membership + marketplace)
- Attendance and check-in reports
- Membership health reports (active, at-risk, churned)
- Class performance (fill rate, attendance)
- Staff performance reports
- Consumer class history and stats
- At-risk member flagging

---

### Epic 11: Platform Administration & Real-time
**Goal:** Platform team can manage gyms, resolve issues, and provide real-time updates.

**FRs covered:** FR77, FR78, FR79, FR80, FR81, FR82, FR83, FR84

**Delivers:**
- Gym application review and approval
- Platform-wide gym management
- Consumer complaint handling
- Account credit issuance
- Platform health monitoring
- Gym-level data access for support
- Real-time class availability (WebSocket)
- Webhook events for gym integrations

---

## Epic 0: Project Foundation & Developer Experience (Detailed Stories)

**Goal:** Development team has a fully working local development environment with all tooling configured.

**Strategy:** Local-first development. Build and test the entire system locally before deploying to production infrastructure. Production deployment is deferred to Epic 16.

**ARCHs covered:** ARCH-1 through ARCH-9, ARCH-24 through ARCH-30

**Development Priority (Web-First Validation):**
1. Gym Web (`manage.studioloop.co.za`) — validate gym features first
2. Consumer Web (`app.studioloop.co.za`) — validate consumer features
3. Consumer Mobile (iOS + Android) — port validated features
4. Gym Mobile (iOS + Android) — add QR scanner

---

### Story 0.1: Initialize Backend with FastAPI Template

As a **developer**,
I want the backend initialized from the FastAPI Full Stack Template,
So that I have a production-ready foundation with established patterns.

**Acceptance Criteria:**

**Given** a new project directory
**When** `copier copy https://github.com/fastapi/full-stack-fastapi-template backend --trust` is executed
**Then** the backend directory contains a working FastAPI application
**And** the directory structure follows: `app/api/routes/`, `app/models/`, `app/schemas/`, `app/services/`, `app/repositories/`
**And** `pyproject.toml` is configured with Python 3.11+ dependencies
**And** Alembic is configured for database migrations
**And** running `uv run uvicorn app.main:app --reload` starts the server successfully
**And** the health endpoint responds at `/health`

---

### Story 0.2: Initialize Frontend Monorepo with Turborepo

As a **developer**,
I want a Turborepo monorepo with pnpm workspaces,
So that I can share code across gym-web, consumer-web, consumer-mobile, and gym-mobile apps.

**Acceptance Criteria:**

**Given** a new frontend directory
**When** I initialize the monorepo with `pnpm init` and Turborepo
**Then** `pnpm-workspace.yaml` defines `apps/*` and `packages/*`
**And** `turbo.json` configures build/dev/lint/test pipelines
**And** `apps/gym-web/` is scaffolded as a Vite + React project (Priority 1 - `manage.studioloop.co.za`)
**And** `apps/consumer-web/` is scaffolded as a Vite + React project (Priority 2 - `app.studioloop.co.za`)
**And** `apps/consumer-mobile/` is scaffolded as an Expo React Native project (Priority 3)
**And** `apps/gym-mobile/` is scaffolded as an Expo React Native project (Priority 4)
**And** `packages/api-client/` exists for generated API client
**And** `packages/ui/` exists for shared components
**And** `packages/utils/` exists for shared utilities
**And** running `pnpm dev` starts all apps concurrently
**And** TypeScript strict mode is enabled with shared `tsconfig.base.json`

---

### Story 0.3: Configure Shared UI Package with NativeWind/Tailwind

As a **developer**,
I want a shared UI package using NativeWind (mobile) and Tailwind CSS (web),
So that components have consistent styling across all 4 frontend apps.

**Acceptance Criteria:**

**Given** the packages/ui directory exists
**When** I configure NativeWind v4 for mobile apps and Tailwind CSS v4 for web apps
**Then** `packages/ui/tailwind.config.js` defines shared design tokens (colors, spacing, typography)
**And** mobile apps (consumer-mobile, gym-mobile) import and use NativeWind components with `className` props
**And** web apps (gym-web, consumer-web) import and use Tailwind-styled components
**And** Button, Input, Card, and Modal primitives are created and functional on all platforms
**And** components render correctly on iOS, Android, and web (both gym-web and consumer-web)

---

### Story 0.4: Setup Local Development Environment

As a **developer**,
I want PostgreSQL and Redis running locally via Docker Compose,
So that I can develop and test without cloud dependencies.

**Acceptance Criteria:**

**Given** Docker is installed on the development machine
**When** I run `docker compose -f docker-compose.local.yml up -d`
**Then** PostgreSQL 17 is running and accessible at `localhost:5432`
**And** Redis 7 is running and accessible at `localhost:6379`
**And** Adminer is available at `localhost:8080` for database management
**And** `.env` file contains correct `POSTGRES_*` and `REDIS_URL` variables
**And** backend can connect to both PostgreSQL and Redis locally
**And** `docker compose -f docker-compose.local.yml down` cleanly stops all services
**And** data persists in Docker volumes across restarts

---

### Story 0.5: Configure Local CI (Lint and Tests)

As a **developer**,
I want CI pipelines that lint and test code on every PR,
So that code quality is maintained during local development.

**Acceptance Criteria:**

**Given** a GitHub repository with the codebase
**When** I configure GitHub Actions workflows
**Then** `.github/workflows/ci.yml` runs lint, type-check, and tests on every PR
**And** backend linting runs with ruff
**And** backend tests run with pytest
**And** frontend linting runs with ESLint
**And** frontend type-checking runs with TypeScript
**And** frontend tests run with Jest
**And** Turborepo caching is enabled for faster CI runs
**And** PRs are blocked if CI fails
**And** no deployment workflows are configured (deferred to Epic 16)

---

### Story 0.6: Configure Hey API for Client Generation

As a **developer**,
I want the API client auto-generated from OpenAPI schema with TanStack Query hooks,
So that frontend apps have type-safe API access.

**Acceptance Criteria:**

**Given** the backend exposes an OpenAPI schema at `/openapi.json`
**When** I run the Hey API generation script
**Then** `packages/api-client/src/generated/` contains TypeScript types for all schemas
**And** `packages/api-client/src/generated/` contains service functions for all endpoints
**And** `packages/api-client/src/hooks/` contains TanStack Query hooks wrappers
**And** all apps can import and use `@sl/api-client` package
**And** API calls use snake_case field names per ARCH-25
**And** regeneration can be triggered via `pnpm generate:api`

---

### Story 0.7: Establish Multi-Tenancy Patterns and Base Models

As a **developer**,
I want base models and patterns for multi-tenant gym data isolation,
So that all future models follow consistent tenant security.

**Acceptance Criteria:**

**Given** the backend is initialized
**When** I create base model patterns
**Then** `app/models/base.py` defines `BaseModel` with UUID primary key, `created_at`, `updated_at`
**And** `app/models/base.py` defines `GymScopedModel` mixin with `gym_id` foreign key
**And** `app/core/dependencies.py` provides `get_current_gym()` dependency
**And** repository base class automatically filters by `gym_id` for gym-scoped models
**And** naming conventions follow snake_case per ARCH-24 (e.g., `created_at`, not `createdAt`)
**And** all IDs use UUIDs per ARCH-27
**And** API error response format matches architecture specification

---

### Story 0.8: Create Seed Data Scripts

As a **developer**,
I want scripts to populate the database with realistic test data,
So that I can test features with meaningful data during development.

**Acceptance Criteria:**

**Given** the database schema is migrated
**When** I run `python scripts/seed.py` (or equivalent)
**Then** sample gyms are created with realistic SA gym names and locations
**And** sample consumers are created with SA-style names and phone numbers
**And** sample staff members are created with different roles (Owner, Manager, Front Desk, Instructor)
**And** sample membership plans are created (Basic, Premium, Unlimited)
**And** sample class templates are created (Yoga, Spin, HIIT, CrossFit)
**And** sample class sessions are scheduled for the next 14 days
**And** sample bookings exist for testing check-in flows
**And** seed data is idempotent (can be run multiple times safely)
**And** a `--reset` flag clears existing seed data before re-seeding

---

### Story 0.9: Configure Local E2E Testing Setup

As a **developer**,
I want E2E testing configured for web and mobile apps,
So that I can verify complete user flows work correctly.

**Acceptance Criteria:**

**Given** the local development environment is running
**When** I configure E2E testing
**Then** Playwright is configured for gym-web and consumer-web apps
**And** `pnpm test:e2e` runs web E2E tests against local backend
**And** basic smoke tests exist: login, view dashboard, navigate pages
**And** tests run in headless mode by default, with `--headed` option available
**And** Detox is configured for consumer-mobile and gym-mobile apps (optional, can be deferred)
**And** test database can be reset between test runs
**And** E2E tests are NOT included in CI (run manually or in separate workflow)

---

## Epic 16: Production Deployment

**Goal:** Deploy the complete system to production infrastructure after local development is complete.

**Note:** This epic was created to hold infrastructure stories deferred from Epic 0 as part of the local-first development strategy. These stories should only be executed after all features are working locally.

**FRs covered:** None (infrastructure-only)
**ARCHs covered:** ARCH-3, ARCH-4, ARCH-5, ARCH-7, ARCH-8, ARCH-9

**Delivers:**
- PostgreSQL 16 + Redis deployed to Fly.io Johannesburg (POPIA compliance)
- Backend deployed to Fly.io
- Web apps deployed to Vercel or Fly.io
- Mobile apps built via EAS Build
- CI/CD deployment pipelines
- Production monitoring (Sentry)
- SSL/TLS configured for all domains

**Stories:**
| ID | Story | Description |
|----|-------|-------------|
| 16-1 | Deploy database infrastructure to Fly.io | PostgreSQL + Redis in Johannesburg region |
| 16-2 | Configure CI/CD deployment pipelines | GitHub Actions for automated deployments |
| 16-3 | Setup monitoring and error tracking | Sentry integration for all apps |
| 16-4 | Configure production domains and SSL | DNS, SSL certificates, domain routing |
| 16-5 | Deploy backend to Fly.io | FastAPI app deployed with secrets |
| 16-6 | Deploy web apps to Vercel or Fly.io | gym-web and consumer-web production builds |
| 16-7 | Configure EAS Build for mobile apps | iOS and Android builds for app stores |

---

## Epic 1: Authentication & Identity Platform

**Goal:** All users can securely register, login, and manage their accounts across all apps.

**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6
**ARCHs covered:** ARCH-10 through ARCH-14

**Platforms:** All platforms (Consumer Web, Consumer Mobile, Gym Web, Gym Mobile)
- **Consumer registration/login:** Consumer Web ✅ + Consumer Mobile ✅
- **Staff/Owner login:** Gym Web ✅ + Gym Mobile ✅

---

### Story 1.1: Consumer Email Registration

As a **consumer**,
I want to register with my email and password,
So that I can create an account to use the platform.

**Acceptance Criteria:**

**Given** the Consumer Web or Consumer Mobile registration screen
**When** I enter a valid email, password (min 8 chars), first name, and last name
**Then** my account is created with `role: consumer`
**And** my password is hashed with Argon2 per ARCH-11
**And** I receive a verification email
**And** I am redirected to verify my email before login
**And** duplicate emails are rejected with appropriate error message
**And** `consumers` table is created with UUID primary key

---

### Story 1.2: Consumer Email Login

As a **consumer**,
I want to login with my email and password,
So that I can access my account.

**Acceptance Criteria:**

**Given** I have a verified consumer account
**When** I enter correct email and password
**Then** I receive a JWT access token (<24h expiry) and refresh token
**And** tokens are stored securely in MMKV
**And** I am redirected to the home screen
**And** invalid credentials return 401 with error message
**And** unverified accounts cannot login

---

### Story 1.3: Staff Email Login

As a **gym staff member**,
I want to login with my email and password,
So that I can access the gym management app.

**Acceptance Criteria:**

**Given** I have an active staff account at a gym
**When** I enter correct email and password
**Then** I receive a JWT with role claims (owner/manager/front_desk/instructor)
**And** the token includes `gym_id` for tenant context
**And** I am redirected to the gym dashboard
**And** `staff` table is created with `gym_id` foreign key
**And** inactive staff accounts cannot login

---

### Story 1.4: JWT Token Refresh

As a **user**,
I want my session to stay active without re-entering credentials,
So that I have a seamless experience.

**Acceptance Criteria:**

**Given** I have a valid refresh token
**When** my access token expires
**Then** the app automatically requests a new access token using the refresh token
**And** the old refresh token is invalidated (rotation per ARCH-12)
**And** a new refresh token is issued
**And** if refresh token is invalid/expired, I am redirected to login
**And** token refresh happens transparently without user action

---

### Story 1.5: Password Reset via Email

As a **user**,
I want to reset my password via email,
So that I can recover my account if I forget my password.

**Acceptance Criteria:**

**Given** I request a password reset with my registered email
**When** I submit the request
**Then** a reset link is sent to my email (valid for 1 hour)
**And** clicking the link opens a password reset screen
**And** I can set a new password (min 8 chars)
**And** all existing sessions are invalidated after reset
**And** unregistered emails do not reveal account existence (security)

---

### Story 1.6: User Profile Management

As a **user**,
I want to update my profile information,
So that my account details are current.

**Acceptance Criteria:**

**Given** I am logged in
**When** I navigate to profile settings
**Then** I can update my first name, last name, and phone number
**And** I can upload or change my profile photo
**And** changes are saved immediately
**And** profile photo is stored and served via CDN
**And** phone number validates SA format (+27...)

---

### Story 1.7: POPIA Account Deletion

As a **consumer**,
I want to delete my account and all associated data,
So that I can exercise my POPIA right to erasure.

**Acceptance Criteria:**

**Given** I am logged in and request account deletion
**When** I confirm the deletion request
**Then** my account is marked for deletion
**And** I receive confirmation email
**And** all my personal data is deleted within 30 days per NFR13
**And** my bookings are anonymized (not deleted for gym records)
**And** my memberships are cancelled
**And** I am logged out and cannot login again

---

### Story 1.8: Role-Based Access Control

As a **system**,
I want to enforce role-based permissions,
So that users only access features appropriate to their role.

**Acceptance Criteria:**

**Given** a user with a specific role (consumer, owner, manager, front_desk, instructor, platform_admin)
**When** they attempt to access an API endpoint
**Then** the endpoint validates the role from JWT claims
**And** unauthorized roles receive 403 Forbidden
**And** gym-scoped endpoints validate `gym_id` claim matches requested resource
**And** consumers cannot access gym management endpoints
**And** front_desk cannot access owner-only features (billing, staff management)

---

### Story 1.9: Google Social Login

As a **consumer**,
I want to register/login with my Google account,
So that I can use the platform without creating a new password.

**Acceptance Criteria:**

**Given** the Google login button on auth screens
**When** I authenticate with Google
**Then** a consumer account is created/linked using my Google email
**And** my Google profile photo is imported (optional)
**And** I receive JWT tokens as with email login
**And** I can later add a password to enable email login
**And** existing accounts with same email are linked (not duplicated)

---

### Story 1.10: Apple Social Login

As a **iOS consumer**,
I want to register/login with my Apple ID,
So that I can use Sign in with Apple for privacy.

**Acceptance Criteria:**

**Given** the Apple login button on iOS auth screens
**When** I authenticate with Apple
**Then** a consumer account is created using Apple-provided email (real or relay)
**And** I receive JWT tokens
**And** Hide My Email relay addresses are supported
**And** Apple login meets App Store requirements
**And** existing accounts with same email are linked

---

## Epic 2: Gym Onboarding & Configuration

**Goal:** Gym owners can register their gym, configure spaces, and set up operational settings.

**FRs covered:** FR7, FR8, FR9, FR10, FR11, FR12, FR13, FR27, FR28, FR29, FR30

**Platforms:** Gym Web ✅ + Gym Mobile ✅ (full configuration available on both, but Gym Web recommended for initial setup)

---

### Story 2.1: Gym Registration and Owner Account

As a **gym owner**,
I want to register my gym on StudioLoop,
So that I can start using the platform to manage my business.

**Acceptance Criteria:**

**Given** a new gym owner visiting the registration page
**When** I enter my email, password, gym name, and contact details
**Then** a consumer account is created with `role: owner`
**And** a `gyms` table record is created with UUID primary key
**And** the owner is linked to the gym via `staff` table with `role: owner`
**And** I receive a verification email
**And** `gyms` table includes: `name`, `slug` (unique URL-friendly), `contact_email`, `contact_phone`, `is_active`

---

### Story 2.2: Gym Profile Configuration

As a **gym owner**,
I want to configure my gym's public profile,
So that consumers can learn about my gym.

**Acceptance Criteria:**

**Given** I am logged in as a gym owner
**When** I navigate to gym profile settings
**Then** I can set gym name, description, and tagline
**And** I can upload a logo and cover photos (gallery)
**And** I can set the gym address with map location (lat/lng via PostGIS)
**And** I can add contact email and phone number
**And** changes are saved and visible on the gym's public profile
**And** photos are stored and served via CDN

---

### Story 2.3: Operating Hours Configuration

As a **gym owner**,
I want to set my gym's operating hours,
So that members know when we're open.

**Acceptance Criteria:**

**Given** I am on the gym settings page
**When** I configure operating hours
**Then** I can set open/close times for each day of the week
**And** I can mark days as closed
**And** I can set different hours for different days
**And** operating hours are stored as JSON in `gyms.business_hours`
**And** operating hours are displayed on the gym's public profile

---

### Story 2.4: Holiday Closures Management

As a **gym owner**,
I want to set holiday closures,
So that members know when we're closed for special dates.

**Acceptance Criteria:**

**Given** I am on the gym settings page
**When** I add a holiday closure
**Then** I can select a date and optionally a reason (e.g., "Christmas Day")
**And** I can add multiple closures
**And** I can remove existing closures
**And** closures are stored in a `gym_closures` table
**And** classes cannot be scheduled on closure dates
**And** closures are displayed on the gym's public profile

---

### Story 2.5: Cancellation Policy Configuration

As a **gym owner**,
I want to set my gym's cancellation policy,
So that members understand the rules for cancelling bookings.

**Acceptance Criteria:**

**Given** I am on the gym settings page
**When** I configure cancellation policy
**Then** I can set the cancellation window (e.g., 2, 6, 12, 24 hours before class)
**And** I can set the no-show penalty (none, credit lost, fee)
**And** the policy is displayed on class detail screens before booking
**And** the policy is enforced when consumers attempt to cancel
**And** settings are stored in `gyms.settings` JSON field

---

### Story 2.6: Marketplace Participation Toggle

As a **gym owner**,
I want to enable or disable marketplace participation,
So that I can control whether my classes appear on the marketplace.

**Acceptance Criteria:**

**Given** I am on the gym settings page
**When** I toggle marketplace participation
**Then** I can enable or disable marketplace for my entire gym
**And** when disabled, none of my classes appear in marketplace search
**And** when enabled, I can still control individual class marketplace visibility
**And** the toggle is stored in `gyms.settings` JSON field
**And** existing marketplace bookings are honored even if disabled

---

### Story 2.7: SaaS Subscription Tier View

As a **gym owner**,
I want to view my SaaS subscription details,
So that I understand my plan and limits.

**Acceptance Criteria:**

**Given** I am on the gym settings page
**When** I view subscription details
**Then** I can see my current tier (Starter, Growth, Pro)
**And** I can see my member limit and current count
**And** I can see my staff limit and current count
**And** I can see my renewal date
**And** I can see a link to upgrade (future payment integration)
**And** subscription tier is stored in `gyms.subscription_tier` enum

---

### Story 2.8: Space Creation and Management

As a **gym owner**,
I want to create and manage spaces (rooms/studios),
So that I can schedule classes in specific locations.

**Acceptance Criteria:**

**Given** I am on the spaces management page
**When** I create a new space
**Then** I can enter name, capacity, and description
**And** a `spaces` table record is created with `gym_id` foreign key
**And** I can view a list of all spaces for my gym
**And** I can edit existing spaces
**And** I can deactivate (soft delete) spaces that are no longer used
**And** deactivated spaces are not available for new class scheduling

---

### Story 2.9: Space Amenities and Equipment

As a **gym owner**,
I want to specify amenities and equipment for each space,
So that staff can choose appropriate spaces for classes.

**Acceptance Criteria:**

**Given** I am editing a space
**When** I configure amenities and equipment
**Then** I can select from predefined equipment (mats, bikes, weights, TRX, etc.)
**And** I can select from predefined amenities (mirrors, sound system, AC, natural light, etc.)
**And** I can add custom equipment/amenities
**And** equipment and amenities are stored as arrays in `spaces` table
**And** this information is displayed when scheduling classes

---

### Story 2.10: Space Double-Booking Prevention

As a **system**,
I want to prevent double-booking of spaces,
So that no two classes are scheduled in the same space at the same time.

**Acceptance Criteria:**

**Given** a space with an existing class session
**When** staff attempts to schedule another class in the same space at overlapping times
**Then** the system rejects the booking with a clear error message
**And** the system suggests alternative available spaces
**And** the check considers start_time and end_time of both sessions
**And** cancelled sessions do not block new bookings

---

### Story 2.11: Member Data Spreadsheet Import

As a **gym owner**,
I want to import my existing members from a spreadsheet,
So that I can migrate to StudioLoop without manually entering each member.

**Acceptance Criteria:**

**Given** I have a CSV/Excel file with member data
**When** I upload the file on the import page
**Then** the system parses the file and shows a preview of detected members
**And** I can map columns to fields (name, email, phone, membership tier)
**And** I can review and confirm the import
**And** consumer accounts are created for each member (pending email verification)
**And** memberships are created linking consumers to my gym
**And** duplicate emails are flagged for manual review
**And** import results show success/error counts

---

## Epic 3: Staff Management & Permissions

**Goal:** Gym owners can add staff members with role-appropriate permissions.

**FRs covered:** FR21, FR22, FR23, FR24, FR25, FR26

**Platforms:** Gym Web ✅ + Gym Mobile ✅

---

### Story 3.1: Add Staff Member

As a **gym owner**,
I want to add staff members to my gym,
So that they can help manage operations.

**Acceptance Criteria:**

**Given** I am logged in as a gym owner
**When** I add a new staff member
**Then** I can enter their email, name, phone, and select a role (manager, front_desk, instructor)
**And** a `staff` record is created with `gym_id` foreign key
**And** an invitation email is sent to the staff member
**And** the staff member can set their password via the invite link
**And** I can see the staff member in my staff list with "pending" status until they accept

---

### Story 3.2: Staff Role Assignment

As a **gym owner**,
I want to assign roles to staff members,
So that they have appropriate access levels.

**Acceptance Criteria:**

**Given** I have staff members in my gym
**When** I assign or change a staff member's role
**Then** I can select from: manager, front_desk, instructor
**And** the role is stored in `staff.role` enum field
**And** the staff member's JWT token reflects the new role on next login
**And** I can change roles at any time
**And** only owners can assign the manager role

---

### Story 3.3: Staff Permission Matrix

As a **system**,
I want to enforce permissions based on staff roles,
So that staff only access features appropriate to their role.

**Acceptance Criteria:**

**Given** a staff member with a specific role
**When** they access gym management features
**Then** managers can: manage classes, members, bookings, view reports, but NOT billing or staff
**And** front_desk can: check-in members, create bookings, view member info, but NOT reports or settings
**And** instructors can: view own schedule, own class attendance, own earnings, but NOT other gym features
**And** unauthorized access returns 403 Forbidden
**And** permission checks are enforced at API level

---

### Story 3.4: Staff Working Hours Configuration

As a **gym owner**,
I want to set working hours for staff members,
So that I can track their schedules.

**Acceptance Criteria:**

**Given** I am viewing a staff member's profile
**When** I configure their working hours
**Then** I can set their regular schedule (days and hours)
**And** I can assign them to specific shifts
**And** a `staff_shifts` table stores shift records with `staff_id`, `gym_id`, `start_time`, `end_time`
**And** shifts are displayed on a weekly calendar view
**And** staff can view their own assigned shifts

---

### Story 3.5: Instructor Pay Rate Configuration

As a **gym owner**,
I want to set pay rates for instructors,
So that I can track their earnings per class.

**Acceptance Criteria:**

**Given** a staff member with role: instructor
**When** I configure their pay rate
**Then** I can set a default pay rate per class (in ZAR)
**And** I can set different rates for different class types (optional)
**And** the rate is stored in `staff.pay_rate_per_class` decimal field
**And** instructor earnings are calculated based on classes taught

---

### Story 3.6: Instructor Schedule View

As an **instructor**,
I want to view my scheduled classes,
So that I know when and where I'm teaching.

**Acceptance Criteria:**

**Given** I am logged in as an instructor
**When** I view my schedule
**Then** I see a calendar view of my assigned classes
**And** each class shows: name, date, time, space, and expected attendance
**And** I can filter by date range
**And** I can see classes for today, this week, or this month
**And** past classes are marked as completed

---

### Story 3.7: Instructor Earnings View

As an **instructor**,
I want to view my earnings,
So that I can track my income.

**Acceptance Criteria:**

**Given** I am logged in as an instructor
**When** I view my earnings
**Then** I see total earnings for the current period (month)
**And** I see a breakdown by class: class name, date, pay rate, earnings
**And** I can filter by date range
**And** earnings are calculated as: classes_taught × pay_rate_per_class
**And** only completed classes count toward earnings

---

### Story 3.8: Deactivate Staff Member

As a **gym owner**,
I want to deactivate staff members,
So that former employees lose access.

**Acceptance Criteria:**

**Given** I have an active staff member
**When** I deactivate them
**Then** their `staff.is_active` is set to false
**And** they can no longer login to the gym management app
**And** their existing sessions are invalidated
**And** their historical data (classes taught, earnings) is preserved
**And** I can reactivate them later if needed

---

## Epic 4: Membership Plans & Consumer Enrollment

**Goal:** Gyms can create membership plans; consumers can enroll and manage their memberships.

**FRs covered:** FR14, FR15, FR16, FR17, FR18, FR19, FR20

**Platform Distribution:**
- **Plan management (Stories 4.1-4.3):** Gym Web ✅ + Gym Mobile ✅
- **Consumer enrollment (Stories 4.4-4.9):** Consumer Web ✅ + Consumer Mobile ✅
- **Gym member views (Stories 4.10-4.11):** Gym Web ✅ + Gym Mobile ✅

---

### Story 4.1: Create Membership Plan

As a **gym owner**,
I want to create membership plans,
So that consumers can choose how to join my gym.

**Acceptance Criteria:**

**Given** I am on the membership plans page
**When** I create a new membership plan
**Then** I can set plan name, description, and price (in ZAR)
**And** I can set billing period (monthly, quarterly, annually)
**And** a `membership_plans` table record is created with `gym_id` foreign key
**And** the plan is visible in the list of available plans
**And** I can create multiple plans for different membership tiers

---

### Story 4.2: Configure Membership Benefits

As a **gym owner**,
I want to configure benefits for each membership plan,
So that members understand what they get.

**Acceptance Criteria:**

**Given** I am editing a membership plan
**When** I configure benefits
**Then** I can set: unlimited gym access (yes/no), off-peak only (with hours)
**And** I can set: classes per month (number or unlimited), allowed class types
**And** I can set: priority booking, advance booking days
**And** I can set: guest passes per month, locker access, towel service, parking
**And** I can set: merchandise discount %, PT discount %
**And** I can set: freeze days per year
**And** benefits are stored as JSON in `membership_plans.benefits`

---

### Story 4.3: Configure Membership Rules

As a **gym owner**,
I want to set rules for membership plans,
So that terms are clear.

**Acceptance Criteria:**

**Given** I am editing a membership plan
**When** I configure rules
**Then** I can set cancellation notice period (e.g., 30 days)
**And** I can enable/disable auto-renewal
**And** rules are stored as JSON in `membership_plans.rules`
**And** rules are displayed to consumers before enrollment

---

### Story 4.4: Consumer Views Gym Membership Plans

As a **consumer**,
I want to view available membership plans at a gym,
So that I can choose the right plan for me.

**Acceptance Criteria:**

**Given** I am viewing a gym's profile
**When** I navigate to membership options
**Then** I see all active membership plans
**And** each plan shows: name, price, billing period, key benefits
**And** I can tap a plan to see full benefit details
**And** I can see "Join" button for each plan

---

### Story 4.5: Consumer Enrolls in Membership

As a **consumer**,
I want to enroll in a gym membership,
So that I can access the gym.

**Acceptance Criteria:**

**Given** I have selected a membership plan
**When** I complete enrollment
**Then** a `memberships` table record is created linking my consumer_id to the gym
**And** the record includes: plan_id, status (active), start_date, end_date (if applicable)
**And** I can see the membership in my "My Memberships" list
**And** I receive a confirmation email
**And** payment is processed (or deferred to payment integration)

---

### Story 4.6: Consumer Views All Memberships

As a **consumer**,
I want to view all my gym memberships in one place,
So that I can manage them easily.

**Acceptance Criteria:**

**Given** I have memberships at one or more gyms
**When** I navigate to "My Memberships"
**Then** I see a list of all my memberships
**And** each shows: gym name, plan name, status, renewal date
**And** I can tap a membership to see full details
**And** memberships with issues (payment failed, expiring) are highlighted

---

### Story 4.7: Consumer Views Membership Benefits

As a **consumer**,
I want to see my membership benefits and usage,
So that I know what I have access to.

**Acceptance Criteria:**

**Given** I am viewing a specific membership
**When** I check benefits
**Then** I see all included benefits
**And** I see usage for limited benefits (e.g., "3 of 8 classes used this month")
**And** I see when limited benefits reset
**And** I see my freeze days remaining (if applicable)

---

### Story 4.8: Consumer Upgrades/Downgrades Membership

As a **consumer**,
I want to change my membership tier,
So that I can adjust my plan as my needs change.

**Acceptance Criteria:**

**Given** I have an active membership
**When** I request to upgrade or downgrade
**Then** I see available alternative plans
**And** I see how the change affects my billing (prorated, next cycle)
**And** I can confirm the change
**And** upgrades take effect immediately
**And** downgrades take effect at next billing cycle

---

### Story 4.9: Consumer Accepts Digital Waiver

As a **consumer**,
I want to accept the gym's waiver digitally,
So that I can complete my membership requirements.

**Acceptance Criteria:**

**Given** the gym requires a waiver for membership
**When** I enroll or am prompted to sign
**Then** I see the waiver text
**And** I can accept by tapping "I Agree" with my name
**And** waiver acceptance is recorded with timestamp
**And** the gym can verify I've signed the waiver
**And** waivers are stored per gym-consumer relationship

---

### Story 4.10: Gym Views Member List

As a **gym owner/manager**,
I want to view all my gym's members,
So that I can manage them.

**Acceptance Criteria:**

**Given** I am on the members management page
**When** I view the member list
**Then** I see all consumers with active or past memberships
**And** I can see: name, email, phone, membership plan, status, join date
**And** I can search by name, email, or phone
**And** I can filter by: plan, status (active, paused, cancelled, expired)
**And** I can tap a member to see full details

---

### Story 4.11: Gym Views Member Details

As a **gym staff member**,
I want to view a member's full details,
So that I can assist them.

**Acceptance Criteria:**

**Given** I am viewing a specific member
**When** I check their details
**Then** I see: profile info, membership details, benefits usage
**And** I see: booking history, check-in history
**And** I see: payment status, outstanding balance (if any)
**And** I can add notes about the member
**And** front_desk role can view but has limited edit access

---

## Epic 5: Class Scheduling System

**Goal:** Gym staff can create, schedule, and manage classes with approval workflows.

**FRs covered:** FR31, FR32, FR33, FR34, FR35, FR36, FR37, FR38

**Platforms:** Gym Web ✅ + Gym Mobile ✅

---

### Story 5.1: Create Class Template

As a **gym owner/manager**,
I want to create class templates,
So that I can define the types of classes my gym offers.

**Acceptance Criteria:**

**Given** I am on the class management page
**When** I create a new class template
**Then** I can set: name, description, category (yoga, pilates, spin, etc.)
**And** I can set: default duration (minutes), default capacity, default price (ZAR)
**And** a `classes` table record is created with `gym_id` foreign key
**And** the template appears in the list of available class types
**And** I can edit or deactivate templates

---

### Story 5.2: Schedule Individual Class Session

As a **gym staff member**,
I want to schedule a class session,
So that members can attend.

**Acceptance Criteria:**

**Given** I have class templates defined
**When** I schedule a new session
**Then** I select a class template
**And** I set date, start time, and end time
**And** I select a space (room/studio)
**And** I assign an instructor
**And** I can override default capacity and price
**And** a `class_sessions` table record is created with `gym_id`, `class_id`, `space_id`, `instructor_id`
**And** session status is set based on approval workflow

---

### Story 5.3: Schedule Recurring Class Sessions

As a **gym owner/manager**,
I want to create recurring class schedules,
So that I don't have to manually schedule each session.

**Acceptance Criteria:**

**Given** I am scheduling a class
**When** I enable recurring schedule
**Then** I can set: repeat weekly on selected days
**And** I can set: end date or number of occurrences
**And** multiple `class_sessions` records are created
**And** each session can be individually modified or cancelled later
**And** I see a preview before confirming bulk creation

---

### Story 5.4: Assign Instructor to Class

As a **gym owner/manager**,
I want to assign instructors to classes,
So that members know who is teaching.

**Acceptance Criteria:**

**Given** I am creating or editing a class session
**When** I assign an instructor
**Then** I see a list of instructors available at that time
**And** I can select one instructor per session
**And** the instructor's name appears on the class listing
**And** the instructor sees this class in their schedule
**And** instructor conflicts (double-booking) are warned

---

### Story 5.5: Class Approval Workflow - Instructor Creates

As an **instructor**,
I want to propose a new class session,
So that I can teach additional classes.

**Acceptance Criteria:**

**Given** I am logged in as an instructor
**When** I create a new class session
**Then** the session status is set to `pending_approval`
**And** a notification is sent to owner/manager
**And** the session is NOT visible to members until approved
**And** I can see my pending sessions with "Awaiting Approval" status

---

### Story 5.6: Class Approval Workflow - Manager Approves

As a **gym owner/manager**,
I want to approve or reject proposed class sessions,
So that I control my gym's schedule.

**Acceptance Criteria:**

**Given** there are sessions pending approval
**When** I view pending sessions
**Then** I see all sessions needing my approval
**And** I can approve (status → `scheduled`) or reject with reason
**And** the instructor is notified of the decision
**And** approved sessions become visible to members
**And** rejected sessions remain hidden

---

### Story 5.7: Class Approval Workflow - Manager Creates

As a **gym owner/manager**,
I want instructors to confirm availability when I schedule them,
So that I don't double-book instructors.

**Acceptance Criteria:**

**Given** I create a session and assign an instructor
**When** the session is created
**Then** the session status is set to `pending_approval`
**And** the assigned instructor is notified to confirm availability
**And** instructor can accept (status → `scheduled`) or decline with reason
**And** declined sessions can be reassigned to another instructor

---

### Story 5.8: Cancel Class Session

As a **gym owner/manager**,
I want to cancel a scheduled class,
So that I can handle changes in availability.

**Acceptance Criteria:**

**Given** a scheduled class session with bookings
**When** I cancel the session
**Then** session status is set to `cancelled`
**And** all booked members are notified
**And** membership class credits are refunded automatically
**And** pay-per-class payments are flagged for refund
**And** I can optionally provide a cancellation reason
**And** the session is removed from schedules but retained for records

---

### Story 5.9: Set Class Capacity and Waitlist

As a **gym owner/manager**,
I want to set capacity and waitlist limits for classes,
So that I can control attendance.

**Acceptance Criteria:**

**Given** I am creating or editing a class session
**When** I set capacity
**Then** I can set max attendees (defaults from space capacity)
**And** I can enable/disable waitlist
**And** I can set max waitlist size
**And** `spots_booked` and `spots_available` are tracked automatically
**And** when capacity is reached, booking shows "Join Waitlist" instead

---

### Story 5.10: Set Marketplace Pricing for Class

As a **gym owner**,
I want to set marketplace pricing for classes,
So that marketplace consumers pay the right price.

**Acceptance Criteria:**

**Given** I am editing a class session
**When** I configure marketplace settings
**Then** I can enable/disable marketplace listing for this session
**And** I can set marketplace price (typically discounted vs direct price)
**And** marketplace-enabled sessions appear in marketplace search
**And** `is_marketplace_enabled` and `marketplace_price` are stored on session
**And** gym-level marketplace toggle overrides individual session settings

---

### Story 5.11: View Class Schedule Calendar

As a **gym staff member**,
I want to view classes on a calendar,
So that I can see the weekly schedule.

**Acceptance Criteria:**

**Given** I am on the schedule page
**When** I view the calendar
**Then** I see a week view with all scheduled sessions
**And** sessions show: class name, time, instructor, spots available
**And** I can filter by: space, instructor, class type
**And** I can navigate between weeks
**And** I can tap a session to view/edit details
**And** colour coding indicates: scheduled, pending, cancelled

---

## Epic 6: Booking & Check-in

**Goal:** Consumers can book classes and check in at gyms via QR code.

**FRs covered:** FR39, FR40, FR41, FR42, FR43, FR44, FR45, FR46, FR47, FR48, FR85

**Platform Distribution:**
- **Booking (Stories 6.1-6.7):** Consumer Web ✅ + Consumer Mobile ✅
- **QR Code Display (Story 6.8):** Consumer Web ✅ + Consumer Mobile ✅
- **QR Scanner (Story 6.9):** Gym Mobile only ✅
- **Manual Check-in (Story 6.10):** Gym Web ✅ (primary) + Gym Mobile ✅ (fallback)
- **Offline Check-in (Story 6.13):** Gym Mobile only ✅

---

### Story 6.1: Book Class with Membership

As a **consumer**,
I want to book a class using my membership,
So that I can attend classes at my gym.

**Acceptance Criteria:**

**Given** I have an active membership with class benefits
**When** I book a class at my gym
**Then** a `bookings` table record is created with `consumer_id`, `session_id`, `gym_id`
**And** `booking_type` is set to `membership_benefit`
**And** `source` is set to `direct`
**And** my class credit is decremented (if limited)
**And** `spots_booked` on the session is incremented
**And** I receive a booking confirmation
**And** the class appears in my "Upcoming Bookings"

---

### Story 6.2: Book Class with Pay-Per-Class

As a **consumer**,
I want to pay for a single class,
So that I can attend without a membership.

**Acceptance Criteria:**

**Given** I am viewing a class at any gym
**When** I book and pay
**Then** a `bookings` record is created with `booking_type: pay_per_class`
**And** `price_paid` is recorded
**And** payment is processed (or flagged for payment integration)
**And** I receive booking confirmation
**And** gym receives the booking notification

---

### Story 6.3: Cancel Booking

As a **consumer**,
I want to cancel my class booking,
So that I can free up my spot if I can't attend.

**Acceptance Criteria:**

**Given** I have a booking for an upcoming class
**When** I cancel the booking
**Then** the gym's cancellation policy is checked
**And** if within policy window: credit is refunded, status → `cancelled`
**And** if outside policy window: no refund, status → `cancelled`, warning shown first
**And** `spots_booked` on the session is decremented
**And** `cancelled_at` timestamp is recorded
**And** waitlist is processed (next person gets the spot)

---

### Story 6.4: Join Waitlist

As a **consumer**,
I want to join the waitlist for a full class,
So that I can attend if a spot opens up.

**Acceptance Criteria:**

**Given** a class session is full but has waitlist enabled
**When** I join the waitlist
**Then** a `waitlist_entries` table record is created
**And** I see my position in the queue
**And** I receive confirmation that I'm on the waitlist
**And** the class shows in my bookings as "Waitlisted"

---

### Story 6.5: Waitlist Spot Offer

As a **system**,
I want to automatically offer spots to waitlisted consumers,
So that cancelled spots are filled quickly.

**Acceptance Criteria:**

**Given** a booked consumer cancels
**When** the spot becomes available
**Then** the first person on waitlist is notified immediately
**And** they have 30 minutes to confirm (configurable)
**And** `waitlist_entries.status` is set to `offered`
**And** `offered_at` and `expires_at` timestamps are recorded
**And** a push notification is sent

---

### Story 6.6: Accept Waitlist Offer

As a **consumer**,
I want to accept a waitlist spot offer,
So that I can secure my place in the class.

**Acceptance Criteria:**

**Given** I received a waitlist spot offer
**When** I accept within the time window
**Then** a booking is created for me
**And** my waitlist entry status → `accepted`
**And** I receive booking confirmation
**And** the spot is no longer available to others

---

### Story 6.7: Waitlist Offer Expiry

As a **system**,
I want to expire unanswered waitlist offers,
So that spots go to the next person.

**Acceptance Criteria:**

**Given** a waitlist offer expires without response
**When** the expiry time passes
**Then** the offer status → `expired`
**And** the next person on waitlist is offered the spot
**And** process repeats until spot is filled or waitlist exhausted
**And** if waitlist exhausted, spot remains available for new bookings

---

### Story 6.8: Consumer QR Code Display

As a **consumer**,
I want to display my QR code for check-in,
So that I can enter the gym and check in to classes.

**Platforms:** Consumer Web ✅ + Consumer Mobile ✅

**Acceptance Criteria:**

**Given** I am a registered consumer on Consumer Web or Consumer Mobile
**When** I tap/click the QR code button
**Then** a full-screen QR code is displayed
**And** the QR encodes my consumer ID (signed/encrypted for security)
**And** QR regenerates periodically (e.g., every 5 minutes) for security
**And** my name is displayed below the QR
**And** if I have a booking today, it's shown on the QR screen
**And** on Consumer Mobile: QR code works offline (cached locally)
**And** on Consumer Web: QR code requires connectivity

---

### Story 6.9: Staff QR Code Scanner

As a **front desk staff member**,
I want to scan member QR codes,
So that I can check them in quickly.

**Platforms:** Gym Mobile only ✅ (requires device camera)

**Acceptance Criteria:**

**Given** I am on the check-in screen in Gym Mobile app
**When** I scan a consumer's QR code using the device camera
**Then** the consumer is identified
**And** their membership status is validated
**And** if valid: check-in is recorded, success confirmation shown
**And** if invalid (expired, wrong gym): error message shown
**And** if they have a class booking: booking is marked as `checked_in`
**And** check-in record is created with timestamp

**Note:** Gym Web uses Manual Check-in (Story 6.10) as primary method since web browsers cannot reliably access device cameras for scanning.

---

### Story 6.10: Manual Check-in Fallback

As a **front desk staff member**,
I want to search for members manually,
So that I can check them in if QR fails.

**Platforms:** Gym Web ✅ (primary method) + Gym Mobile ✅ (fallback)

**Acceptance Criteria:**

**Given** I cannot scan the QR code (or on Gym Web where scanner is unavailable)
**When** I search by phone number or name
**Then** I see matching members
**And** I can select the correct member
**And** I can complete check-in manually
**And** same validation and recording as QR scanner check-in

**Platform Notes:**
- **Gym Web:** This is the PRIMARY check-in method (no QR scanner available)
- **Gym Mobile:** This is a FALLBACK when QR scanning fails

---

### Story 6.11: Membership Validation on Check-in

As a **system**,
I want to validate membership during check-in,
So that only valid members gain access.

**Acceptance Criteria:**

**Given** a consumer is being checked in
**When** validation runs
**Then** membership status is checked (active, not expired)
**And** off-peak restrictions are enforced if applicable
**And** payment status is checked (no failed payments blocking access)
**And** waiver signature is verified if required
**And** clear error messages explain any access denial

---

### Story 6.12: Booking Source Tracking

As a **system**,
I want to track whether bookings are direct or marketplace,
So that gyms can see marketplace ROI.

**Acceptance Criteria:**

**Given** a booking is created
**When** it's saved
**Then** `source` is set to `direct` (via gym) or `marketplace`
**And** gyms can filter bookings by source
**And** reports show breakdown by source
**And** marketplace bookings are flagged for commission calculation

---

### Story 6.13: Offline QR Check-in

As a **front desk staff member**,
I want check-in to work offline,
So that members aren't blocked by connectivity issues.

**Platforms:** Gym Mobile only ✅ (offline capability requires native app storage)

**Acceptance Criteria:**

**Given** the Gym Mobile app loses internet connectivity
**When** I scan a QR code
**Then** the check-in is recorded locally in Expo SQLite
**And** I see a visual indicator that we're in offline mode
**And** check-in succeeds based on cached member data
**And** when connectivity restores, queued check-ins sync to server
**And** conflicts are resolved (server wins for booking status)

**Note:** Gym Web requires internet connectivity for check-in operations.

---

## Epic 7: Marketplace Discovery & Subscriptions

**Goal:** Consumers can discover classes across gyms and subscribe to marketplace packages.

**FRs covered:** FR49, FR50, FR51, FR52, FR53, FR54, FR55, FR56

**Platforms:** Consumer Web ✅ + Consumer Mobile ✅ (class browsing and booking available on both platforms)

---

### Story 7.1: Browse Marketplace Classes

As a **consumer**,
I want to browse classes from all marketplace gyms,
So that I can discover fitness options across Cape Town.

**Acceptance Criteria:**

**Given** I am on the Browse/Discover screen
**When** I view available classes
**Then** I see a list of marketplace-enabled class sessions
**And** each shows: class name, gym name, distance, time, price, spots available
**And** classes are sorted by relevance (distance + time)
**And** only future sessions with spots available are shown
**And** sessions from gyms with marketplace disabled are excluded

---

### Story 7.2: Filter Classes by Type

As a **consumer**,
I want to filter classes by type,
So that I can find the activities I enjoy.

**Acceptance Criteria:**

**Given** I am browsing marketplace classes
**When** I apply the type filter
**Then** I can select one or more class types (yoga, pilates, spin, boxing, HIIT, etc.)
**And** results update to show only matching classes
**And** I can clear filters to see all classes
**And** filter selections persist during my session

---

### Story 7.3: Filter Classes by Location

As a **consumer**,
I want to filter classes by location/distance,
So that I can find classes near me.

**Acceptance Criteria:**

**Given** I am browsing marketplace classes
**When** I apply the distance filter
**Then** I can select: 1km, 2km, 5km, 10km, Any
**And** results show only classes within selected distance
**And** distance is calculated from my current location (GPS)
**And** I can see my location on a map view toggle

---

### Story 7.4: Filter Classes by Date and Time

As a **consumer**,
I want to filter classes by date and time,
So that I can find classes that fit my schedule.

**Acceptance Criteria:**

**Given** I am browsing marketplace classes
**When** I apply date/time filters
**Then** I can select: Today, Tomorrow, This Week, or a specific date
**And** I can select time of day: Morning (5-12), Afternoon (12-5), Evening (5-10)
**And** results show only classes matching my criteria
**And** I can combine date and time filters

---

### Story 7.5: Filter Classes by Price and Availability

As a **consumer**,
I want to filter classes by price and availability,
So that I can find affordable classes with open spots.

**Acceptance Criteria:**

**Given** I am browsing marketplace classes
**When** I apply price/availability filters
**Then** I can filter by price range: Free, Under R100, R100-200, R200+
**And** I can toggle "Available only" to hide full classes
**And** results update to match selected criteria

---

### Story 7.6: View Gym Profile

As a **consumer**,
I want to view a gym's profile,
So that I can learn about the gym before booking.

**Acceptance Criteria:**

**Given** I tap on a gym name or "View Gym" link
**When** the gym profile loads
**Then** I see: name, description, photos, address, operating hours
**And** I see: amenities (showers, lockers, parking, etc.)
**And** I see: upcoming marketplace classes at this gym
**And** I see: distance from my location

---

### Story 7.7: View Class Details

As a **consumer**,
I want to view full class details,
So that I can decide whether to book.

**Acceptance Criteria:**

**Given** I tap on a class in the browse list
**When** the class detail screen loads
**Then** I see: class name, type, duration, description
**And** I see: gym name, address, distance, map link
**And** I see: date, time, instructor name and bio
**And** I see: spots remaining, price, cancellation policy
**And** I see: "Book" button or "Join Waitlist" if full

---

### Story 7.8: Subscribe to Marketplace Plan

As a **consumer**,
I want to subscribe to a marketplace class package,
So that I can book classes across multiple gyms.

**Acceptance Criteria:**

**Given** I am on the marketplace subscription page
**When** I select a plan (8, 12, or unlimited classes/month)
**Then** I see the plan details and price
**And** I can confirm subscription
**And** a `marketplace_subscriptions` table record is created
**And** `classes_remaining` is set to plan allocation
**And** I receive confirmation email
**And** payment is processed (or flagged for payment integration)

---

### Story 7.9: Book Class with Marketplace Subscription

As a **consumer with marketplace subscription**,
I want to book classes using my subscription credits,
So that I can attend classes at any participating gym.

**Acceptance Criteria:**

**Given** I have an active marketplace subscription with credits remaining
**When** I book a marketplace class
**Then** I select "Use subscription credit" as payment method
**And** `classes_remaining` is decremented
**And** booking is created with `source: marketplace`, `booking_type: subscription`
**And** I receive booking confirmation

---

### Story 7.10: View Marketplace Subscription Status

As a **consumer**,
I want to view my marketplace subscription status,
So that I know how many credits I have left.

**Acceptance Criteria:**

**Given** I have a marketplace subscription
**When** I view my subscription
**Then** I see: plan name, classes remaining, classes total
**And** I see: reset date (when credits renew)
**And** I see: subscription status (active, paused, cancelled)
**And** I see: "Manage Subscription" options

---

### Story 7.11: Manage Marketplace Subscription

As a **consumer**,
I want to manage my marketplace subscription,
So that I can upgrade, pause, or cancel.

**Acceptance Criteria:**

**Given** I have a marketplace subscription
**When** I access subscription management
**Then** I can upgrade to a higher tier (immediate)
**And** I can downgrade (takes effect next billing cycle)
**And** I can pause subscription (credits freeze)
**And** I can cancel (takes effect at end of current period)
**And** changes are confirmed and I receive email notification

---

### Story 7.12: Share Class Details

As a **consumer**,
I want to share class details with friends,
So that we can work out together.

**Acceptance Criteria:**

**Given** I am viewing a class detail screen
**When** I tap "Share"
**Then** I can share via: WhatsApp, SMS, Email, or Copy Link
**And** the shared content includes: class name, gym, date/time, booking link
**And** the link opens the class detail in the app (or web fallback)

---

### Story 7.13: Invite Friends via Referral Link

As a **consumer**,
I want to invite friends to StudioLoop,
So that they can discover the platform.

**Acceptance Criteria:**

**Given** I am in the app
**When** I share my referral link
**Then** the link includes my referral code
**And** friends who sign up via my link are tracked
**And** referral tracking is recorded for future rewards (no rewards in MVP)
**And** I can share via: WhatsApp, SMS, Email, or Copy Link

---

## Epic 8: Payments & Billing

**Goal:** Payments flow seamlessly for memberships, bookings, and marketplace subscriptions.

**FRs covered:** FR57, FR58, FR59, FR60, FR61, FR62
**ARCHs covered:** ARCH-20 through ARCH-23

**Platform Distribution:**
- **Consumer payment flows:** Consumer Web ✅ + Consumer Mobile ✅
- **Gym payment dashboard & reports:** Gym Web ✅ + Gym Mobile ✅

---

### Story 8.1: Payment Interface Abstraction

As a **developer**,
I want an abstracted payment interface,
So that we can swap payment providers without changing business logic.

**Acceptance Criteria:**

**Given** the payment module is implemented
**When** processing any payment
**Then** a `PaymentProvider` interface defines: `initiate()`, `verify()`, `refund()`
**And** `OzowProvider` and `PayFastProvider` implement the interface
**And** provider selection is configurable per environment
**And** a `payments` table stores all payment records
**And** payments record: `amount`, `currency`, `type`, `status`, `provider`, `provider_reference`

---

### Story 8.2: Initiate Payment Flow

As a **consumer**,
I want to initiate payment for memberships or bookings,
So that I can complete my purchase.

**Acceptance Criteria:**

**Given** I am completing a purchase (membership, class, subscription)
**When** I proceed to payment
**Then** a payment record is created with `status: pending`
**And** I am redirected to the payment provider's page/SDK
**And** the payment includes: amount, description, return URLs
**And** timeout handling redirects back with appropriate message

---

### Story 8.3: Payment Webhook Processing

As a **system**,
I want to process payment provider webhooks,
So that payment status is updated reliably.

**Acceptance Criteria:**

**Given** a payment was initiated
**When** the payment provider sends a webhook
**Then** the webhook is validated (signature verification)
**And** payment status is updated: `completed`, `failed`, or `refunded`
**And** associated records are updated (membership activated, booking confirmed)
**And** webhook events are logged for debugging
**And** duplicate webhooks are handled idempotently

---

### Story 8.4: Gym Payment Dashboard

As a **gym owner**,
I want to view all payments received,
So that I can track my revenue.

**Acceptance Criteria:**

**Given** I am on the payments page
**When** I view the payment list
**Then** I see all payments to my gym
**And** I can filter by: date range, type (membership, class), status
**And** each payment shows: member name, amount, type, status, date
**And** I can tap to see payment details
**And** summary shows: total received, pending, failed

---

### Story 8.5: Failed Payment Detection

As a **system**,
I want to detect and flag failed payments,
So that gyms can follow up with members.

**Acceptance Criteria:**

**Given** a recurring payment fails (membership renewal)
**When** the failure is detected
**Then** payment status → `failed`
**And** the failure appears on gym owner dashboard action items
**And** member is notified (email + push)
**And** membership status is updated (grace period or suspended based on config)
**And** `failed_at` and `failure_reason` are recorded

---

### Story 8.6: Automatic Payment Retry

As a **system**,
I want to automatically retry failed payments,
So that recoverable failures are resolved without manual intervention.

**Acceptance Criteria:**

**Given** a payment failed
**When** retry is triggered
**Then** retry attempts are made at configured intervals (e.g., day 1, 3, 7)
**And** `retry_count` is incremented
**And** if successful: status → `completed`, member notified
**And** if max retries exceeded: status → `failed_permanent`, gym notified
**And** retry logic is implemented as a background worker

---

### Story 8.7: Marketplace Payout Reports

As a **gym owner**,
I want to view marketplace booking revenue,
So that I can track earnings from marketplace.

**Acceptance Criteria:**

**Given** my gym has marketplace bookings
**When** I view payout reports
**Then** I see: total marketplace bookings, gross revenue, platform fee, net payout
**And** I can filter by date range
**And** I see breakdown by class
**And** payout schedule is displayed (e.g., weekly settlement)
**And** platform commission is calculated and shown

---

### Story 8.8: Consumer Payment History

As a **consumer**,
I want to view my payment history,
So that I can track my spending.

**Acceptance Criteria:**

**Given** I am on my payment history screen
**When** I view payments
**Then** I see all my payments across gyms and marketplace
**And** each shows: description, amount, date, status
**And** I can filter by: date range, type (membership, class, subscription)
**And** I can tap to see payment details including receipt

---

### Story 8.9: Payment Receipt Generation

As a **consumer**,
I want to receive payment receipts,
So that I have records for my purchases.

**Acceptance Criteria:**

**Given** a payment is completed
**When** receipt is requested
**Then** a receipt is generated with: date, amount, description, payment method, reference
**And** receipt is emailed to consumer
**And** receipt can be viewed/downloaded from payment history
**And** receipts include VAT information where applicable

---

## Epic 9: Notifications & Communication

**Goal:** Users receive timely, configurable notifications via push, email, and WhatsApp.

**FRs covered:** FR63, FR64, FR65, FR66, FR67, FR68, FR69

**Platform Distribution:**
- **Push notifications:** Consumer Mobile ✅ + Gym Mobile ✅
- **In-app notification center:** All platforms ✅
- **Gym messaging:** Gym Web ✅ + Gym Mobile ✅
- **Consumer preferences:** Consumer Web ✅ + Consumer Mobile ✅

---

### Story 9.1: Notification Infrastructure Setup

As a **developer**,
I want notification infrastructure configured,
So that we can send push, email, and WhatsApp messages.

**Acceptance Criteria:**

**Given** the notification module is implemented
**When** sending notifications
**Then** email sending is configured (transactional email provider)
**And** push notifications are configured (FCM for Android, APNs for iOS)
**And** WhatsApp Business API is configured (or stubbed for MVP)
**And** a `notifications` table logs all sent notifications
**And** notification templates are stored and reusable
**And** background workers handle async delivery

---

### Story 9.2: Booking Confirmation Notifications

As a **consumer**,
I want to receive booking confirmations,
So that I know my booking was successful.

**Acceptance Criteria:**

**Given** I successfully book a class
**When** the booking is confirmed
**Then** I receive a push notification immediately
**And** I receive a confirmation email
**And** the notification includes: class name, gym, date, time, instructor
**And** email includes "Add to Calendar" link

---

### Story 9.3: Class Reminder Notifications

As a **consumer**,
I want to receive reminders before my class,
So that I don't forget to attend.

**Acceptance Criteria:**

**Given** I have an upcoming class booking
**When** reminder time approaches (configurable: 2h, 24h before)
**Then** I receive a push notification
**And** reminder includes: class name, gym, time, location
**And** reminder time is based on my preferences
**And** reminders are sent via background scheduler

---

### Story 9.4: Waitlist Notifications

As a **consumer**,
I want to be notified when a waitlist spot opens,
So that I can quickly claim my spot.

**Acceptance Criteria:**

**Given** I am on a class waitlist
**When** a spot becomes available and is offered to me
**Then** I receive a push notification immediately
**And** I receive an email
**And** notification includes: class details, time to respond, action buttons
**And** notification links directly to accept/decline screen

---

### Story 9.5: Payment Reminder Notifications

As a **consumer**,
I want to receive payment reminders,
So that I know when payments are due.

**Acceptance Criteria:**

**Given** I have a membership with upcoming renewal
**When** payment is due in 3 days
**Then** I receive a push notification
**And** I receive an email
**And** notification includes: amount, due date, membership name
**And** notification links to payment/update payment method screen

---

### Story 9.6: Payment Failure Notifications

As a **consumer**,
I want to be notified if a payment fails,
So that I can fix the issue.

**Acceptance Criteria:**

**Given** a payment fails
**When** failure is detected
**Then** I receive a push notification immediately
**And** I receive an email
**And** notification includes: what failed, suggested action, link to update payment
**And** gym is also notified (see Epic 8)

---

### Story 9.7: Gym-to-Member Messaging

As a **gym owner/manager**,
I want to send messages to my members,
So that I can communicate announcements and updates.

**Acceptance Criteria:**

**Given** I am on the messaging page
**When** I compose a message
**Then** I can select recipients: all members, specific plan, individual members
**And** I can choose channels: in-app notification, email
**And** I can schedule for later or send immediately
**And** message is delivered to selected channels
**And** delivery status is tracked

---

### Story 9.8: WhatsApp Critical Notifications

As a **system**,
I want to send critical notifications via WhatsApp,
So that urgent messages reach members on their preferred channel.

**Acceptance Criteria:**

**Given** a critical event occurs (class cancelled, emergency closure)
**When** notification is triggered
**Then** WhatsApp message is sent to affected members
**And** message is delivered via WhatsApp Business API
**And** fallback to email if WhatsApp delivery fails
**And** WhatsApp is only used for critical/emergency notifications

---

### Story 9.9: Consumer Notification Preferences

As a **consumer**,
I want to configure my notification preferences,
So that I receive notifications how I want them.

**Acceptance Criteria:**

**Given** I am on notification settings
**When** I configure preferences
**Then** I can enable/disable by channel: push, email, WhatsApp
**And** I can enable/disable by type: bookings, reminders, waitlist, payments, gym messages
**And** I can set reminder timing (2h, 24h, both)
**And** preferences are saved and respected for all notifications
**And** critical notifications (payment failures) cannot be fully disabled

---

### Story 9.10: In-App Notification Center

As a **consumer**,
I want to see my notifications in the app,
So that I can review past notifications.

**Acceptance Criteria:**

**Given** I have received notifications
**When** I open the notification center
**Then** I see a list of all my notifications
**And** unread notifications are highlighted
**And** I can tap to view details or take action
**And** I can mark as read
**And** old notifications are retained for 30 days

---

## Epic 10: Reporting & Analytics

**Goal:** Gym owners have full visibility into business health and can identify at-risk members.

**FRs covered:** FR70, FR71, FR72, FR73, FR74, FR75, FR76

**Platforms:** Gym Web ✅ + Gym Mobile ✅ (full reports available on both platforms)

---

### Story 10.1: Revenue Reports

As a **gym owner**,
I want to view revenue reports,
So that I can track my gym's financial performance.

**Acceptance Criteria:**

**Given** I am on the reports page
**When** I view revenue reports
**Then** I see total revenue for selected period
**And** I see breakdown by source: memberships, classes, marketplace
**And** I can select period: daily, weekly, monthly, custom date range
**And** I see comparison to previous period (growth/decline %)
**And** data is presented in charts and tables
**And** I can export to CSV

---

### Story 10.2: Attendance Reports

As a **gym owner**,
I want to view attendance reports,
So that I can understand member activity.

**Acceptance Criteria:**

**Given** I am on the reports page
**When** I view attendance reports
**Then** I see total check-ins for selected period
**And** I see check-ins by day of week and time of day (heatmap)
**And** I see peak hours analysis
**And** I see average daily/weekly attendance
**And** I can filter by membership tier
**And** data helps me understand gym utilization

---

### Story 10.3: Membership Health Reports

As a **gym owner**,
I want to view membership health reports,
So that I can monitor churn and retention.

**Acceptance Criteria:**

**Given** I am on the reports page
**When** I view membership health
**Then** I see: total active members, new this period, cancelled this period
**And** I see churn rate (% cancelled / total)
**And** I see retention rate
**And** I see breakdown by membership tier
**And** I see members expiring soon
**And** trends are shown over time

---

### Story 10.4: Class Performance Reports

As a **gym owner**,
I want to view class performance reports,
So that I can optimize my class schedule.

**Acceptance Criteria:**

**Given** I am on the reports page
**When** I view class performance
**Then** I see fill rate per class type (% booked / capacity)
**And** I see attendance rate (% checked in / booked)
**And** I see no-show rate
**And** I see most popular classes (by bookings)
**And** I see underperforming classes (low fill rate)
**And** I can filter by instructor, class type, time period

---

### Story 10.5: Staff Performance Reports

As a **gym owner**,
I want to view staff performance reports,
So that I can manage my team effectively.

**Acceptance Criteria:**

**Given** I am on the reports page
**When** I view staff performance
**Then** I see classes taught per instructor
**And** I see average fill rate per instructor
**And** I see total hours worked per staff member
**And** I see instructor earnings (if pay rate configured)
**And** I can filter by staff member, role, time period

---

### Story 10.6: Consumer Class History

As a **consumer**,
I want to view my class history,
So that I can track my fitness journey.

**Acceptance Criteria:**

**Given** I am on my profile/history page
**When** I view class history
**Then** I see a list of all classes I've attended
**And** each shows: class name, gym, date, instructor
**And** I can filter by: gym, class type, date range
**And** I see total classes attended this month/year
**And** I can rebook a past class directly from history

---

### Story 10.7: Consumer Statistics Dashboard

As a **consumer**,
I want to see my fitness statistics,
So that I can stay motivated.

**Acceptance Criteria:**

**Given** I am on my stats page
**When** I view my statistics
**Then** I see: total classes attended (all time, this month)
**And** I see: favorite class type (most attended)
**And** I see: most visited gym
**And** I see: current streak (consecutive weeks with classes)
**And** I see: classes per week average
**And** stats encourage continued engagement

---

### Story 10.8: At-Risk Member Detection

As a **system**,
I want to identify at-risk members,
So that gyms can proactively engage them.

**Acceptance Criteria:**

**Given** member activity data exists
**When** at-risk detection runs
**Then** members with declining attendance are flagged
**And** at-risk criteria: no check-in in X days, attendance dropped by Y%
**And** at-risk members appear on gym owner dashboard
**And** gym can view at-risk member list with last activity date
**And** detection runs as a scheduled background job

---

### Story 10.9: Gym Owner Dashboard

As a **gym owner**,
I want an action-focused dashboard,
So that I can see what needs attention immediately.

**Acceptance Criteria:**

**Given** I log into the gym management app
**When** I view the dashboard
**Then** I see action items at the top: failed payments, at-risk members, low-fill classes, expiring memberships
**And** I see today's summary: revenue, check-ins, bookings
**And** I see quick metrics: active members, classes today, fill rate
**And** I can tap action items to take action
**And** dashboard refreshes in real-time

---

## Epic 11: Platform Administration & Real-time

**Goal:** Platform team can manage gyms, resolve issues, and provide real-time updates.

**FRs covered:** FR77, FR78, FR79, FR80, FR81, FR82, FR83, FR84

**Platform Distribution:**
- **Admin functions (Stories 11.1-11.6):** Admin Web (internal tool)
- **Real-time updates (Stories 11.7-11.10):** All consumer and gym platforms

---

### Story 11.1: Gym Application Review

As a **platform admin**,
I want to review and approve new gym applications,
So that only legitimate gyms join the platform.

**Acceptance Criteria:**

**Given** a new gym registers
**When** their application is submitted
**Then** the gym status is set to `pending_approval`
**And** application appears in admin review queue
**And** admin can view: gym details, owner info, documents
**And** admin can approve (status → `active`) or reject with reason
**And** gym owner is notified of decision

---

### Story 11.2: Platform Gym Management

As a **platform admin**,
I want to view and manage all gyms,
So that I can oversee the platform.

**Acceptance Criteria:**

**Given** I am on the admin gym management page
**When** I view gyms
**Then** I see all gyms with: name, status, member count, join date
**And** I can search by name or location
**And** I can filter by: status, tier, marketplace enabled
**And** I can suspend or reactivate gyms
**And** I can view detailed gym information

---

### Story 11.3: Consumer Complaint Handling

As a **platform admin**,
I want to view and manage consumer complaints,
So that I can resolve issues.

**Acceptance Criteria:**

**Given** consumers can submit complaints (via support)
**When** I view complaints
**Then** I see all open complaints with: consumer, gym, description, date
**And** I can view complaint details and history
**And** I can assign complaints to myself
**And** I can add notes and update status
**And** I can contact consumer or gym
**And** I can resolve and close complaints

---

### Story 11.4: Account Credit Issuance

As a **platform admin**,
I want to issue credits to consumer accounts,
So that I can compensate for issues or run promotions.

**Acceptance Criteria:**

**Given** I am viewing a consumer's account
**When** I issue credits
**Then** I can add marketplace class credits to their account
**And** I enter amount and reason
**And** credit is added to their `marketplace_subscriptions.classes_remaining`
**And** action is logged with admin ID and reason
**And** consumer is notified of credit

---

### Story 11.5: Platform Health Monitoring

As a **platform admin**,
I want to monitor platform health,
So that I can ensure the system is running smoothly.

**Acceptance Criteria:**

**Given** I am on the admin dashboard
**When** I view platform health
**Then** I see: total gyms, total consumers, total bookings today
**And** I see: system status (API, database, services)
**And** I see: error rates and latency metrics (from Sentry/Fly)
**And** I see: recent incidents or alerts
**And** I can drill down into specific metrics

---

### Story 11.6: Gym-Level Data Access for Support

As a **platform admin**,
I want to access gym-level data,
So that I can provide support to gyms.

**Acceptance Criteria:**

**Given** I am supporting a gym
**When** I access their data
**Then** I can view their members, bookings, payments
**And** I can view their settings and configuration
**And** I can impersonate gym owner view (read-only)
**And** all access is logged for audit (NFR14)
**And** I cannot modify data without explicit action

---

### Story 11.7: Real-Time Class Availability

As a **system**,
I want to provide real-time class availability updates,
So that consumers see accurate spot counts.

**Acceptance Criteria:**

**Given** a consumer is viewing a class or class list
**When** spots change (booking, cancellation)
**Then** availability updates in real-time via WebSocket
**And** consumer sees updated spots without refreshing
**And** WebSocket connection is established on class views
**And** events follow format: `{ "event": "session.spots_updated", "session_id": "uuid", "spots_available": N }`
**And** connection handles reconnection gracefully

---

### Story 11.8: Real-Time Waitlist Updates

As a **consumer**,
I want to see my waitlist position update in real-time,
So that I know when I'm getting closer.

**Acceptance Criteria:**

**Given** I am on the waitlist for a class
**When** my position changes
**Then** I see the update in real-time via WebSocket
**And** events follow format: `{ "event": "waitlist.position_updated", "session_id": "uuid", "position": N }`
**And** I receive immediate notification when a spot is offered

---

### Story 11.9: Webhook Event System

As a **gym integrator**,
I want to receive webhook events,
So that I can integrate StudioLoop with other systems.

**Acceptance Criteria:**

**Given** a gym has registered webhook endpoints
**When** relevant events occur
**Then** webhooks are sent to registered endpoints
**And** events include: `booking.created`, `booking.cancelled`, `membership.created`, `payment.completed`, etc.
**And** webhooks are signed for verification
**And** failed deliveries are retried (3 attempts)
**And** delivery logs are available to gym

---

### Story 11.10: Webhook Management

As a **gym owner**,
I want to manage webhook endpoints,
So that I can integrate with my other systems.

**Acceptance Criteria:**

**Given** I am on the integrations settings page
**When** I manage webhooks
**Then** I can add webhook endpoints with URL and events to subscribe
**And** I can view registered webhooks
**And** I can test webhooks (send test event)
**And** I can view delivery logs and failures
**And** I can delete webhooks
**And** endpoint URLs are validated

---

## Epic 12: Gym Web Application (Priority 1)

**Goal:** Build and deploy the Gym Management Web application at `manage.studioloop.co.za`, validating all gym-side features before mobile development.

**Development Priority:** 1st (Web-First Validation Strategy)

**URL:** `manage.studioloop.co.za`

**Implements Features From:**
- Epic 1: Staff/Owner Authentication
- Epic 2: Gym Onboarding & Configuration
- Epic 3: Staff Management & Permissions
- Epic 4: Membership Plans (Gym-side)
- Epic 5: Class Scheduling System
- Epic 6: Manual Check-in (primary method for web)
- Epic 8: Gym Payment Dashboard
- Epic 9: Gym Messaging & Notifications
- Epic 10: Reporting & Analytics (full suite)
- Epic 11: Webhook Management

---

### Story 12.1: Gym Web App Shell & Routing

As a **developer**,
I want to scaffold the Gym Web application with routing and layout,
So that we have a foundation for feature implementation.

**Acceptance Criteria:**

**Given** the `apps/gym-web/` directory in the monorepo
**When** I scaffold the application
**Then** Vite + React is configured with TypeScript strict mode
**And** React Router is configured with protected routes
**And** Layout includes: Header, Sidebar navigation, Main content area
**And** Sidebar has navigation for: Dashboard, Members, Schedule, Check-in, Reports, Settings
**And** Authentication guard redirects unauthenticated users to login
**And** Tailwind CSS is configured using shared `packages/ui` tokens
**And** `@sl/api-client` package is imported and configured
**And** running `pnpm dev --filter gym-web` starts the dev server

---

### Story 12.2: Gym Web Authentication

As a **gym staff member**,
I want to log in to the Gym Web application,
So that I can access gym management features.

**Acceptance Criteria:**

**Given** the Gym Web login page
**When** I enter valid staff credentials
**Then** JWT tokens are stored securely (httpOnly cookies preferred, or secure localStorage)
**And** I am redirected to the Dashboard
**And** my role (Owner/Manager/Front Desk/Instructor) determines visible features
**And** token refresh happens automatically before expiry
**And** invalid credentials show appropriate error messages

**Implements:** Epic 1 (Stories 1.3, 1.4, 1.5, 1.8)

---

### Story 12.3: Gym Web Dashboard

As a **gym owner/manager**,
I want an action-first dashboard,
So that I see what needs my attention immediately.

**Acceptance Criteria:**

**Given** I am logged in to Gym Web
**When** I view the Dashboard
**Then** I see action items at top: failed payments, at-risk members, low-fill classes
**And** I see today's summary: revenue, check-ins, bookings
**And** I see quick metrics: active members, classes today, fill rate
**And** action items are clickable and navigate to relevant sections
**And** data refreshes via polling or WebSocket

**Implements:** Epic 10 (Story 10.9)

---

### Story 12.4: Gym Web Member Management

As a **gym staff member**,
I want to view and manage members,
So that I can handle member operations.

**Acceptance Criteria:**

**Given** I am on the Members section
**When** I view the member list
**Then** I see all gym members with: name, membership status, last visit, payment status
**And** I can search by name, email, or phone
**And** I can filter by: membership tier, status (active/expired/at-risk)
**And** I can click a member to view full details
**And** member detail shows: profile, membership history, booking history, payment history
**And** I can edit member details (if permitted by role)

**Implements:** Epic 4 (Stories 4.10, 4.11)

---

### Story 12.5: Gym Web Class Scheduling

As a **gym manager**,
I want to create and manage class schedules,
So that members can book classes.

**Acceptance Criteria:**

**Given** I am on the Schedule section
**When** I manage classes
**Then** I see a calendar view of all scheduled classes
**And** I can create class templates with recurring schedules
**And** I can schedule individual sessions
**And** I can assign instructors and spaces to classes
**And** I can set capacity and waitlist limits
**And** I can cancel classes (with notification to booked members)
**And** I can set marketplace pricing for classes
**And** approval workflow is respected based on gym settings

**Implements:** Epic 5 (Stories 5.1-5.11)

---

### Story 12.6: Gym Web Manual Check-in

As a **front desk staff member**,
I want to check in members by searching their name or phone,
So that I can record their gym entry.

**Acceptance Criteria:**

**Given** I am on the Check-in section
**When** I search for a member
**Then** I can search by phone number or name
**And** matching members appear with their photo, name, and membership status
**And** I can select a member and check them in
**And** membership status is validated (active, not expired, payment OK)
**And** if member has a class booking today, it's shown and can be marked as checked-in
**And** check-in record is created with timestamp
**And** clear error messages for invalid memberships

**Implements:** Epic 6 (Story 6.10 - PRIMARY method for Gym Web)

---

### Story 12.7: Gym Web Reports

As a **gym owner**,
I want to view comprehensive reports,
So that I understand my business performance.

**Acceptance Criteria:**

**Given** I am on the Reports section
**When** I view reports
**Then** I can access: Revenue, Attendance, Membership Health, Class Performance, Staff Performance
**And** each report supports date range selection
**And** data is presented in charts and tables
**And** I can export reports to CSV
**And** I can see comparison to previous periods
**And** at-risk members are flagged with recommended actions

**Implements:** Epic 10 (Stories 10.1-10.5, 10.8)

---

### Story 12.8: Gym Web Staff Management

As a **gym owner**,
I want to manage my staff members,
So that they have appropriate access to the system.

**Acceptance Criteria:**

**Given** I am on the Settings > Staff section
**When** I manage staff
**Then** I can add new staff members with role assignment
**And** I can configure permissions per role
**And** I can set working hours and shifts
**And** I can set instructor pay rates
**And** I can deactivate staff members
**And** staff can view their own schedule and earnings

**Implements:** Epic 3 (Stories 3.1-3.8)

---

### Story 12.9: Gym Web Settings & Configuration

As a **gym owner**,
I want to configure my gym settings,
So that the platform matches my business operations.

**Acceptance Criteria:**

**Given** I am on the Settings section
**When** I configure my gym
**Then** I can edit gym profile (name, logo, description, photos, location)
**And** I can set operating hours and holiday closures
**And** I can configure cancellation policies
**And** I can manage membership plans (create, edit, archive)
**And** I can manage spaces (rooms, studios, capacity, amenities)
**And** I can toggle marketplace participation
**And** I can view my SaaS subscription tier
**And** I can manage webhook integrations

**Implements:** Epic 2 (Stories 2.1-2.11), Epic 11 (Stories 11.9, 11.10)

---

### Story 12.10: Gym Web Messaging

As a **gym staff member**,
I want to send messages to members,
So that I can communicate important information.

**Acceptance Criteria:**

**Given** I am in the messaging section (or member detail)
**When** I send a message
**Then** I can message individual members or groups
**And** messages can be sent via in-app notification, email, or WhatsApp
**And** I can use templates for common messages
**And** message history is visible

**Implements:** Epic 9 (Story 9.7)

---

### Story 12.11: Gym Web Payment Dashboard

As a **gym owner**,
I want to view payment status and reports,
So that I can track my revenue.

**Acceptance Criteria:**

**Given** I am on the Payments section
**When** I view payment data
**Then** I see pending and completed payments
**And** I see failed payments with retry status
**And** I see marketplace booking revenue and payout reports
**And** I can view payment details for any transaction

**Implements:** Epic 8 (Stories 8.4, 8.5, 8.7)

---

## Epic 13: Consumer Web Application (Priority 2)

**Goal:** Build and deploy the Consumer Web application at `app.studioloop.co.za`, validating all consumer-side features before mobile development.

**Development Priority:** 2nd (Web-First Validation Strategy)

**URL:** `app.studioloop.co.za`

**Implements Features From:**
- Epic 1: Consumer Authentication
- Epic 4: Consumer Membership Enrollment
- Epic 6: Class Booking, QR Code Display
- Epic 7: Marketplace Discovery & Subscriptions
- Epic 8: Consumer Payment Flows
- Epic 9: Consumer Notification Preferences

---

### Story 13.1: Consumer Web App Shell & Routing

As a **developer**,
I want to scaffold the Consumer Web application with routing and layout,
So that we have a foundation for feature implementation.

**Acceptance Criteria:**

**Given** the `apps/consumer-web/` directory in the monorepo
**When** I scaffold the application
**Then** Vite + React is configured with TypeScript strict mode
**And** React Router is configured with protected and public routes
**And** Layout includes: Header with navigation, Main content area, Footer
**And** Navigation has: Home (Bookings), Discover, Memberships, Profile
**And** Authentication guard redirects unauthenticated users to login
**And** Tailwind CSS is configured using shared `packages/ui` tokens
**And** `@sl/api-client` package is imported and configured
**And** running `pnpm dev --filter consumer-web` starts the dev server

---

### Story 13.2: Consumer Web Authentication

As a **consumer**,
I want to register and log in to the Consumer Web application,
So that I can access my gym memberships and book classes.

**Acceptance Criteria:**

**Given** the Consumer Web login/register page
**When** I register with email/password or social login
**Then** my account is created and I'm logged in
**And** JWT tokens are stored securely
**And** I can reset my password via email
**And** I can manage my profile information
**And** I can delete my account (POPIA compliance)

**Implements:** Epic 1 (Stories 1.1, 1.2, 1.5, 1.6, 1.7, 1.9, 1.10)

---

### Story 13.3: Consumer Web Home (My Bookings)

As a **consumer**,
I want to see my upcoming bookings,
So that I know my schedule.

**Acceptance Criteria:**

**Given** I am logged in to Consumer Web
**When** I view the Home page
**Then** I see my upcoming bookings with: class name, gym, date/time, instructor
**And** I see any overdue payments banner if applicable
**And** I can click a booking to view details
**And** I can cancel bookings (subject to cancellation policy)
**And** I can access my QR code for check-in

**Implements:** Epic 6 (Stories 6.1-6.3)

---

### Story 13.4: Consumer Web QR Code Display

As a **consumer**,
I want to display my QR code on the web,
So that I can check in at the gym using any device.

**Acceptance Criteria:**

**Given** I am logged in to Consumer Web
**When** I click the QR code button
**Then** a full-screen QR code is displayed
**And** the QR encodes my consumer ID (signed/encrypted)
**And** my name is displayed below the QR
**And** if I have a booking today, it's shown on the QR screen
**And** QR regenerates periodically for security

**Implements:** Epic 6 (Story 6.8 - Consumer Web)

---

### Story 13.5: Consumer Web Discover Classes

As a **consumer**,
I want to browse and filter classes from marketplace gyms,
So that I can find fitness activities.

**Acceptance Criteria:**

**Given** I am on the Discover page
**When** I browse classes
**Then** I see marketplace-enabled classes from all gyms
**And** I can filter by: class type, date/time, location, price, availability
**And** I can view gym profiles
**And** I can view class details (description, instructor, reviews placeholder)
**And** classes show: name, gym, time, price, spots available

**Implements:** Epic 7 (Stories 7.1-7.7)

---

### Story 13.6: Consumer Web Class Booking

As a **consumer**,
I want to book classes,
So that I can attend fitness activities.

**Acceptance Criteria:**

**Given** I am viewing a class
**When** I book the class
**Then** I can book using my gym membership (if member)
**Or** I can book using marketplace subscription credits
**Or** I can pay per class
**And** if class is full, I can join the waitlist
**And** I receive booking confirmation
**And** booking appears on my Home page

**Implements:** Epic 6 (Stories 6.1, 6.2, 6.4), Epic 7 (Story 7.9)

---

### Story 13.7: Consumer Web Memberships

As a **consumer**,
I want to view and manage my memberships,
So that I can control my gym access.

**Acceptance Criteria:**

**Given** I am on the Memberships page
**When** I view my memberships
**Then** I see all my gym memberships with status and benefits
**And** I see my marketplace subscription (if any) with credits remaining
**And** I can view membership details and usage
**And** I can upgrade/downgrade memberships
**And** I can manage payment methods
**And** I can subscribe to marketplace plans

**Implements:** Epic 4 (Stories 4.4-4.9), Epic 7 (Stories 7.8, 7.10, 7.11)

---

### Story 13.8: Consumer Web Profile & Settings

As a **consumer**,
I want to manage my profile and settings,
So that my account reflects my preferences.

**Acceptance Criteria:**

**Given** I am on the Profile page
**When** I manage my profile
**Then** I can edit personal details (name, photo, contact)
**And** I can manage notification preferences
**And** I can view my class history and statistics
**And** I can view my payment history
**And** I can manage saved payment methods
**And** I can delete my account

**Implements:** Epic 1 (Stories 1.6, 1.7), Epic 9 (Story 9.9), Epic 10 (Stories 10.6, 10.7), Epic 8 (Story 8.8)

---

### Story 13.9: Consumer Web Share & Invite

As a **consumer**,
I want to share classes and invite friends,
So that I can work out with others.

**Acceptance Criteria:**

**Given** I am viewing a class
**When** I share it
**Then** I can share class details via link
**And** I can invite friends via referral link
**And** referral tracking is recorded

**Implements:** Epic 7 (Stories 7.12, 7.13)

---

## Epic 14: Consumer Mobile Application (Priority 3)

**Goal:** Build and deploy the Consumer Mobile application for iOS and Android, porting validated features from Consumer Web with mobile-native enhancements.

**Development Priority:** 3rd (Port validated features from web)

**Distribution:** iOS App Store + Google Play Store

**Implements Features From:**
- All Consumer Web features (Epic 13)
- Mobile-specific: Push notifications, Offline QR display

---

### Story 14.1: Consumer Mobile App Setup

As a **developer**,
I want to scaffold the Consumer Mobile application with Expo,
So that we have a foundation for feature implementation.

**Acceptance Criteria:**

**Given** the `apps/consumer-mobile/` directory in the monorepo
**When** I scaffold the application
**Then** Expo React Native is configured with TypeScript
**And** Expo Router is configured for file-based navigation
**And** Tab navigation has: Home, Discover, Memberships, Profile
**And** NativeWind is configured using shared `packages/ui` tokens
**And** `@sl/api-client` package is imported and configured
**And** MMKV is configured for secure token storage
**And** Expo SQLite is configured for offline data
**And** running `pnpm dev --filter consumer-mobile` starts Expo

---

### Story 14.2: Consumer Mobile Authentication

As a **consumer**,
I want to register and log in on my mobile device,
So that I can access the app.

**Acceptance Criteria:**

**Given** the Consumer Mobile app
**When** I register or log in
**Then** all Consumer Web auth features work (port from Story 13.2)
**And** tokens are stored securely in MMKV
**And** biometric authentication is available (optional enhancement)

**Implements:** Port of Epic 13 (Story 13.2) + mobile enhancements

---

### Story 14.3: Consumer Mobile Home & Bookings

As a **consumer**,
I want to view my bookings on mobile,
So that I can check my schedule on the go.

**Acceptance Criteria:**

**Given** I am logged in to Consumer Mobile
**When** I view the Home tab
**Then** all Consumer Web home features work (port from Story 13.3)
**And** I can pull-to-refresh
**And** bookings are cached for offline viewing

**Implements:** Port of Epic 13 (Story 13.3) + mobile enhancements

---

### Story 14.4: Consumer Mobile QR Code Display (Offline)

As a **consumer**,
I want to display my QR code on mobile,
So that I can check in even without internet.

**Acceptance Criteria:**

**Given** I am in the Consumer Mobile app
**When** I access my QR code
**Then** all Consumer Web QR features work (port from Story 13.4)
**And** QR code is cached locally and works offline
**And** QR is accessible from home screen and booking cards

**Implements:** Port of Epic 13 (Story 13.4) + Epic 6 (Story 6.8 offline requirement)

---

### Story 14.5: Consumer Mobile Discover & Booking

As a **consumer**,
I want to browse and book classes on mobile,
So that I can find activities on the go.

**Acceptance Criteria:**

**Given** I am in the Consumer Mobile app
**When** I use Discover
**Then** all Consumer Web discover/booking features work (port from Stories 13.5, 13.6)
**And** location-based "near me" filter uses device GPS
**And** class list supports infinite scroll

**Implements:** Port of Epic 13 (Stories 13.5, 13.6) + location enhancement

---

### Story 14.6: Consumer Mobile Memberships

As a **consumer**,
I want to manage memberships on mobile,
So that I can control my access on the go.

**Acceptance Criteria:**

**Given** I am in the Consumer Mobile app
**When** I view Memberships
**Then** all Consumer Web membership features work (port from Story 13.7)

**Implements:** Port of Epic 13 (Story 13.7)

---

### Story 14.7: Consumer Mobile Profile & Settings

As a **consumer**,
I want to manage my profile on mobile,
So that I can update preferences on the go.

**Acceptance Criteria:**

**Given** I am in the Consumer Mobile app
**When** I view Profile
**Then** all Consumer Web profile features work (port from Story 13.8)
**And** notification preferences include push notification controls

**Implements:** Port of Epic 13 (Story 13.8)

---

### Story 14.8: Consumer Mobile Push Notifications

As a **consumer**,
I want to receive push notifications,
So that I'm alerted to important events.

**Acceptance Criteria:**

**Given** I have the Consumer Mobile app installed
**When** relevant events occur
**Then** I receive push notifications for: booking confirmations, class reminders, waitlist offers, payment alerts
**And** tapping a notification opens the relevant screen
**And** notification permissions are requested appropriately

**Implements:** Epic 9 (Stories 9.2-9.6) - mobile push

---

### Story 14.9: Consumer Mobile App Store Submission

As a **developer**,
I want to submit the Consumer Mobile app to app stores,
So that consumers can download it.

**Acceptance Criteria:**

**Given** the Consumer Mobile app is complete
**When** I submit to app stores
**Then** EAS Build creates production builds for iOS and Android
**And** App Store assets (screenshots, descriptions) are prepared
**And** Privacy policy and data handling are documented
**And** In-app purchase compliance is handled (if applicable)
**And** App is submitted and approved

---

## Epic 15: Gym Mobile Application (Priority 4)

**Goal:** Build and deploy the Gym Mobile application for iOS and Android, enabling on-floor operations with QR scanning.

**Development Priority:** 4th (Mobile-specific tools after web validation)

**Distribution:** iOS App Store + Google Play Store

**Implements Features From:**
- Core Gym Web features (portable subset)
- Mobile-specific: QR Scanner, Offline Check-in

---

### Story 15.1: Gym Mobile App Setup

As a **developer**,
I want to scaffold the Gym Mobile application with Expo,
So that we have a foundation for feature implementation.

**Acceptance Criteria:**

**Given** the `apps/gym-mobile/` directory in the monorepo
**When** I scaffold the application
**Then** Expo React Native is configured with TypeScript
**And** Expo Router is configured for file-based navigation
**And** Tab navigation has: Dashboard, Check-in, Schedule, Members
**And** NativeWind is configured using shared `packages/ui` tokens
**And** `@sl/api-client` package is imported and configured
**And** MMKV is configured for secure token storage
**And** Expo SQLite is configured for offline check-in queue
**And** Expo Camera is configured for QR scanning
**And** running `pnpm dev --filter gym-mobile` starts Expo

---

### Story 15.2: Gym Mobile Authentication

As a **gym staff member**,
I want to log in on my mobile device,
So that I can access gym tools on the floor.

**Acceptance Criteria:**

**Given** the Gym Mobile app
**When** I log in with staff credentials
**Then** authentication works (port from Gym Web)
**And** tokens are stored securely in MMKV
**And** my role determines visible features

**Implements:** Port of Epic 12 (Story 12.2)

---

### Story 15.3: Gym Mobile Dashboard

As a **gym staff member**,
I want a quick dashboard on mobile,
So that I see today's key information.

**Acceptance Criteria:**

**Given** I am logged in to Gym Mobile
**When** I view the Dashboard
**Then** I see today's metrics: check-ins, bookings, classes
**And** I see urgent action items
**And** I can tap to navigate to relevant sections

**Implements:** Simplified port of Epic 12 (Story 12.3)

---

### Story 15.4: Gym Mobile QR Scanner Check-in

As a **front desk staff member**,
I want to scan member QR codes,
So that I can check them in quickly.

**Acceptance Criteria:**

**Given** I am on the Check-in tab
**When** I scan a member's QR code
**Then** the camera opens with QR scanner overlay
**And** scanning is fast and responsive
**And** member is identified and validated
**And** success/error feedback is clear (haptic + visual)
**And** check-in is recorded
**And** if they have a booking, it's marked as checked-in

**Implements:** Epic 6 (Story 6.9) - THIS IS THE PRIMARY QR SCANNER

---

### Story 15.5: Gym Mobile Manual Check-in Fallback

As a **front desk staff member**,
I want to search for members manually,
So that I can check them in if QR fails.

**Acceptance Criteria:**

**Given** QR scanning isn't working
**When** I search by phone or name
**Then** manual check-in works (port from Gym Web)

**Implements:** Port of Epic 12 (Story 12.6) - fallback

---

### Story 15.6: Gym Mobile Offline Check-in

As a **front desk staff member**,
I want check-in to work offline,
So that connectivity issues don't block members.

**Acceptance Criteria:**

**Given** the Gym Mobile app loses connectivity
**When** I scan a QR code
**Then** check-in is recorded locally in Expo SQLite
**And** offline mode indicator is visible
**And** cached member data allows validation
**And** when online, queued check-ins sync to server
**And** conflicts are resolved (server wins)

**Implements:** Epic 6 (Story 6.13)

---

### Story 15.7: Gym Mobile Schedule View

As a **gym staff member**,
I want to view today's class schedule,
So that I know what's happening.

**Acceptance Criteria:**

**Given** I am on the Schedule tab
**When** I view the schedule
**Then** I see today's classes with times, instructors, and booking counts
**And** I can see upcoming days
**And** I can tap a class to view attendees

**Implements:** Simplified port of Epic 12 (Story 12.5)

---

### Story 15.8: Gym Mobile Member Lookup

As a **gym staff member**,
I want to look up members quickly,
So that I can help with inquiries.

**Acceptance Criteria:**

**Given** I am on the Members tab
**When** I search for a member
**Then** I can find members by name, phone, or email
**And** I can view their membership status and recent visits
**And** I can view their booking history

**Implements:** Simplified port of Epic 12 (Story 12.4)

---

### Story 15.9: Gym Mobile Reports

As a **gym owner/manager**,
I want to view reports on mobile,
So that I can check performance on the go.

**Acceptance Criteria:**

**Given** I am in the Gym Mobile app (owner/manager role)
**When** I access reports
**Then** I can view key reports: Revenue, Attendance, Membership Health
**And** reports are mobile-optimized (simplified views)
**And** I can select date ranges

**Implements:** Port of Epic 12 (Story 12.7) - mobile-optimized

---

### Story 15.10: Gym Mobile Push Notifications

As a **gym staff member**,
I want to receive push notifications,
So that I'm alerted to important events.

**Acceptance Criteria:**

**Given** I have the Gym Mobile app installed
**When** relevant events occur
**Then** I receive push notifications for: new bookings, cancellations, failed payments, at-risk members
**And** tapping opens the relevant screen

**Implements:** Epic 9 - gym-side mobile push

---

### Story 15.11: Gym Mobile App Store Submission

As a **developer**,
I want to submit the Gym Mobile app to app stores,
So that gym staff can download it.

**Acceptance Criteria:**

**Given** the Gym Mobile app is complete
**When** I submit to app stores
**Then** EAS Build creates production builds for iOS and Android
**And** App Store assets are prepared
**And** Camera permission justification is included (QR scanning)
**And** App is submitted and approved

---
