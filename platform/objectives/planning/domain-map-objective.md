# Objective: create the domain map

Goal: create `docs/solution/domain-map.md`, the project's business-domain
decomposition, so that every later story has exactly one owning domain and
stories in different domains can be built in parallel.

Run this before [epics-and-stories-objective.md](epics-and-stories-objective.md),
which reads the map. No domain map exists yet.

## Sources (the only truth)

- `docs/solution/business-prd.md`, `docs/solution/technical-prd.md`,
  `docs/solution/GLOSSARY.md`
- `docs/architecture/rules/bce-architecture.md`: rule 1 (partition by
  business domain), rule 6 (domains interact through boundary or control
  only), rule 7 (platform holds technology, not business) and "Domain map".
  These shape the decomposition; the remaining rules govern code inside a
  domain and reach stories later through `spec.md`.

## Domains

Each domain is named after its business responsibility in glossary terms,
in lower-case kebab case, and owns a cohesive set of glossary concepts: the
concepts that change together and share invariants. Prefer the decomposition
with the fewest cross-domain interactions; a domain earns its place by owning
state and invariants no other domain needs to hold.

## The map contains

1. **Domain table:** `Domain | Owns these glossary concepts | Responsibility`,
   where responsibility is one sentence.
2. **Interactions table:** `From | To | Through | Why`, one row per
   dependency between domains. `Through` is the target's control operation,
   boundary, or a domain event the source consumes, per rule 6.
3. **Outside the business domains:** where presentation, configuration,
   persistence setup, email transport, scheduling and deployment live: each
   domain's boundary, `platform`, or the entry point.

## Done when

- every glossary concept is owned by exactly one domain, or is listed as
  having no owner with the reason (for example a term the glossary marks
  _Avoid_, or a role rather than a stored concept)
- every business rule in the PRDs falls inside one domain's concepts, or its
  cross-domain interaction appears in the interactions table
- the interactions table forms no cycle
- `platform` owns no glossary concept and no business rule
- every technical PRD requirement that belongs to no business domain appears
  under "Outside the business domains"
- every gap, contradiction or ambiguity in the sources that affects the
  decomposition is listed under Open questions, with the domains it affects

## Output

`docs/solution/domain-map.md` containing the domain table, the interactions
table, "Outside the business domains" and Open questions. It opens with
relative links to `docs/architecture/rules/bce-architecture.md` "Domain map",
the rule it implements, and `docs/solution/GLOSSARY.md`, the source of
concept names.
