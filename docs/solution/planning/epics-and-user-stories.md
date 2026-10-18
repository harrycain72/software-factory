# Lunch Roulette — Epics and User Stories

**Status:** draft backlog for factory intake, 2026-10-18
**Sources (the only truth):** [business-prd.md](../solution/business-prd.md)
(cited as **BP**) · [technical-prd.md](../solution/technical-prd.md) (cited
as **TP**) · [GLOSSARY.md](../solution/GLOSSARY.md) ·
[domain-map.md](../solution/domain-map.md)
**Objective:** [epics-and-stories-objective.md](epics-and-stories-objective.md)

**Source check, 2026-10-18:** the objective now reads the domain map from
`docs/solution/domain-map.md` instead of `bce-architecture.md`. Both list the
same five domains with the same owned concepts, and the same `platform`
placement for the interface and the container, configuration and PostgreSQL
setup. Every story's domain, its locks, its split points, its dependencies and
the waves are therefore unchanged. Only the source link and OQ-21 and OQ-22
were updated.

Capitalised terms (Colleague, Location, Round, Sign-up, Match, Lunch Group,
Host, Lunch Slot, Cancelled Round, Withdrawal, Admin) mean exactly what the
glossary says. Stories carry behaviour only; architecture rules reach them
later through each story's `spec.md`.

## How to read this backlog

- **ID** is `<epic>.<story>`. The factory assigns `US-###` at intake. Stories
  are numbered in dependency order: every story depends only on stories with
  a lower ID, so backlog order is always a valid admission order.
- **Domain** is one domain from the map (`identity`, `locations`, `rounds`,
  `matching`, `process-log`) or `platform`.
- **Covers** cites business rules (R, M, W, A), decisions (Q), BP/TP
  sections, journey steps and notifications. The coverage table at the end
  inverts this.
- **Acceptance criteria** are numbered Given/When/Then statements. Each names
  one observable outcome and can be tested on its own.
- **Locks** are narrow `<domain>-<area>` names. Two extra rules keep parallel
  jobs from colliding:
  - Each domain has one `<domain>-schema` lock. A story holds it whenever it
    adds or changes that domain's tables, so two jobs never append competing
    migrations to the same domain's migration chain.
  - Epic 0 alone holds `dependencies`, `migrations`, `compose` and
    `repo-profile`. Later stories use the dependencies Epic 0 installs and add
    tables only through their own domain's migrations, so their locks stay
    domain-scoped.
- **Process events.** Story 1.1 provides the process event log. Every later
  story that performs a Round step names the activity it records; that
  criterion is part of its definition of done (TP §4).
- **Cross-domain hand-offs.** Where one domain reacts to another (a Location
  change removing a Sign-up, a deletion leaving a Lunch Group, rounds handing
  closed Sign-ups to the Match), the story is split so the reacting part sits
  in its own domain and depends on the earlier story that provides the
  trigger.

## Epics

| # | Epic | Capability gained |
|---|---|---|
| 0 | App skeleton | Builders get a runnable, configurable, deployable app with a database, development email, tests and a base page layout to build every later story on. |
| 1 | Process event log | An operator gets an append-only log of every Round step that process-mining tools can analyse. |
| 2 | Sign-in | A person with an allowed work email can sign in through an emailed one-time link without a password. |
| 3 | Locations and schedules | Admins can set up each office as a Location with its time zone and weekly schedule, which every Round follows. |
| 4 | Colleague account | A Colleague can register, keep their home Location and email preference up to date, and delete themselves. |
| 5 | Lunch Groups | Colleagues who signed up are put into small random Lunch Groups with a Host, avoiding recent repeats, and can see their group and history. |
| 6 | Weekly Rounds | Each Location runs a Round every week on its own, from opening sign-ups to the Lunch Slot, with no one operating it. |
| 7 | Withdrawal | A Colleague can leave their Lunch Group before the Lunch Slot, and the group adapts without anyone stepping in. |
| 8 | Success measures | An operator can calculate the proposed success measures and drop-off analyses from the process event log. |

---

## Epic 0 — App skeleton

Builders get a runnable, configurable, deployable app with a database,
development email, tests and a base page layout to build every later story
on. Admitted alone.

### 0.1 Runnable, deployable app skeleton

- **Domain:** platform
- **Story:** As a builder of later stories, I want a running Lunch Roulette
  application with its database, configuration, email path, test harness and
  base layout in place, so that every later story only adds behaviour inside
  its own domain.
- **Covers:** TP §2 (Python/FastAPI, one process; PostgreSQL in Docker; one
  Docker container; hosting chosen later), TP §3 (environment configuration;
  console email in development), TP §5 (Material Design 3 from
  `design/material_design_3/`, brand seed colour), BP §8 (light and dark
  themes following the device, one brand colour, usable on a phone), Q18,
  Q22, Q27, Q28, Q1
- **Scope:** the deliverable contains
  - one FastAPI application process with an unversioned health check;
  - one Docker image that runs the application, and a Compose setup with
    PostgreSQL for development and tests;
  - environment-variable configuration for allowed company domains, the Admin
    email list, the brand seed colour, email delivery settings, the database
    connection, the public base URL used in emailed links and the session
    signing secret (the last two are not named in TP §3; see Open questions
    OQ-3);
  - startup that fails when configuration is missing or invalid;
  - an empty per-domain migration chain for `identity`, `locations`,
    `rounds`, `matching` and `process-log`, applied in one command;
  - a platform email transport with a console mode for development;
  - an in-process scheduler that runs jobs that domains register, against an
    injectable clock;
  - discovery of each domain's routes, migrations and scheduled jobs from the
    domain's own files, so later stories never edit a shared file to wire
    themselves in;
  - a test harness with one passing test, and real install, test, lint,
    format and type-check commands;
  - the base page layout using `design/material_design_3/` with the
    configured brand seed colour;
  - every dependency later stories need: web framework and ASGI server,
    PostgreSQL driver, migration tool, server-side templating, time-zone data,
    test runner with HTTP test client, linter, formatter and type checker
    (the spec chooses the packages);
  - `build.md` recording the real install, test, lint, format and type-check
    commands, and per-slot database create and drop under
    `## Factory isolation`.
- **Acceptance criteria:**
  1. Given the application is running with valid configuration and a
     reachable database, when the health check is requested, then it responds
     with a success status.
  2. Given the database is unreachable, when the health check is requested,
     then it responds with a failure status.
  3. Given any health check response, when its body is read, then it contains
     no configuration value, credential or user data.
  4. Given the Docker image is built and run with valid environment variables
     and a reachable PostgreSQL, when the health check is requested, then it
     responds with a success status.
  5. Given any required configuration value is missing, when the application
     starts, then startup fails with an error naming that variable.
  6. Given the allowed company domains value contains an entry that is not a
     domain name, when the application starts, then startup fails with an
     error naming that variable.
  7. Given the brand seed colour is not a valid colour value, when the
     application starts, then startup fails with an error naming that
     variable.
  8. Given an Admin email list entry that is not an email address, when the
     application starts, then startup fails with an error naming that
     variable.
  9. Given an empty database, when the migration command runs, then every
     domain's migration chain is recorded as applied.
  10. Given email delivery is set to console, when the application sends an
      email, then the email's recipient, subject and body appear on the
      console.
  11. Given email delivery is set to console, when the application sends an
      email, then no external email provider is contacted.
  12. Given a job registered with the scheduler for a due time, when the
      injected clock reaches that time, then the job runs once.
  13. Given a domain declares routes, migrations and scheduled jobs in its own
      package, when the application starts, then its routes respond without
      any shared file having been edited.
  14. Given a fresh checkout, when the recorded install and test commands run,
      then the one harness test passes.
  15. Given a fresh checkout, when the recorded lint, format and type-check
      commands run, then each exits successfully.
  16. Given a factory slot number, when the recorded per-slot create command
      runs, then a database exists that only that slot uses.
  17. Given a slot database exists, when the recorded per-slot drop command
      runs, then that database no longer exists.
  18. Given a page rendered with the base layout, when it is opened, then it
      uses the Material Design 3 stylesheet from `design/material_design_3/`.
  19. Given a configured brand seed colour, when a base-layout page is
      opened, then its colour scheme is generated from that seed colour.
  20. Given a device set to prefer a dark appearance, when a base-layout page
      is opened, then the dark colour scheme is shown.
  21. Given a device set to prefer a light appearance, when a base-layout page
      is opened, then the light colour scheme is shown.
  22. Given a 360-pixel-wide screen, when a base-layout page is opened, then
      no horizontal scrolling is needed.
