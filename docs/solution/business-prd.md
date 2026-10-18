# Lunch Roulette — Business PRD

**Status:** agreed in design interview, 2026-10-17
**Companion documents:** [technical-prd.md](technical-prd.md) · [GLOSSARY.md](GLOSSARY.md)

Capitalised terms (Colleague, Location, Round, Sign-up, Match, Lunch Group,
Host, Lunch Slot, Cancelled Round, Withdrawal, Admin) are defined in the
glossary and mean exactly that here.

## 1. Problem

Colleagues mostly have lunch with the people they already work with. People in
other teams stay strangers, new joiners take a long time to build a network, and
setting up a lunch with someone you don't know feels awkward enough that nobody
does it.

## 2. Product in one paragraph

Lunch Roulette is a web app for one organisation. Each week, Colleagues at an
office (Location) can opt in to that week's Round. When sign-ups close, the
Match puts them at random into small Lunch Groups of 3–4 people, avoiding people
they've recently eaten with, and makes one member the Host. Every group has
lunch at the Location's fixed Lunch Slot (e.g. Thursday 12:00) and picks the
place itself. The app handles the opt-in, the matching and the emails; the
conversation happens in people's normal email or chat.

## 3. Goals and non-goals

### Goals

- Colleagues meet people outside their usual circle with almost no effort: one
  click to opt in, everything else arrives by email.
- Lunches actually happen: small groups, a named Host, a fixed time, and a
  sign-up that is only made when someone actually wants to go.
- No one has to run it: Rounds open, match and close on a schedule.

### Non-goals (v1)

- Several organisations (multi-tenant).
- Matching across Locations, or remote/virtual lunches.
- Matching on availability, departments, interests or seniority.
- Choosing, suggesting or booking restaurants.
- In-app chat or messaging.
- Slack/Teams integration or mobile apps.
- An Admin "skip this week" switch (a quiet week simply becomes a Cancelled Round).
- Replacing a Colleague who withdraws.

## 4. Users and roles

| Role | Who | Can |
|---|---|---|
| **Colleague** | Anyone with an email address at an allowed company domain | Sign in, choose and change their home Location, sign up for and withdraw from Rounds, see their Lunch Group and their own history, turn off the "sign-ups are open" email, delete themselves |
| **Admin** | Colleagues whose email is on the configured Admin list | Everything a Colleague can, plus create and edit Locations (name, time zone, weekly schedule). Admins do not run individual Rounds. |

## 5. User journeys

### 5.1 First visit

1. A Colleague opens the app and enters their work email.
2. Only allowed company domains are accepted; the app emails a one-time sign-in link.
3. On first sign-in they give their name and pick their home Location. They now exist as a Colleague.

### 5.2 A normal week at a Location (default schedule)

| When (Location time) | What happens |
|---|---|
| Monday 09:00 | The Round opens. Colleagues at the Location who haven't opted out get a "sign-ups are open" email. |
| Monday 09:00 → Tuesday 12:00 | Colleagues sign up. Removing a Sign-up is possible until close; nobody is notified. |
| Tuesday 12:00 | Sign-ups close and the Match runs. Each member gets an email with their Lunch Group, names, emails, the Host and the Lunch Slot. |
| Tuesday → Thursday | The Host suggests a place; the group coordinates by email/chat outside the app. |
| Thursday 12:00 | Lunch (the Lunch Slot). |

### 5.3 Withdrawing after the Match

A Colleague can withdraw from their Lunch Group until the Lunch Slot starts.
The rest of the group is emailed. Nobody replaces them. If the Host withdraws,
a new Host is picked at random from those remaining. If only one Colleague is
left, the Lunch Group is dissolved and they're told lunch is off.

### 5.4 Admin sets up a Location

An Admin creates a Location with a name and time zone. It starts with the
default schedule (above), which the Admin can change: day/time sign-ups open,
day/time sign-ups close (= when the Match runs) and the Lunch Slot.

## 6. Business rules

### Rounds

- R1. Every Location runs one Round per week, automatically, on its schedule.
- R2. All times are set and shown in the Location's own time zone.
- R3. A Sign-up is for one Round only; it never carries over.
- R4. Only Colleagues whose home Location is the Round's Location can sign up.

