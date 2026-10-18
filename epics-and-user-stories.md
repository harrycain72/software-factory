# Lunch Roulette — Epics and User Stories

**Status:** Ready for backlog refinement

**Derived from:** `docs/prd/business-prd.md` (agreed 2026-10-17)

**Prepared:** 2026-10-18

## 1. Purpose and conventions

This document turns the Lunch Roulette business requirements into a v1 product
backlog. It does not add features beyond the Business PRD. Capitalised domain
terms have the meanings defined by the product glossary.

Acceptance criteria use Given/When/Then where it improves clarity. Unless a
criterion explicitly says otherwise, displayed and scheduled times use the
relevant Location's time zone. The Business PRD remains authoritative if this
backlog and the source requirements differ.

## Epic 1 — Secure access and colleague onboarding

**Outcome:** A person from the organisation can sign in without a password and
create their Colleague profile on first use.

### US-1.1 — Request a one-time sign-in link

As a prospective Colleague, I want to request a sign-in link with my work email
so that I can access Lunch Roulette without a password or invitation.

**Acceptance criteria**

1. Given an email whose domain is in the configured allowed-domain list, when
   the person requests access, then the system sends a one-time sign-in link to
   that email address.
2. Given an email outside the allowed-domain list, when access is requested,
   then the system does not issue a usable sign-in link or register a
   Colleague.
3. A sign-in link can be used only once.
4. Requesting a sign-in link does not require an invitation or a pre-imported
   account.
5. The sign-in-link email cannot be disabled by a user preference.

### US-1.2 — Complete first-time onboarding

As a first-time user, I want to provide my name and choose my home Location so
that I become a Colleague who can join local Rounds.

**Acceptance criteria**

1. Given a person who successfully uses a sign-in link for the first time, when
   onboarding is shown, then both a name and an existing home Location are
   required.
2. When the person submits valid onboarding details, then a Colleague profile
   is created with the verified email, entered name and chosen home Location.
3. The Colleague is signed in after onboarding completes.
4. A returning Colleague is not asked to repeat first-time onboarding.

### US-1.3 — Recognise configured Admins

As an organisation operator, I want Admin rights to follow a configured email
list so that administration does not require a separate account type.

**Acceptance criteria**

1. Given a signed-in Colleague whose verified email is on the configured Admin
   list, then they can use all Admin functions as well as Colleague functions.
2. Given a signed-in Colleague whose email is not on the configured Admin list,
   then Admin functions are not available or executable by that Colleague.
3. Admin status does not grant any role in running an individual Round or
   choosing its Match.

## Epic 2 — Locations and weekly schedules

**Outcome:** Admins can maintain the offices and local schedules that drive
automatic Rounds.

### US-2.1 — Create a Location

As an Admin, I want to create a Location so that Colleagues at that office can
participate in weekly Rounds.

**Acceptance criteria**

1. An Admin can create a Location with a name and valid time zone.
2. A new Location receives the default weekly schedule: sign-ups open Monday
   at 09:00, sign-ups close Tuesday at 12:00, and the Lunch Slot is Thursday at
   12:00.
3. The schedule is stored and displayed in the Location's time zone.
4. A non-Admin cannot create a Location.

### US-2.2 — Edit a Location and its schedule

As an Admin, I want to edit a Location's details and weekly schedule so that
the Round runs at appropriate local times.

**Acceptance criteria**

1. An Admin can edit the Location name and time zone.
2. An Admin can edit the day and time when sign-ups open, the day and time when
   sign-ups close and the day and time of the Lunch Slot.
3. The configured close time is the time at which the Match runs.
4. The schedule must preserve the order: sign-ups open before sign-ups close,
   and sign-ups close before the Lunch Slot.
5. A non-Admin cannot edit a Location or its schedule.

### US-2.3 — Change home Location

As a Colleague, I want to change my home Location so that future participation
reflects the office where I now have lunch.

**Acceptance criteria**

