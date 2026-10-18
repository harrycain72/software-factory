# Domain map

The business-domain decomposition of Lunch Roulette. It implements
[bce-architecture.md "Domain map"](../architecture/rules/bce-architecture.md#domain-map)
under rule 1 (partition by business domain), rule 6 (domains interact through
boundary or control only) and rule 7 (platform holds technology, not
business). Concept names come from [GLOSSARY.md](GLOSSARY.md). Sources:
[business-prd.md](business-prd.md) and [technical-prd.md](technical-prd.md).

Every story has exactly one owning domain, or `platform`. Stories in
different domains can be built in parallel once the control operations or
domain events they consume, listed under Interactions, exist.

## Domains

| Domain | Owns these glossary concepts | Responsibility |
|---|---|---|
| `locations` | Location, Lunch Slot, Admin | Keeps each Location's name, time zone and weekly schedule (sign-ups open, sign-ups close, Lunch Slot) and lets only Admins, the configured Admin list, create and change them. |
| `colleagues` | Colleague | Registers Colleagues from allowed company domains through emailed sign-in links and keeps each Colleague's name, email, home Location and email preference until they delete themselves. |
| `rounds` | Round, Sign-up, Cancelled Round | Opens and closes each Location's weekly Round on its schedule, takes and removes Sign-ups while it is open, and cancels it at close when fewer than three Colleagues signed up. |
| `matching` | Match, Lunch Group, Host, Withdrawal | Runs the Match over a closed Round's Sign-ups, forms Lunch Groups with a Host while avoiding recent repeats, and handles Withdrawals until the Lunch Slot. |

Every glossary concept has exactly one owner. No concept is left unowned.

Supporting state that is not a glossary concept belongs to the domain that
owns the concept it describes:

| State | Domain | Why there |
|---|---|---|
| Weekly schedule and time zone | `locations` | Attributes of a Location (business PRD §5.4, R2) |
| Home Location, "sign-ups are open" email preference, sign-in links | `colleagues` | Attributes of a Colleague (business PRD §4, §5.1, A1, A4) |
| Each Round's concrete open, close and Lunch Slot times | `rounds` | Copied from the schedule when the Round opens, so a Round keeps its own times |
| Lunch Group history per Location | `matching` | Read only by the Match (M3) and by a Colleague viewing their own groups (A3) |

## Interactions

Each row is one dependency. The source depends on the target. Data that
crosses the line is a plain copy of identifiers and simple values.

| From | To | Through | Why |
|---|---|---|---|
| `colleagues` | `locations` | control: list Locations / confirm a Location exists | A Colleague picks an existing home Location on first sign-in and when changing it (§5.1, A2) |
| `rounds` | `locations` | control: list Locations with time zone and weekly schedule | Each Location's Round opens and closes on its own schedule, in its own time zone (R1, R2) |
| `rounds` | `colleagues` | control: home Location of a Colleague | Only Colleagues whose home Location is the Round's Location can sign up (R4) |
| `rounds` | `colleagues` | control: Colleagues at a Location who want the "sign-ups are open" email, with contact details | "Sign-ups are open" email when a Round opens (§7) |
| `rounds` | `colleagues` | control: contact details of given Colleagues | "Round cancelled" email to those who signed up (M2, §7) |
| `rounds` | `colleagues` | domain event: home Location changed (Colleague id, old and new Location ids) | A Sign-up for a Round that has not been matched yet is removed (A2) |
| `matching` | `rounds` | domain event: sign-ups closed (Round id, Location id, Location name, time zone, Lunch Slot time, signed-up Colleague ids), published only when at least three signed up | The Match runs at close over only that Round's Sign-ups, and Withdrawals end at the Lunch Slot (M1, M2, W1) |
| `matching` | `colleagues` | control: contact details of given Colleagues (name and email, or "a former colleague" after deletion) | "Your Lunch Group", "Someone withdrew" and "Lunch is off" emails, and a Colleague's own history (§7, A3, A4) |

The dependency order is `locations` ← `colleagues` ← `rounds` ← `matching`.
The table has no cycle. `locations` depends on no domain: it decides Admin
from the authenticated email that `platform` supplies and the Admin list the
entry point injects. Every domain may also depend on `platform`, which
depends on no domain.

## Business rules by domain

| Rule | Domain | Cross-domain interaction |
|---|---|---|
| R1 one Round per week per Location, automatically | `rounds` | `rounds` → `locations` schedule |
| R2 times in the Location's time zone | `locations` (holds it), `rounds`, `matching` (apply it) | `rounds` → `locations`; `matching` gets the time zone in "sign-ups closed" |
| R3 a Sign-up is for one Round only | `rounds` | none |
| R4 only Colleagues at the Round's Location sign up | `rounds` | `rounds` → `colleagues` home Location |
| M1 Match at close over that Round's Sign-ups | `matching` | "sign-ups closed" event from `rounds` |
| M2 fewer than three → Cancelled Round and email | `rounds` | `rounds` → `colleagues` contact details |
| M2 groups of 3 or 4; exactly five → one group of 5 | `matching` | none |
| M3 avoid repeats from the last 4 Rounds | `matching` | none: history is `matching`'s own |
| M4 one random Host per Lunch Group, no extra rights | `matching` | none |
| W1 withdraw until the Lunch Slot, no replacement | `matching` | Lunch Slot time arrives in "sign-ups closed" |
| W2 Host withdraws → new random Host | `matching` | none |
| W3 one Colleague left → dissolve and notify | `matching` | `matching` → `colleagues` contact details |
| A1 self-registration for allowed domains | `colleagues` | none: allowed domains injected by the entry point |
| A2 changing home Location removes an unmatched Sign-up | `colleagues` (change), `rounds` (removal) | "home Location changed" event |
| A3 own past Lunch Groups only | `matching` | `matching` → `colleagues` names |
| A4 self-deletion anonymises | `colleagues` | `matching` → `colleagues` returns "a former colleague" |
| Only Admins manage Locations (§4, Q17) | `locations` | none: Admin list injected by the entry point |
| Default schedule Mon 09:00 / Tue 12:00 / Thu 12:00 (§5.4, Q26) | `locations` | none |
| Sign-up removal before close is silent (§5.2, Q20) | `rounds` | none |
| Every email in §7 | Composed by the domain that triggers it: sign-in link → `colleagues`; sign-ups open, Round cancelled → `rounds`; Your Lunch Group, Someone withdrew, Lunch is off → `matching` | Recipients' contact details from `colleagues`; delivery through `platform` |

## Outside the business domains

| Requirement (source) | Lives in |
|---|---|
| Material Design 3 interface, light and dark themes, usable on a phone (business PRD §8; technical PRD §5) | Pages and templates in each domain's boundary; shared theme assets built from `design/material_design_3/` in `platform` |
| Brand seed colour for the light and dark schemes (technical PRD §3, §5) | Read by the entry point, applied by the `platform` theme |
| Python and FastAPI in one application process (technical PRD §2) | Entry point: creates the app and mounts each domain's routes, scheduled triggers and event handlers |
| Configuration through environment variables: allowed company domains, Admin list, brand seed colour, email delivery settings (technical PRD §3) | Loaded by `platform` configuration and read only at the entry point, which passes allowed domains to `colleagues`, the Admin list to `locations`, and the rest to `platform` (rule 8) |
| PostgreSQL in Docker (technical PRD §2) | `platform`: connections and migration running; each domain owns its own tables and migrations (rule 6) |
| Email transport and console email in development (technical PRD §3) | `platform` email transport; the entry point chooses the console or the provider; wording stays in each domain's control (rule 7) |
| Scheduling of Round opening and closing (business PRD §3 "no one has to run it") | `platform` runs a timer; the triggers are in the `rounds` boundary, which decides which Round to open or close |
| Domain event delivery between domains (rule 6) | `platform` provides in-process publish and subscribe; the entry point registers each consumer's handlers |
| Sign-in sessions: issuing, verifying and revoking a session for an authenticated email (business PRD §5.1) | `platform` mechanism; `colleagues` decides who may sign in and starts and revokes sessions; every boundary reads the signed-in identity from `platform` |
| Process event log: case, activity and timestamp for every step of every Round, suitable for process mining and Celonis (technical PRD §4; business PRD §9) | `platform` stores and records events; each domain's control reports its own activities (`colleagues`: registered, home Location changed, deleted; `rounds`: opened, signed up, Sign-up removed, closed, cancelled; `matching`: matched, Withdrawal, Host re-picked, dissolved) |
| One Docker container; hosting chosen at deployment (technical PRD §2) | Deployment files at the repository root, outside product code |

`platform` owns no glossary concept and no business rule. The activity names
recorded in the process event log, and the wording of every email, are owned
by the domain that reports them.

## Open questions

| # | Gap, contradiction or ambiguity | Domains affected | Assumption in this map |
|---|---|---|---|
| 1 | The glossary calls an Admin "a Colleague", and Q17 makes Admins a configured email list. The sources don't say whether an Admin must also have registered as a Colleague, or whether Admin decisions belong with the Colleague record. | `locations`, `colleagues` | `locations` owns Admin and checks the signed-in email against the injected list. An Admin need not have completed first sign-in as a Colleague. Moving Admin to `colleagues` would create a `locations` ↔ `colleagues` cycle. |
| 2 | No source says where sign-in sessions live. Rule 7 doesn't list sessions as a `platform` capability. | all | Session mechanics are in `platform`, and sign-in rules are in `colleagues`. |
| 3 | A4 doesn't say what self-deletion does to an open Sign-up or to a Lunch Group whose Lunch Slot hasn't passed. | `colleagues`, `rounds`, `matching` | They stay; deleted members show as "a former colleague". If they should be removed, add a "Colleague deleted" event that `rounds` and `matching` consume. Those rows would not create a cycle. |
| 4 | M3's "last 4 Rounds at that Location" doesn't say whether Cancelled Rounds count. | `rounds`, `matching` | Only matched Rounds count, so `matching` needs no event for Cancelled Rounds. If they count, `matching` must also consume a "Round cancelled" event from `rounds`. |
| 5 | A2 says a Sign-up for a Round "that hasn't been matched yet" is removed. The sources don't define the moment between close and the Match. | `colleagues`, `rounds` | `rounds` treats sign-ups close as the cut-off. After close, the Colleague is either in a Lunch Group (unaffected) or the Round is cancelled. |
| 6 | §5.4 lets an Admin change a schedule. The sources don't say whether a change affects a Round that is already open, or what order the open, close and Lunch Slot times must follow. | `locations`, `rounds` | A Round copies its times when it opens, so a change applies from the next Round. `locations` requires open < close < Lunch Slot within the week. |
| 7 | The sources don't say whether a Location can be deleted or archived. `colleagues` and `rounds` hold Location ids. | `locations`, `colleagues`, `rounds` | Locations are never deleted. Removing one would need a new event and a rule for its Colleagues. |
| 8 | Technical PRD §4 requires data that can calculate the business PRD §9 measures, but doesn't say whether the app shows them. It also doesn't define the event case (Round, Lunch Group or Colleague). | all, `platform` | The app only records the data, and the measures are calculated outside it. The case is decided per activity with the platform log story. If the app must show the measures, a reporting domain must be added to own them. |
| 9 | A4 removes a deleted Colleague's name, email and sign-ins. The sources don't say whether process events may keep that Colleague's identifier. | `colleagues`, `platform` | Process events hold only opaque Colleague ids, never names or emails, and they keep the id. |
