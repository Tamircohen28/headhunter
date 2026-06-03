---
name: scaffold-base44-app
description: Developer mode — scaffold or regenerate the HeadHunter Base44 React web app (Vite + React + Tailwind + shadcn/ui + Base44 SDK) and its entities/functions. Triggers on build headhunter app, base44, scaffold react app, regenerate entities.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Scaffold Base44 App (developer mode)

Reproduce the HeadHunter web app from the documented data model and server
functions. Use `references/data-model.md`, `references/status-config.md`, and
`references/server-functions.md` as the source of truth.

## Stack

- Vite + React 18 + React Router 6
- TanStack Query for data fetching/caching
- Tailwind CSS + shadcn/ui (semantic tokens: `background`, `foreground`,
  `card`, `border`, `primary`, `muted`)
- `@base44/sdk` client; auth via Base44 `AuthContext` pattern
- Recharts for dashboard charts

## Entities

Generate Base44 entity schemas (`base44/entities/*.jsonc`) from the tables in
`references/data-model.md`: JobApplication, InterviewRound, Task, Contact, Note
— including every field, type, and enum.

## Server functions

Generate Deno functions (`base44/functions/*/entry.ts`) from
`references/server-functions.md`: gmailJobScanner, syncInterviewToCalendar,
syncApplicationToNotion, syncTaskToNotion, syncTaskToGoogleTasks,
syncTaskToTodoist, sendStaleApplicationReminders, sendWhatsAppReminders.

## Pages & layout

Pages: Dashboard, Pipeline, Applications, ApplicationDetail, CalendarView,
Tasks, Contacts, Settings. Layout: sidebar nav + TopBar with notifications bell.
ApplicationDetail tabs: Interviews, Tasks, Contacts, Notes, Timeline, Insights.

## UI principles

Status colors from `references/status-config.md`. Friendly empty states,
centered spinner + skeleton cards on load, responsive grid with collapsible
sidebar (`use-mobile` hook pattern).

## Non-goals

Do not build Stripe billing, multi-tenant admin, public job-board scraping, or
native mobile apps.