1. A Colleague can choose any existing Location as their new home Location.
2. When the Location changes, any Sign-up by that Colleague for a Round that
   has not yet been matched is removed.
3. Lunch Groups produced by an already completed Match are unchanged by the
   Location change.
4. After the change, the Colleague can sign up only for a Round at the new home
   Location.

## Epic 3 — Automatic weekly Round lifecycle

**Outcome:** Each Location runs its weekly Round without a person operating it.

### US-3.1 — Create and open a weekly Round automatically

As a Colleague, I want my Location's Round to open on schedule so that joining
Lunch Roulette requires no organiser.

**Acceptance criteria**

1. The system creates one Round per Location per week.
2. At the Location's configured opening day and time, the Round becomes open
   for Sign-ups automatically.
3. The opening occurs according to the Location's time zone, including local
   daylight-saving-time changes.
4. Each Round has its own Sign-ups; no Sign-up is copied from a prior Round.
5. There is no Admin control to skip an individual week.

### US-3.2 — Close sign-ups and start the Match automatically

As a signed-up Colleague, I want the Round to close and match on schedule so
that I know when participation is settled.

**Acceptance criteria**

1. At the configured close day and time, the Round stops accepting new
   Sign-ups and removal of pre-Match Sign-ups.
2. The Match starts automatically when sign-ups close.
3. The Match uses only Sign-ups belonging to that Round.
4. The Round cannot be matched more than once.

### US-3.3 — Allow a quiet week to cancel naturally

As an Admin, I want a low-participation week to become a Cancelled Round so
that I do not have to manage a skip switch.

**Acceptance criteria**

1. A weekly Round still opens and closes when participation is low or zero.
2. If fewer than three Colleagues signed up, the Match creates no Lunch Groups
   and marks the Round cancelled.
3. The system does not require or expose an Admin "skip this week" action.

## Epic 4 — Round sign-up

**Outcome:** An eligible Colleague can opt in or change their mind with minimal
effort before sign-ups close.

### US-4.1 — Sign up for the current Round

As a Colleague, I want to opt in with one clear action so that joining this
week's lunch takes almost no effort.

**Acceptance criteria**

1. Given an open Round at the Colleague's home Location, the Colleague can
   create one Sign-up for that Round.
2. A Colleague cannot sign up for a Round at another Location.
3. A Colleague cannot create duplicate Sign-ups for the same Round.
4. A Sign-up applies only to the selected weekly Round and never carries over.
5. Given a Round that is not open, the Colleague cannot create a Sign-up for
   it.

### US-4.2 — Remove a Sign-up before close

As a signed-up Colleague, I want to remove my Sign-up before the deadline so
that I can change my mind without disrupting a formed group.

**Acceptance criteria**

1. Given a Sign-up in a Round that is still open, the Colleague can remove it.
2. Removing the Sign-up sends no notification to other Colleagues or Admins.
3. The removed Colleague is not included when that Round's Match runs.
4. Once sign-ups close, this action is no longer available; the post-Match
   withdrawal rules apply after a Lunch Group is formed.

## Epic 5 — Fair matching and Host assignment

**Outcome:** Every viable Round produces small, locally matched groups while
minimising recent repeat pairings.

### US-5.1 — Form valid Lunch Group sizes

As a signed-up Colleague, I want to be placed in a small group so that the
lunch is easy to coordinate and supports conversation.

**Acceptance criteria**

1. With fewer than three Sign-ups, the Round is cancelled and no Lunch Group
   is created.
2. With exactly five Sign-ups, the Match creates one Lunch Group of five.
3. For every other viable Sign-up count, all signed-up Colleagues are assigned
   exactly once to Lunch Groups of three or four.
4. A Lunch Group contains only Colleagues whose home Location was the Round's
   Location when they signed up.
5. Nobody is left out merely to avoid a recent repeat pairing.

### US-5.2 — Minimise recent repeat pairings

