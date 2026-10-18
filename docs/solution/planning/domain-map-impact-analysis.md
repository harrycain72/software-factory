# Impact of the domain map on the epics and user stories

**Date:** 2026-10-18
**Compares:** [domain-map.md](../solution/domain-map.md) (rewritten to meet
[domain-map-objective.md](domain-map-objective.md)) against
[epics-and-user-stories.md](epics-and-user-stories.md) (written against the
earlier five-domain stub).

## Verdict

The backlog is impacted. Its "Source check" paragraph says the map lists "the
same five domains with the same owned concepts" and that every story's
domain, its locks, its dependencies and the waves are unchanged. That is no
longer true. In detail:

- 7 of the 29 stories change domain: 5 by the rename from `identity` to
  `colleagues` (2.1, 4.1–4.4), and 2 by a move (1.1 to `platform`, 3.2 to
  `locations`). Story 8.1 loses its domain.
- 4 stories need different dependencies.
- 1 new story is needed, and 1 story may be removed.
- Every `identity-*` and `process-log-*` lock is renamed.
- Two conflicts between the map and the backlog need a human decision
  before the backlog is regenerated (D1, D2).

Behaviour is almost entirely unaffected. Nearly every acceptance criterion
stays valid, and the coverage of business rules, journeys, notifications and
decisions does not shrink, except for the BP §9 measure calculation if D2
removes story 8.1.

## Decisions needed first

| # | Conflict | Option A | Option B | Recommendation |
|---|---|---|---|---|
| D1 | **Self-deletion.** The backlog (OQ-13; stories 4.4 AC5, 6.7 and 7.4) drops a deleted Colleague's open Sign-up and withdraws them from an upcoming Lunch Group through a "Colleague deleted" domain event. The map (its open question 3) assumes both are left as they are, and its interactions table has no "Colleague deleted" rows. | Keep the backlog behaviour. Add two rows to the map: `rounds` → `colleagues` and `matching` → `colleagues` through the "Colleague deleted" event. Neither row creates a cycle. | Follow the map: remove 4.4 AC5, 6.7 and 7.4. | **A.** A deleted Colleague would otherwise still be matched, and their group would wait for them. The map change is two rows. |
| D2 | **Success measures.** Story 8.1 calculates the BP §9 measures inside the app, in the `process-log` domain. The map has no such domain. Its open question 8 assumes the app only records process events and the measures are calculated outside it (TP §4 requires only "enough information to calculate"). A calculation encodes business definitions, such as what counts as a Withdrawal rate, so it cannot live in `platform`. | Remove 8.1 and Epic 8. Calculation happens in a process-mining tool such as Celonis. OQ-14, OQ-15 and OQ-16 then move out of the backlog. | Keep 8.1 and add a business domain for reporting to the map, owning the measure definitions. It would depend on `colleagues` for the number of Colleagues at a Location (OQ-16). | **A**, unless someone needs to see the measures in the app. BP §9 marks the measures "proposed", and no role in BP §4 reads them (OQ-14). |

The tables below assume A for both. Where B changes the result, that is noted.

## Story-by-story impact

