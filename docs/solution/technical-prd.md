# Lunch Roulette — Technical PRD

**Status:** Initial technical constraints extracted from the 2026-10-17 design
interview

**Companion documents:** [business-prd.md](business-prd.md) ·
[GLOSSARY.md](GLOSSARY.md)

## 1. Purpose

This document owns the implementation, deployment and technical-operability
requirements for Lunch Roulette. Product outcomes, user journeys, business
rules, notification behaviour, visual experience and success measures remain
in the [Business PRD](business-prd.md).

## 2. Application and data architecture

- The application uses Python and FastAPI and runs as one application process.
- PostgreSQL is the database and is available in Docker for the supported
  environment.
- The application is delivered as one Docker container.
- The hosting platform is chosen at deployment time.

## 3. Configuration and development email

- Deployment-specific configuration is supplied through environment
  variables.
- Configuration includes the allowed company domains, Admin email list, brand
  seed colour and email delivery settings.
- In development, email can be written to the console so sign-in and
  notification flows can be exercised without an external email provider.

## 4. Measurement and process data

The application records every step of every Round in a process event log. Each
event contains a case, an activity and a timestamp. The log must contain enough
information to calculate the proposed measures in
[Business PRD §9](business-prd.md#9-success-measures-proposed) and to analyse
where Rounds lose participants, including:

- elapsed time from sign-ups opening to a Sign-up;
- Withdrawal rates by Location;
- repeat pairings across the previous four Rounds at a Location.

The event structure is intended to support process-mining analysis, including
future Celonis use.

## 5. Design implementation source

The interface implements the Material Design 3 product requirement using the
repository design source at `design/material_design_3/`. The configured brand
seed colour supplies the light and dark theme colour schemes.

## 6. Technical and delivery decisions log

The original interview identifiers are retained so the decisions remain
traceable to the 2026-10-17 design interview.

| # | Decision |
|---|---|
| Q1 | Built in this repository by the software factory |
| Q22 | Python/FastAPI, one process; PostgreSQL in Docker replaces SQLite |
| Q27 | Delivered as one Docker container; hosting chosen at deployment |
| Q28 | Configuration from environment variables; console email in development |