As a signed-up Colleague, I want the Match to favour people I have not recently
met so that Lunch Roulette expands my network.

**Acceptance criteria**

1. For each possible pair, the Match considers whether they shared a Lunch
   Group in any of the previous four Rounds at that Location.
2. When a valid grouping with no such repeat pairing exists, the Match chooses
   a grouping with no repeat pairing.
3. When avoiding every repeat is impossible, the chosen valid grouping has the
   fewest achievable repeat pairings; no Colleague is excluded to improve the
   score.
4. History from other Locations or from Rounds earlier than the previous four
   at the Location does not count toward this rule.
5. Among groupings with the same best repeat-pairing score, selection is random
   rather than based on name, email, sign-up order, department, interests,
   seniority or availability.

### US-5.3 — Assign one random Host per group

As a Lunch Group member, I want one member named as Host so that someone is
nudged to suggest a place and start the conversation.

**Acceptance criteria**

1. Every newly formed Lunch Group has exactly one Host selected at random from
   its members.
2. Host selection is not based on name, email, sign-up order or Admin status.
3. The Host receives no extra product permissions.
4. The product describes the Host role as suggesting a place and initiating
   coordination, not as booking or choosing a restaurant for the group.

### US-5.4 — Notify Colleagues when a Round is cancelled

As a signed-up Colleague, I want to know when there are too few participants so
that I do not expect a lunch that week.

**Acceptance criteria**

1. When a Match finds fewer than three Sign-ups, every Colleague who signed up
   receives a Round-cancelled email.
2. The email is sent once for that cancelled Round.
3. The Round-cancelled email cannot be disabled by a user preference.

## Epic 6 — Lunch Group details and personal history

**Outcome:** Members know who they will meet and can review only their own past
groups.

### US-6.1 — Receive Lunch Group details

As a matched Colleague, I want the group details by email so that I can
coordinate in the tools I already use.

**Acceptance criteria**

1. After a successful Match, each group member receives one "Your Lunch Group"
   email.
2. The email identifies every current member by name and email address,
   identifies the Host, and gives the Lunch Slot in the Location's time zone.
3. The email does not suggest or book a restaurant and does not start an in-app
   chat.
4. The email cannot be disabled by a user preference.

### US-6.2 — View the current Lunch Group

As a group member, I want to see my current Lunch Group in the app so that I
can recover the details after the email.

**Acceptance criteria**

1. A matched Colleague can view the member names and emails, current Host and
   Lunch Slot for their own current Lunch Group.
2. A Colleague cannot view a Lunch Group of which they are not a member merely
   by navigating to its address or identifier.
3. The displayed details reflect any withdrawal, Host replacement or group
   dissolution.

### US-6.3 — View personal Lunch Group history

As a Colleague, I want to see my own past Lunch Groups so that I can remember
whom I met.

**Acceptance criteria**

1. A Colleague can view past Lunch Groups in which they were a member.
2. A Colleague cannot browse another Colleague's history or groups in which
   they did not participate.
3. The Match may use all Colleagues' relevant group history internally even
   though that history is not generally visible.

## Epic 7 — Post-Match withdrawal

**Outcome:** A Colleague can leave a formed group before lunch, while the
remaining members receive accurate information and no replacement is added.

### US-7.1 — Withdraw before the Lunch Slot

As a matched Colleague, I want to withdraw before lunch starts so that my group
knows I can no longer attend.

**Acceptance criteria**

1. Given the Lunch Slot has not started, a current member can withdraw from
   their Lunch Group.
2. Given the Lunch Slot has started, withdrawal is no longer permitted.
3. A withdrawn Colleague is removed from the current group membership.
4. No replacement is selected or added after a withdrawal.
5. When the group continues with at least two members, every remaining member
   receives a "Someone withdrew" email identifying the updated group state.
6. The withdrawal email cannot be disabled by a user preference.

### US-7.2 — Replace a withdrawing Host