- **Depends:** none
- **Locks:** dependencies, migrations, compose, repo-profile

---

## Epic 1 — Process event log

An operator gets an append-only log of every Round step that process-mining
tools can analyse.

### 1.1 Record process events

- **Domain:** process-log
- **Story:** As an operator, I want every Round step recorded as a process
  event with a case, an activity and a timestamp, so that I can measure
  Rounds and analyse where they lose participants with process-mining tools
  such as Celonis.
- **Covers:** TP §4 (event structure: case, activity, timestamp; supports
  process mining and future Celonis use), A4 (no personal data kept in the
  log), BP §9
- **Acceptance criteria:**
  1. Given another domain reports an activity for a case, when it is
     recorded, then the stored event holds that case identifier, activity
     name and timestamp.
  2. Given an activity reported with attributes (Location, Colleague
     reference, Lunch Group reference, count), when it is recorded, then the
     stored event holds those attributes.
  3. Given a reported activity whose attributes include a name or an email
     address, when it is recorded, then it is rejected.
  4. Given a recorded event, when later events are recorded, then the earlier
     event is unchanged.
  5. Given several events, including two with the same timestamp, when the
     log is read, then events come back in timestamp order with the same
     order on every read.
  6. Given events for several Locations, when the log is read for one
     Location, then only that Location's events are returned.
- **Depends:** 0.1
- **Locks:** process-log-events, process-log-schema

---

## Epic 2 — Sign-in

A person with an allowed work email can sign in through an emailed one-time
link without a password.

### 2.1 Sign in with an emailed link

- **Domain:** identity
- **Story:** As a person with a work email address, I want to enter my email
  and sign in through a one-time link sent to it, so that I can use Lunch
  Roulette without a password.
- **Covers:** A1, Q7, Q16, BP §5.1 steps 1–2, BP §7 "Sign-in link", TP §3
  (allowed company domains)
- **Acceptance criteria:**
  1. Given an email address at an allowed company domain, when I submit it on
     the sign-in page, then a sign-in link email is sent to that address.
  2. Given an email address at a domain that is not allowed, when I submit it,
     then I am told the address cannot be used.
  3. Given an email address at a domain that is not allowed, when I submit it,
     then no email is sent.
  4. Given an unused sign-in link within its lifetime (OQ-4), when I open it
     and confirm, then I am signed in.
  5. Given a sign-in link that has already been used, when I open it, then I
     am told it is no longer valid.
  6. Given a sign-in link past its lifetime, when I open it, then I am told it
     is no longer valid.
  7. Given I was told a sign-in link is no longer valid, when I look at the
     page, then it offers a way to request a new link.
  8. Given I am signed in and have not completed first sign-in, when I open
     any Colleague page, then I am sent to first sign-in.
  9. Given a 360-pixel-wide screen, when I open the sign-in page, then no
     horizontal scrolling is needed.
- **Depends:** 0.1
- **Locks:** identity-signin, identity-schema

---

## Epic 3 — Locations and schedules

Admins can set up each office as a Location with its time zone and weekly
schedule, which every Round follows.

### 3.1 Keep Locations with a time zone and weekly schedule

- **Domain:** locations
- **Story:** As an Admin, I want every Location kept with its time zone and a
  weekly schedule that starts as the default, so that every Round and every
  time shown at that Location follows it without extra setup.
- **Covers:** R2, Q21, Q26, BP §5.4 (name, time zone, default schedule),
  glossary Lunch Slot
- **Acceptance criteria:**
  1. Given a name and a valid time zone, when a Location is created, then its
     schedule is sign-ups open Monday 09:00, sign-ups close Tuesday 12:00 and
     Lunch Slot Thursday 12:00.
  2. Given a time zone that is not a recognised time-zone name, when a
     Location is created, then it is rejected.
  3. Given an empty name, when a Location is created, then it is rejected.
  4. Given several Locations, when the directory is listed, then every
     Location is returned with its name and time zone.
  5. Given a Location in `Europe/Berlin` with the default schedule, when the
     next sign-ups-open moment after a given instant is requested, then it is
     the following Monday 09:00 Berlin time.
  6. Given a Location whose next sign-ups-open falls in the week a
     daylight-saving change takes effect, when that moment is requested, then
     it is still 09:00 local time.
  7. Given a Location, when the sign-ups-close and Lunch Slot moments for the
     week of a sign-ups-open moment are requested, then they are that week's
     Tuesday 12:00 and Thursday 12:00 local time.
- **Depends:** 0.1
- **Locks:** locations-directory, locations-schema

### 3.2 Admin access

- **Domain:** identity
- **Story:** As an Admin, I want the app to recognise me from the configured
  Admin list, so that I can manage Locations while everyone else cannot.
- **Covers:** BP §4 (Admin role; Admins do not run individual Rounds), Q10,
  Q17, TP §3 (Admin email list)
- **Acceptance criteria:**
  1. Given I am signed in with an email on the Admin list, when I open
     Location administration, then it is shown.
  2. Given I am signed in with an email not on the Admin list, when I open
     Location administration, then access is refused.
  3. Given I am not signed in, when I open Location administration, then I am
     sent to the sign-in page.
  4. Given I am signed in with an email on the Admin list and have not
     completed first sign-in, when I open Location administration, then it
     is shown (bootstrap, OQ-6).
  5. Given I am signed in as an Admin, when I view any page, then no action to
     open, close or match a Round is offered.
- **Depends:** 2.1
- **Locks:** identity-admin

### 3.3 Admin creates a Location

- **Domain:** locations
- **Story:** As an Admin, I want to create a Location with a name and time
  zone, so that Colleagues at that office can take part in Rounds.
- **Covers:** BP §5.4, Q10, Q21, Q26, BP §4 (Admin can create Locations)
- **Acceptance criteria:**
  1. Given I am an Admin, when I submit a name and a time zone chosen from the
     offered list, then the new Location appears in the Location list.
  2. Given I am an Admin, when I create a Location, then its schedule is shown
     as sign-ups open Monday 09:00, close Tuesday 12:00 and Lunch Slot
     Thursday 12:00 in its time zone.
  3. Given I am an Admin, when I submit without a name, then I am told a name
     is required.
  4. Given I am signed in but not an Admin, when I submit the create form,
     then no Location is created.
  5. Given a 360-pixel-wide screen, when I open the Location list and create
     form, then no horizontal scrolling is needed.
- **Depends:** 3.1, 3.2
- **Locks:** locations-admin

### 3.4 Admin edits a Location and its schedule

- **Domain:** locations
- **Story:** As an Admin, I want to change a Location's name, time zone and
  weekly schedule, so that Rounds there fit how that office has lunch.
- **Covers:** BP §5.4 (day/time sign-ups open, day/time sign-ups close = when
  the Match runs, Lunch Slot), R2, Q10, Q21, BP §4 (Admin can edit
  Locations)
