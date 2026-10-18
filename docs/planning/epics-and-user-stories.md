# Lunch Roulette — Epics and User Stories

**Source documents:** [business-prd.md](../prd/business-prd.md) ·
[technical-prd.md](../prd/technical-prd.md) · [GLOSSARY.md](../prd/GLOSSARY.md)

Capitalised terms (Colleague, Location, Round, Sign-up, Match, Lunch Group,
Host, Lunch Slot, Cancelled Round, Withdrawal, Admin) use the glossary
definitions exactly. Each story cites the business rule(s) (R/M/W/A) or
technical requirement it implements where one exists.

Story IDs are `<epic-no>.<story-no>` (e.g. `1.1`). "Done" for every story
also requires the relevant case/activity events described in
[Epic 8](#epic-8-process-event-log--success-measures) to be recorded; this is
called out only where a story introduces a new activity, to avoid repeating
it in every acceptance criterion.

---

## Epic 1 — Colleague identity, sign-in and account

Lets anyone with an allowed company email become a Colleague, sign in
without a password, and manage their own account and data.

### 1.1 Request a sign-in link

As a person with a company email address, I want to request a sign-in link,
so that I can access the app without creating a password.

- Covers: Q7, journey §5.1 steps 1–2.
- Acceptance criteria:
  - Given I enter an email address on an allowed company domain, when I
    submit it, then a one-time sign-in link is emailed to that address.
  - Given I enter an email address that is **not** on an allowed company
    domain, when I submit it, then the request is rejected and no email is
    sent.
  - Given the "allowed company domains" list is empty or misconfigured,
    when the app starts, then it fails to start rather than silently
    accepting every domain.
  - The sign-in link email cannot be turned off (business PRD §7).
  - In development, the email is written to the console instead of sent
    through a real provider (technical PRD §3).

### 1.2 Sign in with the emailed link

As a Colleague, I want to click my emailed link and be signed in, so that I
don't need to remember a password.

- Acceptance criteria:
  - Given a valid, unused, unexpired sign-in link, when I open it, then I am
    signed in.
  - Given a link that was already used, or has expired, when I open it, then
    I am shown an error and can request a new one.
  - Given I have no Colleague record yet, when I sign in for the first time,
    then I am taken to the first-sign-in profile setup (Story 1.3) before
    reaching the rest of the app.

### 1.3 Complete first sign-in (self-registration)

As a new Colleague, I want to give my name and pick my home Location on
first sign-in, so that I can start taking part in Rounds.

- Covers: A1, Q16, journey §5.1 step 3.
- Acceptance criteria:
  - Given I am signing in for the first time, when I submit my name and
    choose one existing Location as my home Location, then a Colleague
    record is created and I land in the normal app.
  - Given no Location exists yet, when I try to complete first sign-in,
    then I'm told no Location is available yet rather than being allowed to
    proceed with an invalid Location.
  - There is no invitation or bulk import path — anyone with an allowed
    email registers themselves (A1).

### 1.4 Change my home Location

As a Colleague, I want to change my home Location, so that I can take part
in Rounds at my new office.

- Covers: A2.
- Acceptance criteria:
  - Given I change my home Location, when the change is saved, then any
    Sign-up I hold for a Round at my old Location that has **not** yet been
    matched is removed.
  - Given I change my home Location, when the change is saved, then Lunch
    Groups I already belong to (already matched) are unaffected.
  - Given I change my home Location, when I next view Rounds, then I can
    only sign up for Rounds at my new home Location (R4).

### 1.5 Turn off the "sign-ups are open" email

As a Colleague, I want to turn off the weekly "sign-ups are open" reminder,
so that I stop getting an email I don't act on.

- Covers: business PRD §5.1 role table, §7 notifications table.
- Acceptance criteria:
  - Given I turn the setting off, when the next Round opens at my home
    Location, then I do not receive a "sign-ups are open" email.
  - Given I turn the setting back on, when the next Round opens, then I
    receive the email again.
  - All other notifications in §7 (sign-in link, your Lunch Group, Round
    cancelled, someone withdrew, lunch is off) cannot be turned off and are
    unaffected by this setting.

### 1.6 Delete my account

As a Colleague, I want to delete myself, so that my personal data is
removed while past groups still make sense to the people I shared them
with.

- Covers: A4.
- Acceptance criteria:
  - Given I delete my account, when the deletion completes, then my name,
    email and sign-in records are removed.
  - Given I previously shared a Lunch Group with other Colleagues, when
    they view that past Lunch Group after my deletion, then I appear as
    "a former colleague" instead of my name.
  - Given I have an open Sign-up or an active (not yet happened) Lunch
    Group at the time of deletion, when deletion completes, then I am
    removed from them consistently with Withdrawal behaviour (Epic 5),
    including notifying remaining members.

### 1.7 View my own Lunch Group history

As a Colleague, I want to see my own past Lunch Groups, so that I can
recall who I've had lunch with.

- Covers: A3.
- Acceptance criteria:
  - Given I have past Lunch Groups, when I open my history, then I see each
    past Round's Lunch Group: date, Location, fellow members (or "a former
    colleague" for deleted Colleagues) and who was Host.
  - Given another Colleague's history, when I try to view it, then I cannot
    — a Colleague sees only their own history (A3).
  - The Match uses everyone's history to avoid repeats (M3), but no
    Colleague-facing view exposes another Colleague's history.

---

## Epic 2 — Admin management of Locations and schedules

Lets Admins set up each office as a Location with its own time zone and
weekly schedule, without being able to intervene in individual Rounds.

### 2.1 Identify as an Admin

As the system, I want to recognise Colleagues on the configured Admin email
list as Admins, so that only authorised people can manage Locations.

- Covers: A... / Q17, role table §4.
- Acceptance criteria:
  - Given a signed-in Colleague's email is on the configured Admin list,
    when they use the app, then they see Admin-only actions (create/edit
    Location) in addition to everything a Colleague can do.
  - Given a Colleague's email is removed from the Admin list, when they
    next load the app, then Admin-only actions are no longer available to
    them.
  - Admin status grants no ability to run, skip, or otherwise intervene in
    an individual Round (business PRD §4, §6 non-goals).

### 2.2 Create a Location

As an Admin, I want to create a Location with a name and time zone, so that
Colleagues at that office can take part in Rounds.

- Covers: journey §5.4.
- Acceptance criteria:
  - Given I submit a name and a time zone, when I save, then a new Location
    is created with the default schedule: Sign-ups open Monday 09:00, close
    Tuesday 12:00, Lunch Slot Thursday 12:00, all in the Location's time
    zone (Q26).
  - Given a Location is created, when its first scheduled opening time
    arrives, then its first Round opens automatically (R1) with no further
    Admin action.

### 2.3 Edit a Location's schedule

As an Admin, I want to change a Location's sign-ups-open time, sign-ups-close
time (= Match time) and Lunch Slot, so that the Round cadence fits that
office.

- Covers: journey §5.4, R1, R2.
- Acceptance criteria:
  - Given I change the schedule, when I save, then future Rounds at that
    Location use the new day/time values; a Round already open or already
    matched is unaffected.
  - Given I change a Location's time zone, when I save, then all of that
    Location's displayed and scheduled times are shown and evaluated in the
    new time zone (R2).
  - Given I enter a close time that is not after the open time, when I try
    to save, then the save is rejected with a clear error.

---

## Epic 3 — Round lifecycle (open, sign up, close)

Runs each Location's weekly Round automatically and lets Colleagues opt in
or out before sign-ups close.

### 3.1 Open a Round automatically on schedule

As a Colleague, I want each week's Round to open on its own, so that I never
have to wait on someone else to start it.

- Covers: R1, R2, journey §5.2.
- Acceptance criteria:
  - Given a Location's scheduled opening day/time arrives in that
    Location's time zone, when the system checks schedules, then exactly
    one new Round opens for that Location (R1).
  - Given a Round is open, when Colleagues at that Location haven't opted
    out of the reminder (Story 1.5), then they receive a "sign-ups are
    open" email.
  - Given a Round for a Location is still open, when its next scheduled
    opening time arrives, then no second Round opens for that Location
    until the current one has closed.

### 3.2 Sign up for the open Round

As a Colleague, I want to opt in to this week's Round at my home Location,
so that I can be matched into a Lunch Group.

- Covers: R3, R4, journey §5.2.
- Acceptance criteria:
  - Given a Round is open at my home Location, when I sign up, then my
    Sign-up is recorded for that Round only — it does not carry over to any
    future Round (R3).
  - Given a Round is open at a Location that is **not** my home Location,
    when I try to sign up, then I am not able to (R4).
  - Given I have already signed up for this Round, when I view it again,
    then I see that I'm signed up rather than being able to sign up twice.
  - Signing up produces no notification to anyone (only the opening and
    closing of a Round, and the Match, generate emails — see §7).

### 3.3 Withdraw a Sign-up before close

As a Colleague, I want to remove my Sign-up before sign-ups close, so that I
can change my mind without consequence.

- Covers: Q20, journey §5.2.
- Acceptance criteria:
  - Given I have a Sign-up for a Round that has not yet closed, when I
    remove it, then I am no longer counted for that Round's Match.
  - Given I remove a Sign-up before close, when the removal completes, then
    nobody is notified (removal before close is silent, per Q20) — this is
    distinct from Withdrawal after the Match (Epic 5), which does notify.
  - Given sign-ups have already closed, when I try to remove my Sign-up,
    then I cannot; the next available action is Withdrawal (Epic 5), once
    the Match has produced a Lunch Group.

### 3.4 Close a Round on schedule and hand off to matching

As a Colleague, I want sign-ups to close automatically at the scheduled
time, so that the Match can run without anyone remembering to trigger it.

- Covers: R1, R2, M1, journey §5.2.
- Acceptance criteria:
  - Given a Location's scheduled close day/time arrives in that Location's
    time zone, when the system checks schedules, then that Round's
    sign-ups close and no further Sign-ups or withdrawals of a Sign-up are
    accepted for it.
  - Given sign-ups for a Round have just closed, when the system proceeds,
    then the Match (Epic 4) runs using only that Round's Sign-ups (M1).

---

## Epic 4 — Matching

Turns one Round's Sign-ups into Lunch Groups of the right size, avoiding
recent repeats, with a randomly chosen Host, or cancels the Round if too few
signed up.

### 4.1 Form Lunch Groups from a Round's Sign-ups

As a Colleague who signed up, I want to be placed into a small Lunch Group
when sign-ups close, so that I have people to have lunch with.

- Covers: M1, M2, journey §5.2.
- Acceptance criteria:
  - Given sign-ups just closed for a Round with 3 or more Sign-ups, when
    the Match runs, then every signed-up Colleague is placed into exactly
    one Lunch Group of 3 or 4 members (M2).
  - Given exactly 5 Sign-ups, when the Match runs, then one Lunch Group of
    5 is formed instead of a group of 3 and a group of 2 (M2).
  - Given fewer than 3 Sign-ups, when the Match runs, then no Lunch Group
    is formed and the Round becomes a Cancelled Round (Story 4.4, M2).
  - Given the Match has run for a Round, when it is checked again, then it
    is not re-run — a Round is matched exactly once.

### 4.2 Avoid recent repeat pairings

As a Colleague, I want to avoid being grouped with people I've recently had
lunch with, so that I keep meeting new colleagues.

- Covers: M3, Q8.
- Acceptance criteria:
  - Given two Colleagues shared a Lunch Group in any of the last 4 Rounds
    at their Location, when the Match runs, then it avoids placing them in
    the same Lunch Group again.
  - Given avoiding all repeats is impossible for a given set of Sign-ups,
    when the Match runs, then it minimises the number of repeat pairings
    rather than leaving any signed-up Colleague out of a Lunch Group (M3).
  - Given the repeat-avoidance window, when counting "the last 4 Rounds",
    then only Rounds at the same Location count, and Cancelled Rounds (no
    Lunch Groups formed) do not count toward the 4.

### 4.3 Assign a Host to each Lunch Group

As a member of a newly formed Lunch Group, I want one member picked at
random as Host, so that someone is nudged to kick off the lunch.

- Covers: M4.
- Acceptance criteria:
  - Given a Lunch Group is formed, when the Match completes, then exactly
    one member is chosen at random as Host.
  - Given a member is the Host, when they or other members use the app,
    then being Host grants no additional permissions — it's a nudge, not a
    role (M4).

### 4.4 Cancel a Round with too few Sign-ups

As a Colleague who signed up for a Round that didn't get enough interest, I
want to be told lunch isn't happening, so that I'm not left waiting.

- Covers: M2, §7 notifications table.
- Acceptance criteria:
  - Given fewer than 3 Colleagues signed up when sign-ups close, when the
    Match runs, then the Round is marked a Cancelled Round and no Lunch
    Groups are created.
  - Given a Round is cancelled, when cancellation completes, then every
    Colleague who signed up for it receives a "Round cancelled" email; this
    cannot be turned off.
  - A Cancelled Round does not count as one of the "last 4 Rounds" used for
    repeat avoidance (Story 4.2).

### 4.5 Notify each Lunch Group of their Match

As a matched Colleague, I want an email with my Lunch Group's names,
emails, Host and Lunch Slot, so that I know who I'm having lunch with and
when.

- Covers: M1, M4, §7 notifications table, journey §5.2.
- Acceptance criteria:
  - Given the Match forms a Lunch Group, when it completes, then every
    member receives an email listing all members' names and emails, who
    the Host is, and the Location's Lunch Slot (day/time).
  - This email cannot be turned off (§7).
  - No in-app chat or messaging is provided; coordination happens over the
    emailed addresses (business PRD §6 non-goals, §5.2).

---

## Epic 5 — After the Match: Withdrawal and Host re-pick

Lets a Colleague leave their Lunch Group after matching without being
replaced, re-picks a Host if needed, and dissolves a group reduced to one
person.

### 5.1 Withdraw from my Lunch Group

As a matched Colleague, I want to withdraw from my Lunch Group before the
Lunch Slot, so that the others know I'm not coming.

- Covers: W1, Q12, Q19, journey §5.3.
- Acceptance criteria:
  - Given I am a member of a Lunch Group and the Lunch Slot has not yet
    started, when I withdraw, then I am removed from the Lunch Group.
  - Given the Lunch Slot has already started, when I try to withdraw, then
    I cannot (W1).
  - Given I withdraw, when withdrawal completes, then no replacement member
    is added (W1) and the remaining members are emailed that I withdrew
    (§7), an email that cannot be turned off.

### 5.2 Re-pick the Host when the Host withdraws

As a remaining member of a Lunch Group, I want a new Host picked if the
current Host withdraws, so that the group still has a Host.

- Covers: W2, Q13, Q19.
- Acceptance criteria:
  - Given the Host withdraws and at least 2 members remain, when the
    withdrawal is processed, then a new Host is chosen at random from the
    remaining members.
  - Given a new Host is picked, when the pick completes, then the "someone
    withdrew" notification to remaining members also identifies the new
    Host (§7 notifications table).
  - Given a non-Host member withdraws, when the withdrawal is processed,
    then the existing Host is unchanged.

### 5.3 Dissolve a Lunch Group down to one person

As the last remaining member of a Lunch Group, I want to be told lunch is
off, so that I don't wait for a lunch that won't happen.

- Covers: W3, Q19, journey §5.3.
- Acceptance criteria:
  - Given withdrawals reduce a Lunch Group to exactly one remaining member,
    when the last withdrawal is processed, then the Lunch Group is
    dissolved.
  - Given a Lunch Group is dissolved, when dissolution completes, then the
    one remaining Colleague receives a "lunch is off" email (§7), which
    cannot be turned off.
  - A dissolved Lunch Group is not replaced or re-matched (business PRD §6
    non-goals: no replacement of a withdrawing Colleague).

---

## Epic 6 — Material Design 3 interface

Delivers a usable, on-brand, responsive interface, built from the
repository's Material Design 3 source.

### 6.1 Apply Material Design 3 styling with the brand colour

As a Colleague, I want the app to look consistent and on-brand, so that it
feels like a real product, not a prototype.

- Covers: Q18, business PRD §8, technical PRD §5.
- Acceptance criteria:
  - Given the app renders any screen, when styled, then it uses Material
    Design 3 components and uses the design source at
    `design/material_design_3/` as the implementation basis.
  - Given the configured brand seed colour (environment variable, technical
    PRD §3), when the app builds its colour scheme, then light and dark
    theme palettes are derived from that single seed colour.
  - Given my device/browser is set to dark mode, when I open the app, then
    it renders in the dark theme automatically; light mode renders the
    light theme, with no manual in-app toggle required by this story.

### 6.2 Use the app comfortably on a phone

As a Colleague who often opens emails on my phone, I want the web app to
work well on a small screen, so that I can sign up and check my Lunch Group
without a laptop.

- Covers: business PRD §8.
- Acceptance criteria:
  - Given I open the app on a phone-sized viewport, when I view sign-up,
    Lunch Group, history and Admin (if applicable) screens, then all
    content and actions are usable without horizontal scrolling or
    overlapping elements.
  - Given I follow a link from a notification email on my phone, when the
    linked page loads, then it renders correctly at phone width.

---

## Epic 7 — Deployment, configuration and runtime

Packages the application as a single container with environment-driven
configuration, backed by PostgreSQL, so it can be deployed to a
hosting platform chosen at deployment time.

### 7.1 Run the application as one Docker container

As an operator, I want to deploy Lunch Roulette as a single container, so
that hosting it doesn't require assembling multiple services by hand.

- Covers: Q27, technical PRD §2.
- Acceptance criteria:
  - Given the repository is built, when the build completes, then one
    Docker image is produced that runs the Python/FastAPI application as a
    single process.
  - Given that image is run against a reachable PostgreSQL instance, when
    the container starts, then the application becomes available without
    needing a second application container.
  - No specific hosting platform is assumed by the build or the image; the
    platform is chosen at deployment time (technical PRD §2).

### 7.2 Configure the deployment through environment variables

As an operator, I want to configure allowed domains, Admins, branding and
email delivery through environment variables, so that I can deploy the same
image to different environments without code changes.

- Covers: Q28, technical PRD §3.
- Acceptance criteria:
  - Given environment variables for allowed company domains, the Admin
    email list, the brand seed colour and email delivery settings, when the
    container starts, then it applies exactly those values with no
    additional config file required.
  - Given email delivery settings indicate development/console mode, when
    an email would be sent, then its content is written to the console
    instead of dispatched to a real provider (technical PRD §3).
  - Given a required configuration value is missing (e.g. no allowed
    domains, no database connection), when the container starts, then it
    fails fast with a clear error rather than starting in an unsafe default
    state.

### 7.3 Persist data in PostgreSQL

As an operator, I want all application data stored in PostgreSQL, so that
data survives container restarts and can be backed up with standard tools.

- Covers: Q22, technical PRD §2.
- Acceptance criteria:
  - Given the application starts, when it needs to read or write Colleague,
    Location, Round, Sign-up, Lunch Group or process-event data, then it
    uses the configured PostgreSQL database for all of it (no SQLite, no
    in-memory-only storage in non-development use).
  - Given the supported environment, when PostgreSQL is provisioned, then
    it runs in Docker alongside the application image (technical PRD §2).

---

## Epic 8 — Process event log & success measures

Records every step of every Round as process events so that the proposed
success measures can be calculated and participation drop-off analysed,
with a structure suited to process-mining tools such as Celonis.

### 8.1 Record a process event for every Round step

As a product owner, I want every meaningful step of a Round recorded as an
event, so that I can analyse what happens between opening a Round and
having lunch.

- Covers: technical PRD §4.
- Acceptance criteria:
  - Given any of the following occurs — Round opens, Sign-up created,
    Sign-up removed before close, sign-ups close, Match runs (including
    Cancelled Round), Lunch Group formed, Withdrawal, Host re-picked, Lunch
    Group dissolved, Colleague deleted/anonymised — when it occurs, then
    one process event is written with a case (the Round or Lunch Group it
    belongs to), an activity name, and a timestamp.
  - Given a process event is written, when it is queried, then it is
    immutable (append-only) and attributable to a specific Location.
  - The event log's structure supports export/analysis compatible with
    process-mining tools, including future Celonis use (technical PRD §4).

### 8.2 Calculate the proposed success measures from the event log

As a product owner, I want the proposed success measures computed from
recorded events, so that I can see whether the product is working without
manual data gathering.

- Covers: business PRD §9, technical PRD §4.
- Acceptance criteria:
  - Given a date range and a Location, when the share of Colleagues who
    signed up at least once that month is requested, then it is computed
    from Sign-up events, not estimated.
  - Given a Location, when the share of Rounds that are **not** Cancelled
    Rounds is requested, then it is computed from Round and Match events.
  - Given a Location, when the Withdrawal rate per Lunch Group is
    requested, then it is computed from Withdrawal events relative to
    matched Lunch Groups.
  - Given a Location, when the share of Lunch Groups with no repeat pairing
    from the last 4 Rounds is requested, then it is computed from Match
    events and the repeat-avoidance data used in Story 4.2.
  - Given the elapsed time from sign-ups opening to a given Sign-up, when
    requested, then it is computed from the Round-opened and Sign-up-created
    event timestamps (technical PRD §4).

---

## Epic summary

| Epic | Title | Primary rules covered |
|---|---|---|
| 1 | Colleague identity, sign-in and account | A1–A4, Q7, Q16 |
| 2 | Admin management of Locations and schedules | R1, R2, Q17, Q21, Q26 |
| 3 | Round lifecycle (open, sign up, close) | R1–R4, Q20 |
| 4 | Matching | M1–M4, Q8, Q11, Q13 |
| 5 | After the Match: Withdrawal and Host re-pick | W1–W3, Q12, Q19 |
| 6 | Material Design 3 interface | Q18 |
| 7 | Deployment, configuration and runtime | Q1, Q22, Q27, Q28 |
| 8 | Process event log & success measures | technical PRD §4, business PRD §9 |

## Explicit non-goals carried over (not covered by any story above)

Per business PRD §6, the following are deliberately out of scope for v1 and
must not be implemented by any story's design: multi-tenant support;
cross-Location or virtual matching; matching on availability, department,
interests or seniority; restaurant choice/suggestion/booking; in-app
chat/messaging; Slack/Teams integration or mobile apps; an Admin
"skip this week" switch (a quiet week becomes a Cancelled Round on its own);
replacing a Colleague who withdraws.