As a remaining group member, I want a new Host selected when the Host withdraws
so that responsibility for starting the conversation remains clear.

**Acceptance criteria**

1. If the Host withdraws and at least two members remain, exactly one remaining
   member is selected at random as the new Host.
2. The updated group details identify the new Host.
3. The withdrawal email to remaining members identifies the new Host.
4. If a non-Host withdraws, the existing Host remains unchanged.

### US-7.3 — Dissolve a group that falls to one member

As the last remaining member, I want to be told that lunch is off so that I do
not expect the group to proceed.

**Acceptance criteria**

1. When a withdrawal leaves exactly one member, the Lunch Group is marked
   dissolved.
2. No replacement Host is selected for a dissolved group.
3. The last remaining member receives a "Lunch is off" email.
4. The email cannot be disabled by a user preference.

## Epic 8 — Notification preferences

**Outcome:** Colleagues receive the operational emails they need while being
able to opt out of the weekly invitation.

### US-8.1 — Receive the Round-open invitation

As a Colleague, I want an email when sign-ups open so that I remember to opt in
for the week.

**Acceptance criteria**

1. When a Round opens, each Colleague whose home Location is that Round's
   Location and who has not disabled the invitation receives one "Sign-ups are
   open" email.
2. The invitation is sent at the configured opening time in the Location's
   time zone.
3. Colleagues at other Locations do not receive that Round's invitation.

### US-8.2 — Turn the Round-open invitation off or on

As a Colleague, I want to control the weekly invitation so that I can reduce
optional email without losing service messages.

**Acceptance criteria**

1. A Colleague can turn the "Sign-ups are open" email off and later turn it
   back on.
2. Turning it off suppresses future Round-open invitations for that Colleague.
3. The preference does not prevent the Colleague from signing up.
4. The preference does not suppress sign-in links, group details, cancellation,
   withdrawal or lunch-off emails.

## Epic 9 — Account deletion and privacy

**Outcome:** A Colleague can remove their identifying account data without
corrupting other people's historical records.

### US-9.1 — Delete my Colleague account

As a Colleague, I want to delete myself so that the system no longer retains my
name, email or sign-in identity.

**Acceptance criteria**

1. A signed-in Colleague can initiate deletion of their own account.
2. On confirmed deletion, the Colleague's name, email and sign-in records are
   removed.
3. The deleted person can no longer sign in as the deleted Colleague.
4. Historical group membership needed by other Colleagues' histories remains,
   but the deleted person is displayed as "a former colleague".
5. Another ordinary Colleague cannot delete this account.

### US-9.2 — Preserve privacy after deletion

As a former colleague, I want my identity removed from history so that past
participation does not expose my personal details.

**Acceptance criteria**

1. No past Lunch Group view exposes the deleted person's former name or email.
2. Match history can retain an anonymous participant reference only to the
   extent needed to preserve historical group records.
3. Other members' histories remain readable and show "a former colleague" in
   place of the deleted identity.

## Epic 10 — Responsive Material Design experience

**Outcome:** The essential journey is clear and usable on phones and follows
the agreed visual system.

### US-10.1 — Use Lunch Roulette on a phone

As a Colleague opening an email on my phone, I want the linked app journey to
fit a small screen so that I can act without switching devices.

**Acceptance criteria**

1. Sign-in, onboarding, Location selection, Sign-up, Sign-up removal, current
   group viewing, withdrawal, notification preference and account deletion are
   usable at common mobile viewport widths without horizontal page scrolling.
2. Primary actions and essential content remain visible and operable in both
   portrait and landscape orientation.
3. Email links open the relevant responsive app destination.

### US-10.2 — Apply the agreed visual theme

As a Colleague, I want a consistent visual experience so that the product is
recognisable and comfortable to use.

**Acceptance criteria**

1. The interface uses Material Design 3 components and conventions from the
   repository's design source.