| Story | Today | Under the map | Change | Why |
|---|---|---|---|---|
| 0.1 | platform | platform | **Scope and acceptance criteria** | The map puts three capabilities in `platform` that no story builds today: (1) in-process publishing and subscribing to domain events, which 4.2 and 4.4 publish and 6.6, 6.7 and 7.4 consume; (2) issuing, verifying and revoking sign-in sessions; (3) process-event storage, which already belongs to 1.1. Add (1) and (2) to 0.1's scope, with criteria such as "an event published by one domain reaches every registered consumer". The migration chains become `colleagues`, `locations`, `rounds`, `matching` and `platform`, replacing `identity` and `process-log`. |
| 1.1 | process-log | **platform** | Domain; locks `process-log-events`, `process-log-schema` → `platform-process-events`, `platform-schema` | Rule 7 and the map put process-event recording in `platform`. Two criteria name business concepts that `platform` must not know. AC6 filters "by Location": make it a generic filter on an attribute. AC3 rejects "a name or an email address": make it a rejection of attribute keys outside an allowed list, so no business rule sits in `platform`. |
| 2.1 | identity | **colleagues** | Domain; locks → `colleagues-signin`, `colleagues-schema` | Rename. Sign-in rules stay in `colleagues`. The session itself comes from `platform` (0.1). |
| 3.2 | identity | **locations** | Domain; lock `identity-admin` → `locations-admin-access`; depends `2.1` → `0.1, 3.1` | The map makes `locations` own Admin. It checks the signed-in email from the `platform` session against the Admin list injected at the entry point. The criteria are unchanged. AC4, which lets an Admin in before first sign-in, matches the map's open question 1. The old backlog OQ-22 default (locations calls identity's control for the Admin check) is the cycle the map removes. |
| 3.3, 3.4 | locations | locations | None | They still depend on 3.2, now inside the same domain. |
| 4.1 | identity | **colleagues** | Domain; locks → `colleagues-profile`, `colleagues-schema`. **Add two criteria**: "another domain asks colleagues for a Colleague's home Location and receives it" (the map's R4 row; 6.3 needs it, and no criterion provides it today); and, under D2-A, a "Colleague registered" process event. Under D2-A it also depends on 1.1. | AC5, AC6 and the other criteria say "asks identity"; replace with "asks colleagues". |
| 4.2 | identity | **colleagues** | Domain; lock → `colleagues-home-location`. Under D2-A, add a "home Location changed" process-event criterion. | AC2's domain event matches the map's `rounds` → `colleagues` row exactly. |
| 4.3 | identity | **colleagues** | Domain; locks → `colleagues-preferences`, `colleagues-schema`; AC5 "asks identity" → "asks colleagues" | Rename only. |
| 4.4 | identity | **colleagues** | Domain; locks → `colleagues-deletion`, `colleagues-schema`; AC4 "asks identity" → "asks colleagues". Under D2-A, add a "Colleague deleted" process-event criterion. Under D1-B, remove AC5. | Rename. AC3 (signed out) is `colleagues` revoking sessions through `platform`, as the map describes. |
| 5.1 | matching | matching | None to its own scope. It stays the Match operation over a list of Colleagues, with no dependency on `rounds`. | AC4 (fewer than 3 → no group) stays as the Lunch Group invariant, even though `rounds` never hands over fewer than 3. |
| 5.2–5.5 | matching | matching | None | Dependencies on 4.1 and 4.4 match the map's `matching` → `colleagues` row. 5.2 follows the backlog's OQ-9 default (only matched Rounds count), which matches the map's open question 4. |
| 6.1–6.4 | rounds | rounds | None | Their dependencies on 3.1, 4.1 and 4.3 match the map's `rounds` → `locations` and `rounds` → `colleagues` rows. |
| 6.5 | rounds | rounds | **Dependencies and criteria**: depends `6.3, 5.1` → `6.3`. AC2 "the Match runs with exactly that Round's Sign-ups" becomes "a 'sign-ups closed' domain event is published with the Round, Location, time zone, Lunch Slot time and the signed-up Colleague ids". AC4 becomes "no 'sign-ups closed' event is published". | The backlog has `rounds` call `matching` (6.5 → 5.1). The map reverses this: `matching` consumes the event from `rounds`. Keeping both would make a cycle. |
| **new 6.9** | n/a | matching | **New story: Run the Match when sign-ups close.** Depends on 6.5 and 5.1; lock `matching-match-trigger`. Criteria: the event starts exactly one Match for that Round; a repeated event does not form a second set of groups; the groups carry the Location, time zone and Lunch Slot time from the event. | This replaces the half of 6.5 that moved. It must have an ID above 6.5 so backlog order stays a valid admission order. It can't go in Epic 5 as 5.6, because it would then depend on a story with a higher ID. |
| 6.6 | rounds | rounds | **Dependencies and criteria**: depends `6.3, 4.2, 5.4` → `6.3, 4.2`. Remove AC2 ("My Lunch Group still shows that group"), or move it to 5.4. | AC2 checks a `matching` page from a `rounds` story, which suggests a `rounds` → `matching` dependency. The map forbids that, because `matching` already depends on `rounds`. `matching` never consumes "home Location changed", so the behaviour holds without a test in `rounds`. |
| 6.7 | rounds | rounds | Under D1-A, none. Under D1-B, remove the story. | It consumes the "Colleague deleted" event (D1). |
| 6.8 | rounds | rounds | None | |
| 7.1–7.3 | matching | matching | None | W1's Lunch Slot time arrives in the "sign-ups closed" event, as the map describes. |
| 7.4 | matching | matching | Under D1-A, none. Under D1-B, remove the story. | It consumes the "Colleague deleted" event (D1). |
| 8.1 | process-log | n/a | Under D2-A, remove the story and Epic 8. Under D2-B, assign it to the new reporting domain. | `process-log` no longer exists (D2). |

## Changes to the backlog's front matter, tables and open questions

- **Source check paragraph:** rewrite. The map now has four domains plus
  `platform`, Admin has moved to `locations`, and the interactions table
  exists.
- **How to read, Domain:** the list becomes `colleagues`, `locations`,
  `rounds`, `matching` or `platform`.
- **How to read, Cross-domain hand-offs:** "rounds handing closed Sign-ups
  to the Match" becomes "the Match consuming the sign-ups-closed event from
  rounds" (6.5 → 6.9).
- **Process events:** add the `colleagues` activities the map lists
  (registered, home Location changed, deleted) if D2-A is chosen. With them,
  the log alone can supply OQ-16's denominator to an outside tool.
- **Epics table:** under D2-A, remove Epic 8. Epic 1's capability is
  unchanged.
- **Wave table and dependency graph:** recompute. The proposed result is
  below.
- **Coverage table:** under D2-A, the BP §9 rows and the TP §4 "enough
  information" row point to the process-event criteria (5.2, 6.3, 6.5, 7.1
  and the new `colleagues` events) instead of 8.1. A4 loses 8.1 and gains
  nothing else. M1 adds 6.9.