- **Acceptance criteria:**
  1. Given I am an Admin, when I change a Location's name, then the new name
     is shown in the Location list.
  2. Given I am an Admin, when I change a Location's time zone, then its
     schedule is shown in the new time zone with the same local days and
     times.
  3. Given I am an Admin, when I set sign-ups open, sign-ups close and Lunch
     Slot to new days and times, then the Location shows the new schedule.
  4. Given I am an Admin, when I set sign-ups close at or before sign-ups
     open in the weekly cycle, then the change is rejected with an
     explanation (OQ-8).
  5. Given I am an Admin, when I set the Lunch Slot at or before sign-ups
     close in the weekly cycle, then the change is rejected with an
     explanation (OQ-8).
  6. Given a Round at the Location is already open, when I save a new
     schedule, then that Round keeps its original close time and Lunch Slot
     (OQ-7).
  7. Given I am signed in but not an Admin, when I submit an edit, then the
     Location is unchanged.
  8. Given a 360-pixel-wide screen, when I open the edit form, then no
     horizontal scrolling is needed.
- **Depends:** 3.3
- **Locks:** locations-admin

---

## Epic 4 — Colleague account

A Colleague can register, keep their home Location and email preference up
to date, and delete themselves.

### 4.1 Register on first sign-in

- **Domain:** identity
- **Story:** As a person signing in for the first time, I want to give my
  name and pick my home Location, so that I become a Colleague who can join
  Rounds there.
- **Covers:** A1, Q3, Q16, BP §5.1 step 3, BP §4 (choose home Location)
- **Acceptance criteria:**
  1. Given I am signed in for the first time, when I submit my name and pick
     a Location, then I am a Colleague with that home Location.
  2. Given I am signed in for the first time, when I submit without a name,
     then I am told a name is required.
  3. Given I am signed in for the first time and no Location exists, when I
     open first sign-in, then I am told no Location is available yet.
  4. Given I already completed first sign-in, when I sign in again, then I go
     straight to the app without the first sign-in step.
  5. Given a Colleague, when another domain asks identity for that
     Colleague's display name and email, then it receives their current name
     and email.
  6. Given Colleagues at several Locations, when another domain asks identity
     for the Colleagues at one Location, then only Colleagues whose home
     Location it is are returned.
  7. Given a 360-pixel-wide screen, when I open first sign-in, then no
     horizontal scrolling is needed.
- **Depends:** 2.1, 3.1
- **Locks:** identity-profile, identity-schema

### 4.2 Change my home Location

- **Domain:** identity
- **Story:** As a Colleague, I want to change my home Location, so that I
  take part in Rounds at the office I now work from.
- **Covers:** A2, BP §4 (change home Location)
- **Acceptance criteria:**
  1. Given I am a Colleague, when I pick a different Location in my account
     settings and save, then my home Location is the new Location.
  2. Given I change my home Location, when the change is saved, then a
     "home Location changed" domain event is published with my Colleague
     reference and the old and new Locations.
  3. Given a 360-pixel-wide screen, when I open my account settings, then no
     horizontal scrolling is needed.
- **Depends:** 4.1
- **Locks:** identity-home-location

### 4.3 Turn the "sign-ups are open" email off and on

- **Domain:** identity
- **Story:** As a Colleague, I want to turn off the "sign-ups are open"
  email, so that I am not reminded each week when I don't want to be.
