# Boundary–Control–Entity architecture rules

**Status:** adopted for all new and changed product code
**Scope:** All product code, independent of programming language, framework,
or runtime. Terms such as "module", "operation", and "contract" mean whatever
unit the language provides: a directory, package, namespace, file, class,
function set, or interface. Does not apply to factory-owned paths.
**Sources:** the BCE pattern as described at [bce.design](https://bce.design/).
Quoted phrases come from that site. Where the site is silent or only
"discourages" something, this file makes a project decision and says so.
These rules supplement the [technical PRD](../../solution/technical-prd.md)
and define the default seams for
[test-driven-development.md](test-driven-development.md).

## How to apply these rules

Decide the owning business domain first, then the BCE layer inside it, before
writing any code or test. Record an exception in the pull request when a rule
cannot apply, together with the reason and its effect on dependencies. A
change is complete when every new or changed piece of code sits in exactly one
domain and one layer, and every dependency it adds points in an allowed
direction.

## Rules

### 1. Partition by business domain first, BCE second

- The top level of product code is a set of business domains, which
  bce.design calls business components. Name each one "after their business
  responsibility, not technical concerns".
- Each domain is a "self-contained module" containing exactly three layers:
  `boundary`, `control`, and `entity`. Every domain uses the same structure.
- Aim for "maximal cohesion within the component and minimal coupling between
  components": related functionality stays together in one domain.
- Never create top-level technical groupings that span domains, such as
  shared `controllers`, `models`, `services`, or `repositories` collections.
- Name domains and their contents with terms from
  [GLOSSARY.md](../../solution/GLOSSARY.md). Do not use a term the glossary
  lists under _Avoid_.
- Each glossary concept is owned by exactly one domain. Only the owner holds
  that concept's state and enforces its invariants.

Language-neutral layout:

```text
<product-root>/
  <domain-a>/
    boundary/   exposes this domain to users and systems
    control/    business logic: use-case actions and integration access
    entity/     domain model: concepts, data, invariants
  <domain-b>/
    boundary/
    control/
    entity/
  platform/     technical capabilities with no business rules
  <entry point> wires the domains together at startup
```

Follow the language's own naming and file conventions inside each layer. The
structure is the rule, not the spelling.

### 2. Entity: the domain model

- An entity is a core business concept: its data, its relationships, and the
  rules that must always hold for it, such as "a Lunch Group has 3 to 5
  Colleagues". Entities may reference and compose other entities in the same
  domain.
- An entity may carry declarative persistence mappings, meaning metadata that
  describes how it is stored. It never executes input or output itself: no
  queries, network calls, clock reads, random draws, or message sending. Time,
  randomness, and identifiers it needs are passed in.
- An entity never calls a control or a boundary. When something must happen
  in response to an entity change, the entity emits a domain event.
- An entity rejects any change that would break its invariants. It never
  relies on a caller having checked first.

### 3. Control: business logic and integration access

- A control is "stateless procedural logic": the actions and commands that
  carry out business use cases. It manipulates and orchestrates entities and
  owns the transaction and consistency scope of the use case.
- Name use-case controls as verb phrases from the domain, such as "sign up for
  Round" or "form Lunch Groups". Map each user story to one or more named
  control operations.
- Access to storage and external systems also lives in control, as integration
  controls: loading and saving entities, sending email, reading the clock,
  drawing random values, and calling external services. bce.design does not
  name a layer for this; the placement follows from its direction rule, which
  forbids controls from invoking boundaries.
- Controls within the same domain may call each other. Keep use-case logic out
  of integration controls and transport details out of use-case controls.
- A control never calls a boundary. When a boundary must react to something a
  control did, the control publishes a domain event.
- A control returns results and domain-specific failures as plain data, never
  transport-specific values such as HTTP statuses, rendered pages, or raw
  database rows.

### 4. Boundary: exposing the domain

- A boundary "exposes the functionality of components to users and systems":
  pages, HTTP routes, form handlers, scheduled triggers, message handlers, and
  command-line commands. HTTP boundaries also follow
  [api-endpoint-design.md](api-endpoint-design.md).
- A boundary performs "input validation and transformation", authenticates
  the caller, delegates business logic to controls, and turns the result into
  the transport's response. It makes no business decision.
- A boundary may access entities directly for simple data operations that
  involve no business rule, such as reading an entity to display it. An HTTP
  boundary still maps entities to separate request and response models, as
  `api-endpoint-design.md` requires.
- Boundaries do not call other boundaries. Use a control to orchestrate
  instead.
- Presentation, such as page templates and styling, belongs to the boundary
  that renders it.

### 5. Dependencies flow B → C → E only

- Allowed inside a domain: boundary → control, boundary → entity,
  control → control, control → entity, and entity → entity.
- Forbidden: entity → control, entity → boundary, control → boundary,
  boundary → boundary, and any dependency cycle. Reverse communication happens
  only through domain events.
- Every layer may depend on `platform`. `platform` depends on no domain.
- "Zero dependencies": use existing language and platform functionality
  before adding an external library. The BCE structure itself needs no
  framework, and no library may be added only to implement or enforce it.
- Where the toolchain can check dependency direction without a new library,
  add that check to the lint command in `factory/repo.md`.

### 6. Domains interact through boundary or control only

- One domain may use another only through the other domain's boundary or
  control layer, or by consuming its domain events.
- Never use another domain's entities directly. bce.design only discourages
  this; this project forbids it because the factory builds domains in
  parallel jobs, and shared entities would couple jobs that hold separate
  locks.
- Data that crosses a domain line is a plain copy, such as identifiers and
  simple values, never a live entity from the sending domain.
- Each domain owns its stored data. When several domains share one database,
  each table or collection still belongs to exactly one domain.
- Dependencies between domains form no cycle. When two domains seem to need
  each other, publish a domain event from one side or move the shared concept
  to its single rightful owner.

### 7. Platform holds technology, not business

- bce.design does not define cross-cutting code; this section is a project
  decision. `platform` holds capabilities several domains need: configuration
  loading, logging, database connections, email transport, and
  process-event recording mechanics.
- `platform` contains no business rule and no glossary concept. A
  domain-specific use of a platform capability, such as the wording of a Match
  notification, lives in that domain's control layer.
- Keep `platform` small. Code used by only one domain belongs inside that
  domain.

### 8. Wire domains together at the entry point

- bce.design does not prescribe wiring; this section is a project decision.
  The application's entry point connects integration controls to their real
  storage and external systems and reads deployment configuration. No domain
  reads deployment configuration directly.
- Tests use the same wiring mechanism to substitute fakes, so production
  wiring and test wiring cross the same seam.

### 9. Test each layer at its bce.design level

bce.design states: "Exposed boundaries are tested using system tests/e2e
tests, plain facades using integration tests, and sufficiently complex
controls or entities using unit tests." Combined with
[test-driven-development.md](test-driven-development.md):

- **Default TDD seam:** a domain's use-case control operation, or the plain
  facade a boundary delegates to. `spec.md` names it as the domain plus the
  operation, for example `rounds: sign up for Round`. Test it as an
  integration test.
- **Sufficiently complex controls and entities** get their own unit tests.
  Simple ones are covered through the default seam instead.
- **Exposed boundaries**, such as routes and scheduled triggers, get system
  or end-to-end tests. Per test-driven-development.md rule 5, write these
  after the behavior behind them is green.
- **Fakes:** replace only integration controls that face storage, email,
  time, randomness, or external services, and only where
  test-driven-development.md rule 3 allows mocking. Never fake a use-case
  control or an entity.

## Domain map

Each project records its decomposition in a domain map: every business
domain, the glossary concepts it owns, and where work that belongs to no
business domain lives (each domain's boundary, `platform`, or the entry
point). The repository profile names the map's location. Change the map in
its own reviewed change before code depends on a new or moved domain.