2. The interface follows the device's light or dark theme.
3. Both themes use the single brand seed colour configured at deployment.
4. Content and actions remain legible and distinguishable in both themes.

## Epic 11 — Process measurement and deployment readiness

**Outcome:** The organisation can deploy the agreed v1 and measure whether the
Lunch Roulette process is working.

### US-11.1 — Record Round process events

As a product owner, I want each Round step recorded as a process event so that
participation and drop-off can be analysed.

**Acceptance criteria**

1. Each process event records a case, an activity and a timestamp.
2. The event log records enough Round lifecycle, Sign-up, Match and Withdrawal
   activity to determine when Rounds lose participants.
3. Event timestamps preserve enough Location context to analyse elapsed time
   from sign-ups opening to Sign-up correctly.
4. The event log does not make one Colleague's history visible to another.

### US-11.2 — Derive the proposed success measures

As a product owner, I want the proposed v1 measures derivable from process data
so that the team can agree baselines and targets after launch.

**Acceptance criteria**

1. The data can determine the share of Colleagues at a Location who sign up at
   least once in a calendar month.
2. The data can determine the share of Rounds that are not Cancelled Rounds.
3. The data can determine the Withdrawal rate per Lunch Group.
4. The data can determine the share of Lunch Groups with no pairing repeated
   from the previous four Rounds at that Location.
5. This story does not invent targets; the measures remain proposed until the
   organisation agrees them.

### US-11.3 — Deploy and configure the agreed v1

As an operator, I want a portable, environment-configured deployment so that
Lunch Roulette can be installed without product code changes.

**Acceptance criteria**

1. The application runtime is a single Python/FastAPI process and uses
   PostgreSQL as its database, with PostgreSQL available in Docker for the
   supported environment.
2. The application is deliverable as one Docker container, with the hosting
   platform selected at deployment time.
3. Deployment-specific values are supplied through environment variables,
   including the allowed company domains, Admin email list, brand seed colour
   and email delivery configuration.
4. Development mode can deliver email to the console so that sign-in and
   notification journeys can be exercised without an external mail service.
5. The v1 remains a web application for one organisation.

## 12. V1 scope boundaries

The following are explicit non-goals and must not be treated as missing backlog
items for v1:

- multiple organisations or tenant isolation;
- cross-Location matching or remote/virtual lunches;
- matching by availability, department, interests or seniority;
- restaurant selection, recommendation or booking;
- in-app chat or messaging;
- Slack or Microsoft Teams integrations;
- native mobile applications;
- an Admin control to skip a Round;
- replacing a Colleague after a post-Match withdrawal.

## 13. Requirements traceability

| Business PRD requirement | Backlog coverage |
|---|---|
| Goals and automated weekly journey (§§2–3, 5.2) | US-3.1–US-3.3, US-4.1–US-4.2, US-5.1–US-5.4, US-6.1 |
| Colleague and Admin roles (§4) | US-1.2–US-1.3, US-2.1–US-2.3, US-6.2–US-6.3, US-8.2, US-9.1 |
| First visit (§5.1), A1 | US-1.1–US-1.2 |
| Admin sets up a Location (§5.4) | US-2.1–US-2.2 |
| R1–R4 | US-3.1–US-3.2, US-4.1, US-2.3 |
| M1–M4 | US-3.2, US-5.1–US-5.3 |
| W1–W3 | US-7.1–US-7.3 |
| A2 | US-2.3 |
| A3 | US-6.2–US-6.3, US-11.1 |
| A4 | US-9.1–US-9.2 |
| Notification matrix (§7) | US-1.1, US-5.4, US-6.1, US-7.1–US-7.3, US-8.1–US-8.2 |
| Look and feel (§8) | US-10.1–US-10.2 |
| Proposed success measures (§9) | US-11.1–US-11.2 |
| Technical and deployment decisions Q22, Q27–Q28 | US-11.3 |
| V1 non-goals (§3) | §12 and relevant negative criteria throughout |