- **Covers:** BP §4 (turn off the "sign-ups are open" email), BP §7 ("Can be
  turned off" column), Q15
- **Acceptance criteria:**
  1. Given I am a new Colleague, when I open my email settings, then the
     "sign-ups are open" email is shown as on.
  2. Given the email is on, when I turn it off and save, then my settings show
     it as off.
  3. Given the email is off, when I turn it on and save, then my settings show
     it as on.
  4. Given I open my email settings, when the page is shown, then no setting
     is offered for the other emails.
  5. Given Colleagues at a Location, when another domain asks identity for the
     Colleagues there who want the "sign-ups are open" email, then Colleagues
     who turned it off are not returned.
- **Depends:** 4.1
- **Locks:** identity-preferences, identity-schema

### 4.4 Delete myself

- **Domain:** identity
- **Story:** As a Colleague, I want to delete myself, so that my name, email
  and sign-ins are removed while other people's history still makes sense.
- **Covers:** A4, Q23, BP §4 (delete themselves)
- **Acceptance criteria:**
  1. Given I am a Colleague, when I delete myself, then my name and email are
     no longer stored.
  2. Given I deleted myself, when one of my earlier sign-in links is opened,
     then it does not sign anyone in.
  3. Given I deleted myself, when I next open any Colleague page in the same
     browser, then I am signed out.
  4. Given a deleted Colleague, when another domain asks identity for their
     display name, then it receives "a former colleague".
  5. Given I delete myself, when the deletion completes, then a "Colleague
     deleted" domain event is published with my Colleague reference.
  6. Given a 360-pixel-wide screen, when I open the delete action, then no
     horizontal scrolling is needed.
- **Depends:** 4.1
- **Locks:** identity-deletion, identity-schema

---

## Epic 5 — Lunch Groups

Colleagues who signed up are put into small random Lunch Groups with a Host,
avoiding recent repeats, and can see their group and history.

### 5.1 Form Lunch Groups with a Host

- **Domain:** matching
- **Story:** As a Colleague who signed up for a Round, I want to be put at
  random into a small Lunch Group with one Host, so that I meet a few people
  I may not know and someone starts the conversation.
- **Covers:** M1, M2, M4, Q4, Q11, Q13, BP §5.2 "Tuesday 12:00" (Match runs),
  TP §4 (group membership for repeat-pairing analysis)
- **Acceptance criteria:**
  1. Given a Round's Sign-ups for any number of Colleagues from 3 upwards,
     when the Match runs, then every signed-up Colleague is in exactly one
     Lunch Group.
  2. Given 3, 4 or 6 or more Sign-ups, when the Match runs, then every Lunch
     Group has 3 or 4 members (OQ-10).
  3. Given exactly 5 Sign-ups, when the Match runs, then one Lunch Group of 5
     is formed.
  4. Given fewer than 3 Sign-ups, when the Match is asked to run, then no
     Lunch Group is formed.
  5. Given the same Sign-ups and the same injected random source, when the
     Match runs twice, then it forms the same Lunch Groups both times.
  6. Given the same Sign-ups and two different injected random sources, when
     the Match runs, then it forms different Lunch Groups.
  7. Given a Lunch Group is formed, when its Host is chosen, then exactly one
     member is Host.
  8. Given an injected random source that selects a particular member, when a
     Lunch Group's Host is chosen, then that member is Host.
  9. Given a Match for a Round, when it completes, then each Lunch Group keeps
     the Round's Location, its time zone and Lunch Slot.
  10. Given a Match runs, when each Lunch Group is formed, then a
      "Lunch Group formed" process event is recorded for the Round's case
      with the Location, the Lunch Group and its members' Colleague
      references.
- **Depends:** 0.1, 1.1
- **Locks:** matching-groups, matching-schema

### 5.2 Avoid recent repeat Lunch Groups

- **Domain:** matching
- **Story:** As a Colleague, I want the Match to avoid putting me with people
  I had lunch with in the last four Rounds, so that I keep meeting new
  people.
- **Covers:** M3, Q8, BP §9 (no repeat pairing measure), TP §4 (repeat
  pairings across the previous four Rounds)
- **Acceptance criteria:**
  1. Given Sign-ups for which a grouping without repeats exists, when the
     Match runs, then no two members of any Lunch Group shared a Lunch Group
     in the last 4 Rounds at that Location (OQ-9).
  2. Given two Colleagues who shared a Lunch Group 5 or more Rounds ago at the
     Location and not since, when the Match runs, then they are not kept
     apart on that account.
  3. Given two Colleagues who shared a Lunch Group at a different Location,
     when the Match runs at this Location, then that earlier group is not
     counted as a repeat.
  4. Given Sign-ups for which every grouping repeats at least one pair, when
     the Match runs, then it forms a grouping with the fewest repeated pairs
     possible (OQ-11).
  5. Given Sign-ups for which every grouping repeats at least one pair, when
     the Match runs, then every signed-up Colleague is still in a Lunch Group.
  6. Given a Match runs, when each Lunch Group is formed, then its
      "Lunch Group formed" process event carries the number of repeated
      pairs in that group.
- **Depends:** 5.1
- **Locks:** matching-groups

### 5.3 Email each member their Lunch Group

- **Domain:** matching
- **Story:** As a member of a new Lunch Group, I want an email with who is in
  my group, who the Host is and when we have lunch, so that we can arrange
  where to eat by email or chat.
- **Covers:** BP §7 "Your Lunch Group", Q14, Q9, R2, BP §5.2 "Tuesday 12:00"
  (each member is emailed) and "Tuesday → Thursday" (group coordinates
  outside the app)
- **Acceptance criteria:**
  1. Given a Match formed Lunch Groups, when it completes, then each member
     receives one "Your Lunch Group" email.
  2. Given a member's "Your Lunch Group" email, when it is read, then it lists
     the name and email of every member of their Lunch Group.
  3. Given a member's "Your Lunch Group" email, when it is read, then it names
     the Host.
  4. Given a member's "Your Lunch Group" email, when it is read, then it gives
     the Lunch Slot day and time in the Location's time zone.
  5. Given two Lunch Groups in one Round, when the emails are sent, then no
     email names a member of the other group.
  6. Given a member who turned the "sign-ups are open" email off, when the
     Match completes, then they still receive "Your Lunch Group".
  7. Given the emails for a Lunch Group are sent, when sending completes, then
     a "Lunch Group emailed" process event is recorded for the Round's case.
- **Depends:** 5.1, 4.1
- **Locks:** matching-notify

### 5.4 See my Lunch Group

- **Domain:** matching
- **Story:** As a Colleague in a Lunch Group, I want to see my group in the
  app, so that I can find my lunch companions and the Lunch Slot again.
- **Covers:** BP §4 (see their Lunch Group), M4 (Host gives no extra
  rights), Q14, R2
- **Acceptance criteria:**
  1. Given I am in a Lunch Group whose Lunch Slot has not started, when I open
     My Lunch Group, then I see every member's name and email.
  2. Given I am in a Lunch Group, when I open My Lunch Group, then the Host is
     marked.
  3. Given I am in a Lunch Group, when I open My Lunch Group, then the Lunch
     Slot is shown in the Location's time zone.
  4. Given I am not in a Lunch Group whose Lunch Slot has not started, when I
     open My Lunch Group, then I am told I have no upcoming Lunch Group.
  5. Given I am the Host, when I open My Lunch Group, then I am offered the
     same actions as every other member.
  6. Given a 360-pixel-wide screen, when I open My Lunch Group, then no
     horizontal scrolling is needed.
- **Depends:** 5.1, 4.1
- **Locks:** matching-my-group

### 5.5 See my own Lunch Group history

- **Domain:** matching
- **Story:** As a Colleague, I want to see the Lunch Groups I was in, so that
  I can remember who I've had lunch with.
- **Covers:** A3, A4 (former colleague in other people's history), Q23, BP
  §4 (see their own history)
- **Acceptance criteria:**
  1. Given I was in Lunch Groups in past Rounds, when I open My history, then
     each of those Lunch Groups is listed with its Lunch Slot date and
     members.
  2. Given other Colleagues' Lunch Groups that I was not in, when I open My
     history, then none of them is listed.
  3. Given a member of one of my past Lunch Groups deleted themselves, when I
     open My history, then they appear as "a former colleague".
  4. Given I have never been in a Lunch Group, when I open My history, then I
     am told there is no history yet.
  5. Given a 360-pixel-wide screen, when I open My history, then no horizontal
     scrolling is needed.
- **Depends:** 5.1, 4.4
- **Locks:** matching-history

---

## Epic 6 — Weekly Rounds

Each Location runs a Round every week on its own, from opening sign-ups to
the Lunch Slot, with no one operating it.

### 6.1 Open a Round on schedule

- **Domain:** rounds
- **Story:** As a Colleague, I want a Round to open at my Location every week
  without anyone starting it, so that I can always join this week's lunch.
- **Covers:** R1, R2, Q6, Q10, Q24, BP §3 goal "No one has to run it", BP
  §5.2 "Monday 09:00" (Round opens), TP §4 (Round case starts)
- **Acceptance criteria:**
  1. Given a Location with the default schedule, when the clock reaches Monday
     09:00 in its time zone, then a Round is open at that Location.
  2. Given a Round is open at a Location, when the Round is read, then its
     sign-ups-close time and Lunch Slot are that week's moments from the
     Location's schedule.
  3. Given a Round already opened at a Location this week, when the opening
     job runs again for the same week, then no second Round is opened.
  4. Given two Locations in different time zones, when the clock reaches
     Monday 09:00 in one of them, then only that Location's Round opens.
  5. Given a Round opens, when it is opened, then a "Round opened" process
     event is recorded with the Round as case and the Location as attribute.
- **Depends:** 3.1, 1.1
- **Locks:** rounds-lifecycle, rounds-schema

### 6.2 Email "sign-ups are open"

- **Domain:** rounds
- **Story:** As a Colleague, I want an email when sign-ups open at my
  Location, so that I can opt in with one click.
- **Covers:** BP §7 "Sign-ups are open", BP §5.2 "Monday 09:00" (email), Q15,
  R2, BP §3 goal "one click to opt in, everything else arrives by email"
- **Acceptance criteria:**
  1. Given Colleagues whose home Location is the Round's Location and who
     have the email on, when the Round opens, then each receives one
     "Sign-ups are open" email.
  2. Given a Colleague at the Location who turned the email off, when the
     Round opens, then they receive no "Sign-ups are open" email.
  3. Given a Colleague whose home Location is another Location, when the
     Round opens, then they receive no "Sign-ups are open" email for it.
  4. Given a "Sign-ups are open" email, when it is read, then it states the
     sign-ups-close time in the Location's time zone.
  5. Given a "Sign-ups are open" email, when its link is followed by a
     signed-in Colleague, then the sign-up page for that Round is shown.
  6. Given the emails for a Round are sent, when sending completes, then a
     "Sign-ups-open email sent" process event is recorded for the Round's
     case.
- **Depends:** 6.1, 4.3
- **Locks:** rounds-open-email

### 6.3 Sign up for this week's Round

- **Domain:** rounds
- **Story:** As a Colleague, I want to sign up for the open Round at my home
  Location in one click, so that I'm included in this week's Match.
- **Covers:** R2, R3, R4, Q5, BP §5.2 "Monday 09:00 → Tuesday 12:00"
  (Colleagues sign up), BP §3 goal (one click to opt in), TP §4 (elapsed
  time from sign-ups opening to a Sign-up)
- **Acceptance criteria:**
  1. Given a Round is open at my home Location and I have not signed up, when
     I choose to sign up, then I have a Sign-up for that Round.
  2. Given I have a Sign-up for the open Round, when I open the Round page,
     then it shows that I am signed up.
  3. Given a Round is open, when I open the Round page, then the
     sign-ups-close time and Lunch Slot are shown in the Location's time
     zone.
  4. Given a Round open at a Location that is not my home Location, when I try
     to sign up for it, then no Sign-up is made.
  5. Given I already have a Sign-up for the open Round, when I sign up again,
     then I still have exactly one Sign-up for it.
  6. Given the Round's sign-ups have closed, when I try to sign up, then no
     Sign-up is made.
  7. Given I had a Sign-up for last week's Round, when this week's Round
     opens, then I have no Sign-up for this week's Round.
  8. Given no Round is open at my home Location, when I open the Round page,
     then I am told when sign-ups next open in my Location's time zone.
  9. Given I sign up, when the Sign-up is made, then a "Sign-up made" process
     event is recorded for the Round's case with my Colleague reference.
  10. Given a 360-pixel-wide screen, when I open the Round page, then no
      horizontal scrolling is needed.
- **Depends:** 6.1, 4.1
- **Locks:** rounds-signup, rounds-schema

### 6.4 Remove my Sign-up before sign-ups close

- **Domain:** rounds
- **Story:** As a Colleague, I want to remove my Sign-up before sign-ups
  close without anyone being told, so that I only go when I really want to.
- **Covers:** Q20, BP §5.2 "Monday 09:00 → Tuesday 12:00" (removing a
  Sign-up; nobody is notified), BP §3 goal (a Sign-up only when someone
  actually wants to go)
- **Acceptance criteria:**
  1. Given I have a Sign-up for an open Round, when I remove it, then I no
     longer have a Sign-up for that Round.
  2. Given I remove my Sign-up, when the removal completes, then no email is
     sent to anyone.
  3. Given the Round's sign-ups have closed, when I try to remove my Sign-up,
     then my Sign-up remains.
  4. Given I removed my Sign-up while the Round is open, when I sign up again,
     then I have a Sign-up for that Round.
  5. Given I remove my Sign-up, when the removal completes, then a
     "Sign-up removed" process event is recorded for the Round's case with my
     Colleague reference.
- **Depends:** 6.3
- **Locks:** rounds-signup

### 6.5 Close sign-ups and start the Match or cancel the Round

- **Domain:** rounds
- **Story:** As a Colleague who signed up, I want sign-ups to close on
  schedule and either a Match to run or the Round to be cancelled, so that I
  know whether lunch is on.
- **Covers:** M1, M2 (Cancelled Round), R2, Q6, Q11, BP §5.2 "Tuesday 12:00"
  (sign-ups close and the Match runs), BP §7 "Round cancelled", BP §3 goal
  (no one has to run it)
- **Acceptance criteria:**
  1. Given an open Round with the default schedule, when the clock reaches
     Tuesday 12:00 in the Location's time zone, then the Round accepts no more
     Sign-ups.
  2. Given 3 or more Sign-ups at close, when sign-ups close, then the Match
     runs with exactly that Round's Sign-ups.
  3. Given fewer than 3 Sign-ups at close, when sign-ups close, then the Round
     becomes a Cancelled Round.
  4. Given a Cancelled Round, when it is cancelled, then no Match runs for it.
  5. Given a Cancelled Round, when it is cancelled, then each Colleague who
     signed up receives one "Round cancelled" email.
  6. Given a Round with no Sign-ups at close, when it becomes a Cancelled
     Round, then no email is sent.
  7. Given sign-ups close, when they close, then a "Sign-ups closed" process
     event is recorded for the Round's case with the number of Sign-ups.
  8. Given a Round becomes a Cancelled Round, when it is cancelled, then a
     "Round cancelled" process event is recorded for the Round's case.
- **Depends:** 6.3, 5.1
- **Locks:** rounds-lifecycle, rounds-schema

### 6.6 Drop my Sign-up when I change home Location

- **Domain:** rounds
- **Story:** As a Colleague who moves office, I want my Sign-up at my old
  Location removed while my existing Lunch Group stays, so that I am never
  matched at an office I no longer work from.
- **Covers:** A2, R4
- **Acceptance criteria:**
  1. Given I have a Sign-up for a Round at my old Location whose sign-ups
     have not closed, when I change my home Location, then that Sign-up is
     removed.
  2. Given I am in a Lunch Group from an already matched Round at my old
     Location, when I change my home Location, then My Lunch Group still
     shows that group.
  3. Given a Round is open at my new home Location, when I have changed my
     home Location, then I can sign up for it.
  4. Given my Sign-up is dropped by a Location change, when it is dropped,
     then a "Sign-up dropped" process event is recorded for the Round's case
     with my Colleague reference.
- **Depends:** 6.3, 4.2, 5.4
- **Locks:** rounds-signup-move

### 6.7 Drop a deleted Colleague's Sign-up

- **Domain:** rounds
- **Story:** As a Colleague who deletes themselves, I want any open Sign-up
  of mine removed, so that I am never matched after I left (OQ-13).
- **Covers:** A4
- **Acceptance criteria:**
  1. Given a Colleague has a Sign-up for a Round whose sign-ups have not
     closed, when they delete themselves, then that Sign-up is removed.
  2. Given a deleted Colleague's Sign-up is dropped, when it is dropped, then
     a "Sign-up dropped" process event is recorded for the Round's case.
- **Depends:** 6.3, 4.4
- **Locks:** rounds-signup-delete

### 6.8 Reach the Lunch Slot

- **Domain:** rounds
- **Story:** As an operator, I want each matched Round to record when its
  Lunch Slot is reached, so that the process event log shows the whole Round
  from opening to lunch.
- **Covers:** BP §5.2 "Thursday 12:00" (lunch), TP §4 (every step of every
  Round), glossary Round
- **Acceptance criteria:**
  1. Given a matched Round with the default schedule, when the clock reaches
     Thursday 12:00 in the Location's time zone, then the Round is shown as
     complete.
  2. Given a matched Round reaches its Lunch Slot, when it is reached, then a
     "Lunch Slot reached" process event is recorded for the Round's case.
  3. Given a Cancelled Round, when its week's Lunch Slot time passes, then no
     "Lunch Slot reached" event is recorded.
- **Depends:** 6.5
- **Locks:** rounds-lifecycle, rounds-schema

---

## Epic 7 — Withdrawal

A Colleague can leave their Lunch Group before the Lunch Slot, and the group
adapts without anyone stepping in.

### 7.1 Withdraw from my Lunch Group

- **Domain:** matching
- **Story:** As a Colleague in a Lunch Group, I want to withdraw before the
  Lunch Slot and have the others told, so that they aren't left waiting for
  me.
- **Covers:** W1, Q12, Q19, BP §5.3, BP §7 "Someone withdrew", TP §4
  (Withdrawal rates by Location)
- **Acceptance criteria:**
  1. Given I am in a Lunch Group whose Lunch Slot has not started, when I
     withdraw on My Lunch Group, then I am no longer a member of it.
  2. Given I withdraw, when the Withdrawal completes, then each remaining
     member receives one "Someone withdrew" email.
  3. Given I withdraw, when the Withdrawal completes, then no Colleague is
     added to the Lunch Group.
  4. Given the Lunch Slot has started, when I try to withdraw, then I remain a
     member.
  5. Given I withdrew, when a remaining member opens My Lunch Group, then I am
     not listed.
  6. Given I withdraw, when the Withdrawal completes, then a "Withdrawal"
     process event is recorded for the Round's case with the Location, the
     Lunch Group and my Colleague reference.
- **Depends:** 5.4
- **Locks:** matching-withdrawal, matching-schema

### 7.2 Re-pick the Host when the Host withdraws

- **Domain:** matching
- **Story:** As a remaining member of a Lunch Group, I want a new Host picked
  when the Host withdraws, so that someone still starts the conversation.
- **Covers:** W2, Q19, BP §5.3, BP §7 "Someone withdrew" (and the new Host,
  if re-picked)
- **Acceptance criteria:**
  1. Given the Host withdraws and two or more members remain, when the
     Withdrawal completes, then exactly one remaining member is Host.
  2. Given an injected random source that selects a particular remaining
     member, when the Host withdraws, then that member becomes Host.
  3. Given a new Host is picked, when the "Someone withdrew" emails are sent,
     then the new Host's email tells them they are now the Host.
  4. Given a member who is not the Host withdraws, when the Withdrawal
     completes, then the Host is unchanged.
  5. Given the Host withdraws and only one member remains, when the
     Withdrawal completes, then no new Host is picked.
  6. Given a new Host is picked, when it is picked, then a "Host re-picked"
     process event is recorded for the Round's case.
- **Depends:** 7.1
- **Locks:** matching-host-repick

### 7.3 Dissolve a Lunch Group left with one Colleague

- **Domain:** matching
- **Story:** As the last remaining member of a Lunch Group, I want to be
  told lunch is off, so that I don't go to a lunch nobody else is coming to.
- **Covers:** W3, Q19, BP §5.3, BP §7 "Lunch is off"
- **Acceptance criteria:**
  1. Given a Lunch Group with two members, when one withdraws, then the Lunch
     Group is dissolved.
  2. Given a Lunch Group is dissolved, when it is dissolved, then the last
     remaining member receives one "Lunch is off" email.
  3. Given a Lunch Group is dissolved, when it is dissolved, then the last
     remaining member receives no "Someone withdrew" email (OQ-12).
  4. Given my Lunch Group was dissolved, when I open My Lunch Group, then I am
     told I have no upcoming Lunch Group.
  5. Given a Lunch Group is dissolved, when it is dissolved, then a
     "Lunch Group dissolved" process event is recorded for the Round's case.
- **Depends:** 7.1
- **Locks:** matching-dissolve, matching-schema

### 7.4 Withdraw a deleted Colleague from their upcoming Lunch Group

- **Domain:** matching
- **Story:** As a member of a Lunch Group, I want a Colleague who deletes
  themselves before the Lunch Slot to be withdrawn, so that the group knows
  who is still coming (OQ-13).
- **Covers:** A4, W1, W2, W3
- **Acceptance criteria:**
  1. Given a Colleague in a Lunch Group whose Lunch Slot has not started,
     when they delete themselves, then they are no longer a member of it.
  2. Given a deleted Colleague is withdrawn, when the Withdrawal completes,
     then each remaining member receives a "Someone withdrew" email naming
     "a former colleague".
  3. Given the deleted Colleague was Host and two or more members remain,
     when they are withdrawn, then a new Host is picked.
  4. Given the deleted Colleague's Withdrawal leaves one member, when it
     completes, then the Lunch Group is dissolved.
  5. Given a deleted Colleague in a Lunch Group whose Lunch Slot has passed,
     when they delete themselves, then that Lunch Group's membership is
     unchanged.
- **Depends:** 7.1, 7.2, 7.3, 4.4
- **Locks:** matching-deletion

---

## Epic 8 — Success measures

An operator can calculate the proposed success measures and drop-off
analyses from the process event log.

### 8.1 Calculate success measures from the process event log

- **Domain:** process-log
- **Story:** As an operator, I want the proposed success measures and the
  drop-off analyses calculated from the process event log for a Location and
  period, so that we can see whether Lunch Roulette works (OQ-14, OQ-15).
- **Covers:** BP §9 (all four measures), TP §4 (elapsed time from sign-ups
  opening to a Sign-up; Withdrawal rates by Location; repeat pairings across
  the previous four Rounds)
- **Acceptance criteria:**
  1. Given a Location with 20 Colleagues of whom 5 made a Sign-up in a
     calendar month, when the measures are calculated for that month, then
     the monthly sign-up share is 25% (OQ-16).
  2. Given 10 Rounds at a Location in a period of which 2 were Cancelled
     Rounds, when the measures are calculated, then the share of Rounds that
     are not Cancelled Rounds is 80%.
  3. Given 4 Lunch Groups at a Location in a period with 2 Withdrawals in
     total, when the measures are calculated, then the Withdrawal rate per
     Lunch Group is 0.5 (OQ-15).
  4. Given 5 Lunch Groups at a Location in a period of which 4 have no
     repeated pair, when the measures are calculated, then the share of Lunch
     Groups with no repeat pairing is 80%.
  5. Given a Round opened at 09:00 and a Sign-up made at 10:30 Location time,
     when the analyses are calculated, then that Sign-up's elapsed time from
     sign-ups opening is 90 minutes.
  6. Given Withdrawals at two Locations, when the analyses are calculated,
     then a Withdrawal rate is reported separately for each Location.
  7. Given a Round whose Lunch Groups contain 3 repeated pairs from the
     previous four Rounds at its Location, when the analyses are calculated,
     then that Round reports 3 repeat pairings.
  8. Given process events for a Location, when the measures are calculated,
     then the result is the same whether or not any Colleague has since
     deleted themselves.
- **Depends:** 1.1, 4.1, 5.2, 6.3, 6.5, 7.1
- **Locks:** process-log-measures

---

## Wave table

A story joins the earliest wave after all its dependencies; when two
otherwise-ready stories share a lock, the later one in backlog order moves to
the next wave. Story 4.4 is the only one moved: it shares `identity-schema`
with 4.3 in wave 3.

| Wave | Stories | Locks held in this wave (each appears once) |
|---|---|---|
| 0 | 0.1 | dependencies, migrations, compose, repo-profile |
| 1 | 1.1, 2.1, 3.1 | process-log-events, process-log-schema · identity-signin, identity-schema · locations-directory, locations-schema |
| 2 | 3.2, 4.1, 5.1, 6.1 | identity-admin · identity-profile, identity-schema · matching-groups, matching-schema · rounds-lifecycle, rounds-schema |
| 3 | 3.3, 4.2, 4.3, 5.2, 5.3, 5.4, 6.3 | locations-admin · identity-home-location · identity-preferences, identity-schema · matching-groups · matching-notify · matching-my-group · rounds-signup, rounds-schema |
| 4 | 3.4, 4.4, 6.2, 6.4, 6.5, 6.6, 7.1 | locations-admin · identity-deletion, identity-schema · rounds-open-email · rounds-signup · rounds-lifecycle, rounds-schema · rounds-signup-move · matching-withdrawal, matching-schema |
| 5 | 5.5, 6.7, 6.8, 7.2, 7.3, 8.1 | matching-history · rounds-signup-delete · rounds-lifecycle, rounds-schema · matching-host-repick · matching-dissolve, matching-schema · process-log-measures |
| 6 | 7.4 | matching-deletion |

Dependency graph (every arrow points from a lower ID to a higher one, so it
has no cycle):

| Story | Depends | Wave |
|---|---|---|
| 0.1 | none | 0 |
| 1.1 | 0.1 | 1 |
| 2.1 | 0.1 | 1 |
| 3.1 | 0.1 | 1 |
| 3.2 | 2.1 | 2 |
| 3.3 | 3.1, 3.2 | 3 |
| 3.4 | 3.3 | 4 |
| 4.1 | 2.1, 3.1 | 2 |
| 4.2 | 4.1 | 3 |
| 4.3 | 4.1 | 3 |
| 4.4 | 4.1 | 4 (moved from 3 for `identity-schema`) |
| 5.1 | 0.1, 1.1 | 2 |
| 5.2 | 5.1 | 3 |
| 5.3 | 5.1, 4.1 | 3 |
| 5.4 | 5.1, 4.1 | 3 |
| 5.5 | 5.1, 4.4 | 5 |
| 6.1 | 3.1, 1.1 | 2 |
| 6.2 | 6.1, 4.3 | 4 |
| 6.3 | 6.1, 4.1 | 3 |
| 6.4 | 6.3 | 4 |
| 6.5 | 6.3, 5.1 | 4 |
| 6.6 | 6.3, 4.2, 5.4 | 4 |
| 6.7 | 6.3, 4.4 | 5 |
| 6.8 | 6.5 | 5 |
| 7.1 | 5.4 | 4 |
| 7.2 | 7.1 | 5 |
| 7.3 | 7.1 | 5 |
| 7.4 | 7.1, 7.2, 7.3, 4.4 | 6 |
| 8.1 | 1.1, 4.1, 5.2, 6.3, 6.5, 7.1 | 5 |

---

## Coverage table

Every business rule, user journey step, notification, role ability and
technical requirement in the sources maps to at least one story.

### Business rules (BP §6)

| Rule | Stories |
|---|---|
| R1 One Round per week per Location, automatically | 6.1 |
| R2 Times set and shown in the Location's time zone | 3.1, 3.4, 5.3, 5.4, 6.1, 6.2, 6.3, 6.5 |
| R3 A Sign-up is for one Round only | 6.3 |
| R4 Only Colleagues at the Round's Location can sign up | 6.3, 6.6 |
| M1 Match runs at close using only that Round's Sign-ups | 5.1, 6.5 |
| M2 Groups of 3 or 4; five → one group of 5; under three → Cancelled Round | 5.1, 6.5 |
| M3 Random, avoiding last-4-Rounds repeats; fewest repeats, nobody left out | 5.1, 5.2 |
| M4 One random Host per Lunch Group, no extra rights | 5.1, 5.4 |
| W1 Withdraw until the Lunch Slot; no replacement | 7.1, 7.4 |
| W2 Host withdraws → new random Host | 7.2, 7.4 |
| W3 One Colleague left → dissolved and notified | 7.3, 7.4 |
| A1 Self-registration at an allowed domain; no invite or import | 2.1, 4.1 |
| A2 Change home Location; unmatched Sign-up removed; Lunch Groups unaffected | 4.2, 6.6 |
| A3 Own past Lunch Groups only | 5.5 |
| A4 Self-deletion; "a former colleague" in others' history | 4.4, 5.5, 6.7, 7.4, 1.1, 8.1 |

### User journeys (BP §5)

| Journey step | Stories |
|---|---|
| §5.1 step 1 Enter work email | 2.1 |
| §5.1 step 2 Allowed domains only; one-time link emailed | 2.1 |
| §5.1 step 3 Give name and home Location on first sign-in | 4.1 |
| §5.2 Monday 09:00 Round opens; "sign-ups are open" email | 6.1, 6.2 |
| §5.2 Monday 09:00 → Tuesday 12:00 Sign up; remove silently until close | 6.3, 6.4 |
| §5.2 Tuesday 12:00 Sign-ups close; Match runs; each member emailed | 6.5, 5.1, 5.2, 5.3 |
| §5.2 Tuesday → Thursday Host suggests a place; group coordinates outside the app | 5.3, 5.4 |
| §5.2 Thursday 12:00 Lunch (Lunch Slot) | 6.8, 7.1 (Withdrawal closes) |
| §5.3 Withdrawing after the Match (notify, no replacement, Host re-pick, dissolve) | 7.1, 7.2, 7.3 |
| §5.4 Admin creates a Location with default schedule and changes it | 3.1, 3.3, 3.4 |

### Roles (BP §4)

| Ability | Stories |
|---|---|
| Colleague: sign in | 2.1 |
| Colleague: choose home Location | 4.1 |
| Colleague: change home Location | 4.2, 6.6 |
| Colleague: sign up for Rounds | 6.3 |
| Colleague: withdraw from Rounds (Sign-up before close, Lunch Group after Match) | 6.4, 7.1 |
| Colleague: see their Lunch Group | 5.4 |
| Colleague: see their own history | 5.5 |
| Colleague: turn off the "sign-ups are open" email | 4.3, 6.2 |
| Colleague: delete themselves | 4.4 |
| Admin: configured email list, also a Colleague | 3.2 |
| Admin: create and edit Locations (name, time zone, weekly schedule) | 3.3, 3.4 |
| Admin: does not run individual Rounds | 3.2 |

### Notifications (BP §7)

| Email | Stories |
|---|---|
| Sign-in link (cannot be turned off) | 2.1 |
| Sign-ups are open (can be turned off) | 6.2, 4.3 |
| Your Lunch Group (cannot be turned off) | 5.3 |
| Round cancelled (cannot be turned off) | 6.5 |
| Someone withdrew, to remaining members and the new Host if re-picked (cannot be turned off) | 7.1, 7.2, 7.4 |
| Lunch is off (cannot be turned off) | 7.3 |

### Goals, look and feel, success measures (BP §3, §8, §9)

| Requirement | Stories |
|---|---|
| §3 One click to opt in, everything else by email | 6.2, 6.3, 5.3 |
| §3 Small groups, named Host, fixed time, Sign-up only when wanted | 5.1, 5.3, 6.4 |
| §3 No one has to run it | 6.1, 6.5, 6.8 |
| §3 Non-goals (multi-tenant, cross-Location, availability matching, restaurants, chat, Slack/Teams/mobile, skip switch, replacement) | none by design; 3.2 AC5 and 7.1 AC3 assert two of them |
| §8 Material Design 3, light and dark themes following the device, one brand colour | 0.1 |
| §8 Usable on a phone | 0.1, 2.1, 3.3, 3.4, 4.1, 4.2, 4.4, 5.4, 5.5, 6.3 |
| §9 Share of Colleagues signing up at least once a month | 6.3, 8.1 |
| §9 Share of Rounds that are not Cancelled Rounds | 6.5, 8.1 |
| §9 Withdrawal rate per Lunch Group | 7.1, 8.1 |
| §9 Share of Lunch Groups with no repeat pairing from the last 4 Rounds | 5.2, 8.1 |

### Decisions (BP §10, TP §6)

| Decision | Stories |
|---|---|
| Q1 Built in this repository by the software factory | all (0.1 sets up the build) |
| Q2 Web app first | 0.1 |
| Q3 One organisation; matched only within home Location | 4.1, 5.2, 6.3 |
| Q4 Lunch Groups of 3–4 | 5.1 |
| Q5 Opt in to each Round | 6.3 |
| Q6 Recurring weekly Rounds with a batch Match | 6.1, 6.5 |
| Q7 Sign-in by emailed link, company domains only | 2.1 |
| Q8 Random, avoiding repeats from the last 4 Rounds | 5.2 |
| Q9 Fixed Lunch Slot per Location; the group picks the place | 3.1, 5.3 |
| Q10 Automatic Rounds; Admins manage Locations and schedules | 3.2, 3.3, 3.4, 6.1 |
| Q11 Five → one group of 5; under three → Cancelled Round | 5.1, 6.5 |
| Q12 Withdrawal allowed, no replacement | 7.1 |
| Q13 Random Host per Lunch Group | 5.1 |
| Q14 Group sees names, emails, Host; no in-app chat | 5.3, 5.4 |
| Q15 Three notification moments; "sign-ups open" can be turned off | 4.3, 6.2, 5.3 |
| Q16 Self-registration on first sign-in | 2.1, 4.1 |
| Q17 Admins are a configured email list | 3.2 |
| Q18 Material Design 3 look | 0.1 |
| Q19 Host re-pick; dissolve at one; withdraw until the Lunch Slot | 7.1, 7.2, 7.3 |
| Q20 Sign-ups can be removed silently before close | 6.4 |
| Q21 Each Location has its own time zone | 3.1, 3.3, 3.4 |
| Q22 Python/FastAPI, one process; PostgreSQL in Docker | 0.1 |
| Q23 Own history only; self-deletion anonymises | 4.4, 5.5 |
| Q24 No holiday skip | 6.1 |
| Q25 Name: Lunch Roulette | 0.1 |
| Q26 Default schedule Mon 09:00 / Tue 12:00 / Thu 12:00 | 3.1, 3.3 |
| Q27 One Docker container; hosting chosen at deployment | 0.1 |
| Q28 Configuration from environment variables; console email in development | 0.1 |

### Technical requirements (TP §2–§5)

| Requirement | Stories |
|---|---|
| §2 Python and FastAPI, one application process | 0.1 |
| §2 PostgreSQL, available in Docker | 0.1 |
| §2 Delivered as one Docker container | 0.1 |
| §2 Hosting platform chosen at deployment time | 0.1 (AC4: runs from environment variables alone) |
| §3 Deployment configuration through environment variables | 0.1 |
| §3 Allowed company domains | 0.1, 2.1 |
| §3 Admin email list | 0.1, 3.2 |
| §3 Brand seed colour | 0.1 |
| §3 Email delivery settings | 0.1 |
| §3 Console email in development | 0.1 |
| §4 Every step of every Round recorded as an event with case, activity, timestamp | 1.1, 5.1, 5.2, 5.3, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 7.1, 7.2, 7.3 |
| §4 Enough information for the BP §9 measures | 8.1 |
| §4 Elapsed time from sign-ups opening to a Sign-up | 6.1, 6.3, 8.1 |
| §4 Withdrawal rates by Location | 7.1, 8.1 |
| §4 Repeat pairings across the previous four Rounds at a Location | 5.1, 5.2, 8.1 |
| §4 Structure suitable for process mining and future Celonis use | 1.1 |
| §5 Interface uses `design/material_design_3/`; seed colour gives light and dark schemes | 0.1 |

---

## Open questions

Each entry names the gap, contradiction or ambiguity, the default this
backlog assumes so stories stay buildable, and the stories that change if the
answer differs.

| # | Question | Default assumed here | Affected stories |
|---|---|---|---|
| OQ-1 | `api-endpoint-design.md` relies on PRD content the technical PRD does not contain: a read-only `/api/v1/extract/...` JSON extraction API with its own bearer token and a "gap-free transaction cursor", "tombstone rules", an email outbox, and a signed session with CSRF protection. Are these requirements, and if so which source owns them? | Not in scope; no story builds an extraction API. Session handling and email sending follow the rule files through each spec. | 0.1, 1.1, 2.1, 8.1 |
| OQ-2 | Production email delivery is only "email delivery settings" (TP §3). Which provider or protocol (for example SMTP) is used outside development? | 0.1 provides console delivery plus one configurable real transport chosen in its spec. | 0.1, 2.1, 5.3, 6.2, 6.5, 7.1, 7.2, 7.3 |
| OQ-3 | Emailed links need the app's public base URL, and signed sessions need a secret; TP §3 lists neither. | Both are added as required environment variables in 0.1. | 0.1, 2.1, 6.2 |
| OQ-4 | The sources say the sign-in link is "one-time" but give no lifetime, session length, sign-out, rate limit, or rule for letter case and subdomains in allowed domains. | Short-lived single-use link; domain match is exact and case-insensitive; session length and sign-out are decided in 2.1's spec. | 2.1 |
| OQ-5 | Is an Admin email required to be on an allowed company domain? | Yes; Admins sign in like everyone else. | 0.1, 3.2 |
| OQ-6 | Bootstrapping: first sign-in needs a Location, but only Admins create Locations and an Admin is defined as a Colleague. How does the first Admin get in? | An Admin-list email reaches Location administration before completing first sign-in (3.2 AC4). | 3.2, 4.1 |
| OQ-7 | When does an edited schedule or time zone take effect if a Round is already open? What happens when a new Location is created after its sign-ups-open time in the current week? | Edits apply from the next Round not yet opened; a new Location's first Round opens at its next scheduled sign-ups-open moment. | 3.4, 6.1, 6.5, 6.8 |
| OQ-8 | Which schedules are valid? Must open → close → Lunch Slot fall in that order within one week, and is there a minimum gap? | Order open < close < Lunch Slot inside one weekly cycle, no minimum gap. | 3.4 |
| OQ-9 | What counts as "shared a Lunch Group in the last 4 Rounds" (M3)? Do Cancelled Rounds count as Rounds; do groups someone withdrew from, or dissolved groups, count as shared? | The last 4 Rounds at the Location that had a Match; every formed Lunch Group counts, including members who later withdrew. | 5.2, 8.1 |
| OQ-10 | For counts that split several ways into 3s and 4s (for example 12 = 4+4+4 or 3+3+3+3), which split is preferred? | Any split with only 3s and 4s; the spec picks one rule. | 5.1 |
| OQ-11 | "Repeats are kept as few as possible" (M3): fewest repeated pairs, or fewest Colleagues with a repeat? | Fewest repeated pairs. | 5.2, 8.1 |
| OQ-12 | When a Withdrawal dissolves a group, does the last member get "Someone withdrew" as well as "Lunch is off"? | Only "Lunch is off". | 7.1, 7.3 |
| OQ-13 | A4 does not say what happens to an open Sign-up or an upcoming Lunch Group when a Colleague deletes themselves, or whether the same email can register again afterwards. | Open Sign-ups are dropped; upcoming Lunch Groups treat it as a Withdrawal; the same email may register again as a new Colleague. | 4.4, 6.7, 7.4 |
| OQ-14 | Who reads the success measures, and through what interface (page, export, command)? No operator role exists in BP §4. | 8.1 delivers a calculation operation with no user interface; a follow-up story adds the surface once decided. | 8.1 |
| OQ-15 | BP §9 marks the measures as "proposed" and not agreed. Is "Withdrawal rate per Lunch Group" Withdrawals per Lunch Group or the share of groups with at least one Withdrawal? | Measures are built as proposed; the rate is Withdrawals divided by Lunch Groups. | 8.1 |
| OQ-16 | "Share of Colleagues at a Location who sign up at least once a month" needs how many Colleagues were at the Location, which is not a Round step and is not in the event log. Where does the denominator come from, and is it the count at month end or over the month? | identity's current count of Colleagues at the Location at calculation time. | 4.1, 8.1 |
| OQ-17 | What is the process-mining case: the Round, the Sign-up, or the Colleague's participation? TP §4 only requires "a case". | The Round is the case; Colleague, Lunch Group and Location are event attributes. | 1.1, 5.1, 5.2, 5.3, 6.1–6.8, 7.1–7.3, 8.1 |
| OQ-18 | A4 removes a deleted Colleague's name, email and sign-ins. May the process event log keep a pseudonymous Colleague reference after deletion? | Yes; the log holds only opaque references, never names or emails. | 1.1, 8.1 |
| OQ-19 | Can Locations be deleted or renamed in a way that affects past history? BP §4 lists only create and edit. | No deletion; a rename shows the new name everywhere. | 3.4, 5.5 |
| OQ-20 | Which order and how far back does "own history" go, and does it include Cancelled Rounds or groups the Colleague withdrew from? | Formed Lunch Groups the Colleague was still in at the Lunch Slot, newest first, all time. | 5.5 |
| OQ-21 | `docs/solution/domain-map.md` does not yet meet its own objective (`domain-map-objective.md`): it has no Responsibility column, no interactions table, no Open questions, and no link to the rule it implements. Story domains here rest only on its domain table, which is complete. | The domain table is used as is. If a completed map moves a concept to another domain, the stories that own that concept change domain and locks. | all |
| OQ-22 | Domain dependencies risk a cycle that the missing interactions table in `domain-map.md` must settle: `identity` needs the Location list for first sign-in (4.1 → 3.1) while `locations` needs identity's Admin check (3.3, 3.4 → 3.2). `rounds` and `matching` react to identity changes. | Cross-domain reactions use domain events (4.2 and 4.4 publish; 6.6, 6.7 and 7.4 consume). `locations` reaches the Admin check through identity's control, and identity gets the Location list through an operation that the entry point wires in. If the map instead settles the cycle by changing direction, the dependencies of 3.3, 3.4 and 4.1 change. | 3.2, 3.3, 3.4, 4.1, 6.6, 6.7, 7.4 |
| OQ-23 | Health and readiness: the deployment target is unknown (TP §2), so is one health check enough? | One unversioned health check that also checks the database. | 0.1 |
