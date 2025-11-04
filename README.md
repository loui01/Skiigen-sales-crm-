# Skiigen CRM Project Plan

## Vision
Skiigen CRM enables outbound sales teams to efficiently manage call campaigns and track lead outcomes. The platform will deliver a focused, startup-quality experience for both sales managers (admins) and sales reps (users), emphasizing clarity, modularity, and real-time visibility into pipeline performance.

## Personas & Goals
- **Admin (Sales Manager / Owner)**
  - Upload curated CSV lead lists by region.
  - Distribute call assignments to individual reps.
  - Monitor performance (calls completed, outcomes, conversions).
  - Maintain data hygiene and update lead statuses.
- **Sales Rep (Caller / SDR)**
  - View prioritized queue of assigned leads.
  - Click-to-call directly from the CRM.
  - Log call notes, disposition (Failed, Warm, Closed, etc.), and follow-up tasks.
  - Track personal progress throughout the day.

## Core Features
1. **Lead Intake & Management**
   - CSV import aligned to the target schema: `Name, Formatted phone number, Street number, Street, City, Region, Postal code, Country, Url, Website present (Y/N), Lat, Lng`.
   - Region-based batching to support campaign-level organization.
   - Automatic data validation, deduplication, and enrichment hooks.

2. **Assignment Engine**
   - Admin-managed assignment of lead batches to reps (manual and future automated options).
   - Lead lifecycle states: _New → In Progress → Completed_ with dispositions (_Failed, Warm, Closed_).

3. **Rep Workspace**
   - Responsive list/table with filtering by assignment, status, and priority.
   - Lead detail drawer/modal with click-to-call, notes, timeline, and follow-up scheduling.
   - Quick actions for disposition updates and note templates.

4. **Admin Analytics & Oversight**
   - Dashboards summarizing call volume, conversion rates, and disposition mix per rep, per region, and overall.
   - Activity feeds for auditability (call logs, note edits, reassignment history).

5. **Notifications & Collaboration (Phase 2+)**
   - Daily summary emails/slack notifications.
   - Escalation workflow for hot leads or stalled prospects.

## Information Architecture
- **Regions** group lead batches and support workload segmentation.
- **Leads** hold contact and location information plus status, notes, and interaction history.
- **Assignments** map leads to reps with metadata (priority, due date).
- **Call Logs** capture each call attempt, outcome, and timestamp.
- **Users** distinguished by roles (Admin, Rep) with RBAC enforced throughout the app.

## Data Model (Initial Draft)
- `User`: id, name, email, role, phone, active
- `Region`: id, name, description
- `Lead`: id, region_id, name, formatted_phone, street_number, street, city, region_name, postal_code, country, url, has_website, latitude, longitude, status, last_contacted_at
- `Assignment`: id, lead_id, assignee_id, assigned_by, assigned_at, priority, due_at
- `CallLog`: id, lead_id, user_id, disposition, notes, duration, called_at
- `Note`: id, lead_id, user_id, body, created_at

## CSV Import Flow
1. Admin uploads a CSV per region (enforced column mapping & validation feedback).
2. Server normalizes phone numbers, geocodes if missing, and stores leads.
3. Admin confirms assignments (bulk assign to reps or auto-split evenly).
4. System queues leads for reps and triggers notification.

## User Journeys
### Admin
1. Sign in → Upload region CSV → Review parsed data → Assign to reps → Monitor dashboard.
2. Reassign leads as needed → Export metrics for reporting.

### Sales Rep
1. Sign in → See “My Queue” sorted by priority → Click a lead → Start call.
2. Log disposition and notes → Set follow-up reminders → Move to next lead.
3. Review personal performance dashboard.

## Technical Stack (Proposed)
- **Frontend**: React (TypeScript) + Vite, Tailwind or Chakra UI for rapid styling, Zustand/Redux for state as needed.
- **Backend**: Node.js (NestJS or Express + TypeScript) or Django REST Framework (Python) depending on team preference; RESTful API with future GraphQL option.
- **Database**: PostgreSQL (leveraging PostGIS extensions for geo data).
- **Auth**: JWT-based sessions via Auth0 / custom provider (supports role-based access).
- **Telephony Integration**: Twilio Voice SDK or similar for click-to-call and call logging.
- **Deploy**: Dockerized services; CI/CD through GitHub Actions; hosting on Render/Heroku/AWS.

## Milestones
1. **Foundation (Week 1-2)**
   - Confirm tech stack & project setup.
   - Implement authentication and role-based navigation shells.
   - Set up database schema & migrations.

2. **Lead Management (Week 3-4)**
   - CSV ingestion pipeline with validation UI.
   - Lead list views for admin and rep.
   - Assignment workflows and statuses.

3. **Rep Workspace (Week 5-6)**
   - Lead detail view with notes & disposition updates.
   - Click-to-call integration (initial Twilio setup).
   - Personal metrics dashboard.

4. **Admin Analytics (Week 7-8)**
   - Aggregated KPIs by rep, region, and campaign.
   - Export/reporting capabilities.
   - QA + usability polishing.

5. **Enhancements (Post-MVP)**
   - Notification system, SLA tracking, automated assignment rules.
   - Integrations with CRM/marketing tools (HubSpot, Salesforce).

## Design Principles
- **Clarity**: Minimal clutter, emphasize actionable data.
- **Speed**: Optimistic UI updates, caching, and fast navigation.
- **Modularity**: Component-driven frontend and service-oriented backend.
- **Auditability**: Every interaction is tracked with timestamps and ownership.

## Next Steps
1. Gather branding assets and finalize UI design system.
2. Decide on backend framework and telephony provider.
3. Scaffold repositories (frontend, backend, infrastructure) following this plan.
4. Begin implementation with Foundation milestone tasks.