- **Open questions:**
  - OQ-21 and OQ-22: close them. The map now has responsibilities,
    interactions and open questions, and it settles the cycle by giving
    Admin to `locations`. That is the opposite of OQ-22's default, which
    reached the Admin check through identity.
  - OQ-13: replace it with D1's outcome.
  - OQ-14, OQ-15 and OQ-16: move them out of the backlog under D2-A, since
    they only concern calculating the measures. Under D2-B, keep them and
    change "identity's current count" to "colleagues' current count".
  - OQ-17 (the case is the Round): consistent with the map, which leaves the
    case to the platform log story. The map could adopt this default.
  - OQ-5, OQ-6, OQ-7, OQ-8, OQ-9, OQ-18 and OQ-19: unchanged. Their defaults
    match the map's open questions 1, 4, 6, 7 and 9.
  - New: sessions and domain events are `platform` capabilities that no
    source names (the map's open question 2). They should be recorded as an
    assumption behind the 0.1 scope change.

## Proposed waves (D1-A, D2-A)

The same rule as today: a story joins the earliest wave after its
dependencies, and when two ready stories share a lock, the later one in
backlog order waits a wave.

| Wave | Stories | Locks |
|---|---|---|
| 0 | 0.1 | dependencies, migrations, compose, repo-profile |
| 1 | 1.1, 2.1, 3.1 | platform-process-events, platform-schema · colleagues-signin, colleagues-schema · locations-directory, locations-schema |
| 2 | 3.2, 4.1, 5.1, 6.1 | locations-admin-access · colleagues-profile, colleagues-schema · matching-groups, matching-schema · rounds-lifecycle, rounds-schema |
| 3 | 3.3, 4.2, 4.3, 5.2, 5.3, 5.4, 6.3 | locations-admin · colleagues-home-location · colleagues-preferences, colleagues-schema · matching-groups · matching-notify · matching-my-group · rounds-signup, rounds-schema |
| 4 | 3.4, 4.4, 6.2, 6.4, 6.5, 6.6, 7.1 | locations-admin · colleagues-deletion, colleagues-schema · rounds-open-email · rounds-signup · rounds-lifecycle, rounds-schema · rounds-signup-move · matching-withdrawal, matching-schema |
| 5 | 5.5, 6.7, 6.8, 6.9, 7.2, 7.3 | matching-history · rounds-signup-delete · rounds-lifecycle, rounds-schema · matching-match-trigger · matching-host-repick · matching-dissolve, matching-schema |
| 6 | 7.4 | matching-deletion |

The width and depth stay the same: 7 waves with at most 7 stories each. The
dependency changes don't lengthen the critical path:

- 6.5 no longer waits for 5.1, but 6.3 already holds it in wave 4.
- 6.6 drops its dependency on 5.4 and stays in wave 4.
- 3.2 now depends on 3.1 instead of 2.1, so it stays in wave 2.
- 6.9 is new in wave 5, alongside 7.2 and 7.3.

4.4 is still the only story moved for a lock (`colleagues-schema`, shared
with 4.3). 6.9 assumes it adds no table: groups are keyed by Round, which
makes a repeated event detectable without one. If it needs a table, it takes
`matching-schema` and 7.3 moves to wave 6.

## Unaffected

- Every acceptance criterion in 3.1, 3.3, 3.4, 5.1–5.5, 6.1–6.4, 6.8 and
  7.1–7.3.
- All locks of `locations`, `rounds` and `matching`, except the new
  `locations-admin-access` and `matching-match-trigger`.
- Epic 0's exclusive locks and the rule that only Epic 0 changes
  dependencies, migrations, Compose files and the repository profile.
- Coverage of every business rule (R, M, W, A), journey step, role ability,
  notification and decision. Each keeps at least one story.