### Matching

- M1. The Match runs when sign-ups close and uses only that Round's Sign-ups.
- M2. Group sizes: 3 or 4. Exactly five Sign-ups make one group of 5. Fewer than three Sign-ups make a **Cancelled Round**: no groups, and those who signed up are emailed.
- M3. The Match is random, but avoids putting Colleagues together who shared a Lunch Group in the last 4 Rounds at that Location. When that's impossible, repeats are kept as few as possible rather than leaving anyone out.
- M4. Each Lunch Group gets one Host, chosen at random. The Host is a nudge to suggest the place and start the conversation; it gives no extra rights.

### After the Match

- W1. A Colleague may withdraw until the Lunch Slot starts. No replacement.
- W2. Host withdraws → new Host picked at random from those remaining.
- W3. One Colleague left → the Lunch Group is dissolved and that Colleague is notified.

### Accounts and data

- A1. Anyone with an email at an allowed domain can register themselves; there is no invite or import.
- A2. A Colleague can change their home Location. Doing so removes any Sign-up they have for a Round that hasn't been matched yet; Lunch Groups they're already in are unaffected.
- A3. A Colleague sees only their own past Lunch Groups. Everyone's history is used only by the Match to avoid repeats.
- A4. A Colleague can delete themselves: their name, email and sign-ins are removed, and they appear as "a former colleague" in other people's history.

## 7. Notifications (email)

| Email | To | When | Can be turned off |
|---|---|---|---|
| Sign-in link | The person signing in | On request | No |
| Sign-ups are open | Colleagues at the Location | Round opens | Yes |
| Your Lunch Group | Each group member | Match ran | No |
| Round cancelled | Colleagues who signed up | Match found fewer than 3 | No |
| Someone withdrew | Remaining members (and the new Host, if re-picked) | Withdrawal | No |
| Lunch is off | The last remaining member | Group dissolved | No |

## 8. Look and feel

Material Design 3, with light and dark themes that follow the device and a
single brand colour. Usable on a phone, since people often open the emails
there.

## 9. Success measures (proposed)

These weren't discussed in the interview; they're a starting point to agree on.
How the product captures and reports the required data is defined in the
[technical PRD](technical-prd.md#4-measurement-and-process-data).

- Share of Colleagues at a Location who sign up at least once a month.
- Share of Rounds that are not Cancelled Rounds.
- Withdrawal rate per Lunch Group (lower is better).
- Share of Lunch Groups with no repeat pairing from the last 4 Rounds.

## 10. Business decisions log

All decisions were made in the 2026-10-17 design interview. Original interview
identifiers are retained; Q1, Q22, Q27 and Q28 are technical or delivery
decisions and are recorded in the [technical PRD](technical-prd.md).

| # | Decision |
|---|---|
| Q2 | Web app first |
| Q3 | One organisation; Colleagues matched only within their home Location |
| Q4 | Lunch Groups of 3–4 |
| Q5 | Opt in to each Round |
| Q6 | Recurring weekly Rounds with a batch Match |
| Q7 | Sign-in by emailed link, company domains only |
| Q8 | Random, avoiding repeats from the last 4 Rounds |
| Q9 | Fixed Lunch Slot per Location; the group picks the place |
| Q10 | Automatic Rounds; Admins manage Locations and schedules |
| Q11 | Five → one group of 5; under three → Cancelled Round |
| Q12 | Withdrawal allowed, no replacement |
| Q13 | Random Host per Lunch Group |
| Q14 | Group sees names, emails, Host; no in-app chat |
| Q15 | Three notification moments; "sign-ups open" can be turned off |
| Q16 | Self-registration on first sign-in |
| Q17 | Admins are a configured email list |
| Q18 | Material Design 3 look |
| Q19 | Host re-pick; dissolve at one; withdraw until the Lunch Slot |
| Q20 | Sign-ups can be removed silently before close |
| Q21 | Each Location has its own time zone |
| Q23 | Own history only; self-deletion anonymises |
| Q24 | No holiday skip |
| Q25 | Name: Lunch Roulette |
| Q26 | Default schedule Mon 09:00 / Tue 12:00 / Thu 12:00 |
