# Test-driven development rules

**Status:** adopted for all new and changed product behavior
**Scope:** Any product code with testable behavior. Does not apply to
`.agents/`, `.claude/`, `.codex/`, `.github/agents/`, `factory/`, `AGENTS.md`,
or `tests/test_factory_orchestration.py` — factory-owned paths the builder
may not touch regardless. Vocabulary and workflow are adapted from
aihero.dev's `tdd` skill (https://www.aihero.dev/skills-tdd).

## How to apply these rules

Follow the loop for every behavior the spec describes. Record an exception in
the pull request when a behavior genuinely cannot be driven this way (for
example, a pure configuration change with no observable behavior), together
with the reason. A change is complete when every acceptance criterion in
`spec.md` has a test that failed before its matching implementation and
passes after it, and `build.md` states that this was true for each one.

## Rules

### 1. Confirm the seam before writing a test

- A seam is the public boundary where behavior can be observed or altered
  without reaching inside the module — a behavioral boundary, not a file or
  function name. `spec.md` must name the seam for each test case before
  implementation starts; no test goes at an unconfirmed seam.
- Choose seams from [bce-architecture.md](bce-architecture.md) rule 9: by
  default a domain's use-case control operation or the plain facade a
  boundary delegates to; an exposed boundary only for system tests.
- If the agreed seam is unclear or contested, stop and raise it rather than
  guessing; resolving it belongs in `spec.md`, not in the test file.

### 2. Drive one behavior at a time: red, then green

- Work vertically: write one failing test for one behavior, then the minimal
  code that makes it pass, then move to the next behavior. Never write a
  batch of tests before any implementation exists — bulk-written tests verify
  imagined behavior, not the real path.
- The first cycle for a story is a single path end to end (a tracer bullet)
  that proves the chosen seam works before expanding to edge cases.
- Refactoring is not part of this loop. Once a behavior is green, stop;
  structural cleanup is the reviewer's concern in code review, not an
  implementation-time step.

### 3. Mock only at system boundaries

- Mock external APIs, time, randomness, and — when isolation genuinely
  requires it — the filesystem or database. Never mock a module this
  repository owns.
- A test with a mock pointed at an internal module, or a database query used
  to verify behavior rather than to set up state, is implementation-coupled
  and must be rewritten against the seam instead.

### 4. Name and assert from the outside

- Name tests as capabilities a caller would recognize ("user can check out
  with an expired cart"), never after internal calls ("checkout calls
  paymentService.process").
- Expected values must come from the spec, a known-good literal, or a worked
  example — never recomputed with the same logic as the implementation under
  test. A test whose expected value is derived the same way as the code it
  checks is tautological and proves nothing.

### 5. Known limits

- No instruction makes an agent follow this loop every time. A reviewer who
  finds a test written after its implementation, a bulk-written batch, or a
  tautological assertion must send it back as a correctness finding, not a
  style note.
- End-to-end and browser tests follow after the unit-level behavior is green,
  never before it — they confirm wiring, not design.
