# Objective: create the epics and user stories

Goal: create `docs/planning/epics-and-user-stories.md`, a backlog of epics
and stories that the factory builds in the widest possible parallel waves.

## Sources (the only truth)

- `docs/solution/business-prd.md`, `docs/solution/technical-prd.md`,
  `docs/solution/GLOSSARY.md`
- `docs/solution/domain-map.md`: its domains and the glossary concepts
  each one owns decide each story's domain, lock names and split points.
  Architecture rules reach stories later through `spec.md`, so stories carry
  behaviour only.

## Epics

One epic per coherent capability a user or operator gains. Each epic gets a
number, a name, and one sentence describing that capability.

## Each story carries

- ID `<epic>.<story>`; the factory assigns `US-###` at intake
- Domain: one domain from the map, or `platform`
- As a … I want … so that …
- Covers: the rule IDs or technical PRD sections it implements
- Acceptance criteria: Given/When/Then, each one testable on its own
- Depends: earlier story IDs, or `none`
- Locks: narrow `<domain>-<area>` names (e.g. `identity-signin`, `locations`)

## Story shape

One builder, one feature branch, one domain. When a capability spans domains
or needs a later story, split it so every part depends only on earlier
stories.

## Epic 0: app skeleton

Admitted alone. Derive its contents from the technical PRD's application,
data, configuration and deployment requirements, plus whatever a later story
needs before it can start:

- a runnable app with a health check
- the deployable image
- environment configuration that fails startup when it is invalid
- the database with per-domain migrations
- the development email path
- a test harness with one passing test
- the base page layout
- every expected dependency installed

Its `build.md` records the real install/test/lint/format/type-check commands
and per-slot database create/drop under `## Factory isolation`.

Epic 0 holds `dependencies, migrations, compose, repo-profile`. Every later
story adds tables through its own domain's migrations and uses the installed
dependencies, so its locks stay domain-scoped.

## Waves

Group stories into waves. A story joins the earliest wave after all its
dependencies, and stories in one wave share no lock.

## Done when

- the coverage table maps every business rule, user journey step,
  notification and technical requirement in the sources to at least one story
- every epic contains at least one story and every story belongs to one epic
- every Depends points to an earlier story and the graph has no cycles
- the wave table shows no shared lock inside any wave
- every acceptance criterion names one observable outcome
- every gap, contradiction or ambiguity in the sources is listed under
  Open questions, with the affected stories

## Output

`docs/planning/epics-and-user-stories.md` containing the epics and stories,
then the wave table, the coverage table and Open questions.
