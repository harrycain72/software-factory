# API endpoint design rules

**Status:** adopted for new and changed endpoints
**Scope:** All FastAPI HTTP endpoints: server-rendered pages, forms, downloads,
health checks, and the JSON extraction API. These rules supplement the
[technical PRD](../prd/technical-prd.md), especially its route, security, and
extraction sections. Protocol requirements come from the cited standards;
other rules are project conventions.

## How to apply these rules

Apply every rule that fits when proposing or changing an endpoint. Record an
exception in the pull request when a rule cannot apply, together with the
reason and the client impact. A route is complete when its documented request,
response, errors, access rules, side effects, and tests match the implementation.

## Rules

### 1. Design the public contract before the handler

- Define the method, path, path and query parameters, request body, response
  schema, success status, error statuses, authentication, authorization, and
  pagination before implementation. Describe JSON APIs in OpenAPI; describe
  browser form fields, redirects, and rendered errors in route documentation
  or testable examples.
- Name the caller, their task, and the source of truth. Include example valid
  requests and responses, meaningful failure examples, privacy and caching
  needs, side effects, limits, retry behavior, and transaction boundaries.
- Decide whether an endpoint is needed at all. Check existing routes and
  clients before adding a new operation or changing a contract.
- Treat documented response fields, status codes, defaults, ordering, limits,
  and error types as client-visible behavior. Do not silently change them in a
  minor release.
- Keep request and response models separate. Request models allow only fields
  the caller may set; response models expose only fields the caller may see.
- Define each field's type, allowed values, size, units, requiredness, default,
  and meaning when omitted or `null`. Use RFC 3339 timestamps with an offset
  for instants; document local time zone and daylight-saving behavior for
  schedule inputs. Define rounding for decimal values.
- Specify accepted `Content-Type` values and response media types. Negotiate
  with `Accept` where multiple representations exist. Define whether empty
  collections are `[]` or an envelope and keep that shape stable.

### 2. Model business resources, not database tables

- Use plural nouns for collections and an identifier for one resource:
  `/groups` and `/groups/{group_id}`.
- Add a nested collection only when the parent owns or meaningfully scopes the
  child. Keep paths shallow and use opaque, stable identifiers.
- Do not expose a table, join, or internal storage layout as an endpoint just
  because it exists in PostgreSQL. Shape responses around client tasks and
  business concepts.
- Use standard resource operations where they fit: `GET` reads, `POST` creates
  within a collection, `PATCH` changes supplied mutable fields, `PUT` replaces
  a complete representation, and `DELETE` removes or retires a resource.
- Model a domain action that does not fit resource lifecycle as an explicit,
  documented action route. State its preconditions, side effects, replay
  behavior, and result. The existing sign-up and withdrawal form routes are
  examples of domain actions.

### 3. Preserve HTTP method semantics

- `GET` and `HEAD` must be read-only from the caller's perspective. They must
  not trigger sign-up, withdrawal, token redemption, emails, or other business
  state changes.
- `HEAD` returns the headers of the corresponding `GET` without a body.
  Document the `PATCH` media type and semantics; distinguish omitted fields
  from fields explicitly cleared. `PUT` is a full replacement, not a partial
  update. State whether repeat `DELETE` returns `204` or `404`; either can be
  consistent with idempotent effects.
- Design `PUT`, `DELETE`, and safe methods so replaying the same request has
  the same intended effect. For retryable `POST` actions that may create a
  record or send an external side effect, make the action naturally idempotent
  or accept an idempotency key. Scope a key to caller and action, reject reuse
  with a different payload, atomically retain the original outcome, and
  document its retention window.
- A successful synchronous JSON API creation returns `201 Created`, a
  `Location` header for the primary resource, and its representation when
  useful. Browser form creation may use `303 See Other` to show the new
  resource after the POST. Return `202
  Accepted` only when processing continues asynchronously, and provide a
  status resource or other documented way to observe completion.
- Use `200 OK` when returning a representation and `204 No Content` only when
  there is intentionally no response body. A `204` or `304` response has no
  body. A successful browser form POST normally redirects to a GET page to
  prevent resubmission on refresh.

### 4. Validate at the boundary and return precise errors

- Parse and validate types, formats, size limits, enum values, and cross-field
  constraints before domain work or persistence. Reject unknown write fields
  in project API requests. Define duplicate field, omitted field, and `null`
  behavior explicitly.
- Use `400` for malformed syntax, `401` for absent or invalid credentials,
  `403` when the authenticated caller lacks permission, `404` when the
  resource must not be disclosed, `409` for a resolvable state conflict, and
  `422` for a syntactically valid request that violates domain or validation
  rules. Use `405` with `Allow` for an unsupported method, `415` for an
  unsupported request media type, and `406` when no response representation
  satisfies an explicit `Accept` requirement. Use `429` for rate limits and
  `503` for temporary unavailability; include `Retry-After` when a meaningful
  retry time is known. Send the applicable `WWW-Authenticate` challenge with
  `401`.
- Return JSON API errors as `application/problem+json`. Include a stable
  `type`, a short `title`, the HTTP `status`, a request-specific `instance` or
  request ID, and safe field-level details where they help a caller correct
  input.
- Browser form errors may render HTML with accessible field messages or an
  error page. Their HTTP status must still reflect the result.
- Do not include stack traces, SQL, secrets, authentication tokens, or personal
  data in an error response.

### 5. Authorize every object and property

- Authenticate before accessing protected data, then authorize the caller for
  the specific resource, parent resource, and action. An identifier supplied by
  the client is never evidence of permission.
- Apply the same authorization check to list filters, counts, exports,
  pagination cursors, download links, and nested routes. A cursor conveys
  position only; it never grants access.
- Enforce field-level permissions when serializing responses and applying
  updates. Never bind request JSON directly to an ORM object.
- Browser routes use the signed session and CSRF protection specified in the
  technical PRD. `/api/v1/extract/...` uses its bearer token, remains
  read-only, and must never expose names, emails, or email bodies.
- Enforce authorization when loading records as well as at the route boundary.
  Apply it to exports, counts, and each later page. Validate untrusted IDs
  even when they are opaque or hard to guess.
- Prefer credentials in authorization headers or secure cookies. The PRD's
  emailed sign-in link is a narrow exception: it contains a short-lived,
  single-use token in the URL. Hash it at rest, redeem it only through the
  confirmation POST, redact its URL from logs and telemetry, prevent referrer
  disclosure, and mark the page `Cache-Control: no-store`. Do not introduce
  more URL-token flows without reviewing their exposure.
- For any endpoint that fetches a caller-supplied URL, allowlist schemes and
  destinations, block private and metadata addresses after DNS resolution,
  and bound redirects and timeouts. Review future webhook and import routes
  for server-side request forgery.

### 6. Make lists bounded, deterministic, and safe to resume

- Every collection endpoint has a documented default and maximum `limit`, and
  rejects or clamps values above the maximum consistently.
- Prefer cursor pagination for mutable or large collections. Cursors are
  opaque, URL-safe, scoped to the endpoint and filter set, and expire after a
  documented interval if expiration is needed. Do not encode authorization or
  sensitive data in them. Reject a cursor used with a different filter or
  caller scope. Document how concurrent inserts or deletes affect pages;
  ordinary cursor pagination does not guarantee a frozen snapshot.
- Document supported filters and sort keys; allow only a fixed list. Define a
  stable default sort and add a unique tie-breaker so a cursor does not skip or
  duplicate rows merely because equal values changed order.
- Return an explicit continuation indicator, such as `next_cursor` and
  `has_more`. The extraction API keeps its PRD-defined gap-free transaction
  cursor rather than introducing a generic offset scheme.

### 7. Prevent lost updates

- For a resource that users can edit concurrently, return an `ETag` or a
  version field. Require `If-Match` or that version on updates and deletes when
  a stale write could overwrite another user's work.
- Return `412 Precondition Failed` when an HTTP precondition does not match;
  use `409 Conflict` for a business-state conflict that a caller can resolve.
- Put each state change and its required audit event in one database
  transaction. Preserve the PRD's append-only event log and tombstone rules.
- Return `428 Precondition Required` if an endpoint requires `If-Match` and it
  is missing. Recheck mutable business conditions inside the transaction.
  Persist email and webhook work through the outbox so a retry cannot publish
  an uncommitted operation or lose a committed one.
- Define what a client should do after a timeout or connection loss. Do not
  imply that a missing response means the database operation rolled back.

### 8. Limit work and protect sensitive operations

- Set request body, upload, query, page-size, and execution-time limits before
  releasing an endpoint. Apply rate limits to sign-in, token redemption,
  extraction, export, and any expensive search or fan-out operation.
- Avoid unbounded synchronous work. For work that can exceed the request time
  budget, create an observable asynchronous job and return `202 Accepted`.
- Use HTTPS in production. Set CORS only for explicitly required origins and
  methods. Do not put credentials or secrets in ordinary paths, query strings,
  logs, or telemetry; the sign-in link exception is specified above.
- Return an asynchronous status resource that exposes pending, succeeded, and
  failed states when using `202`. Define job retention and duplicate-submission
  behavior. A response must not report completion before durable work finishes.

### 9. Make operations observable without logging private data

- Accept or generate a request ID, return it in the response, and include it
  in structured logs, audit events, and error `instance` values.
- Log the endpoint, method, outcome class, latency, authenticated actor ID
  where permitted, and authorization decision. Redact bodies and credentials
  by default.
- Use route templates such as `/groups/{group_id}` in metrics to avoid
  high-cardinality labels and leaking URL values. Redact cookies, tokens,
  email addresses, and sensitive query strings from logs and traces; set
  retention for operational data according to its privacy requirements.
- Publish health and readiness separately when deployment needs both; neither
  endpoint may reveal configuration, credentials, or user data.

### 10. Define caching and conditional reads

- Decide caching behavior for each response. Use `Cache-Control: no-store` for
  sign-in, token, and sensitive personalized responses. Use `private` for
  personalized responses that may be stored only in a private cache. Public
  caching needs an explicit freshness policy and correct `Vary` fields when
  representation depends on request headers.
- For stable, frequently read resources, consider `ETag` or `Last-Modified`
  and conditional `GET` with `304 Not Modified`. Define the representation
  covered by a validator. A write precondition protects concurrent edits;
  a read validator reduces transfer size.
- Test browser or proxy behavior when caching affects privacy or correctness.
  `GET` alone does not prevent a sensitive response from being cached.

### 11. Evolve contracts deliberately

- Put the major version in the path of every JSON API route, using `/api/v1/...`
  for the current contract. Keep browser pages, HTML form submissions, browser
  downloads, and operator health checks unversioned. For example,
  `GET /sign-in` displays the form and `POST /sign-in` submits it. Apply this
  convention by route purpose, regardless of whether the client runs in a
  separate container.
- Keep the same API major version across ordinary deployments and compatible
  additions. A separate client deployment does not require a new version.
  Introduce `/api/v2/...` only when an incompatible contract must coexist with
  `/api/v1/...` for clients that update or roll back independently.
- Make additive changes when possible: add optional response fields and
  optional request fields with defaults that preserve prior behavior.
- Do not remove or rename fields, change a field's type or meaning, narrow
  accepted values, change default behavior, or introduce pagination to an
  existing unbounded list within the same API version. Document whether
  response enum values are open to additions; new values can break clients.
- For a breaking change, publish a new versioned API surface, migration notes,
  a deprecation date, and an overlap period. Use standardized `Deprecation`
  and `Sunset` headers when they help automated clients. Keep `/api/v1` stable
  for Celonis consumers according to its documented contract.
- Keep OpenAPI, examples, implementation, and tests synchronized. Document
  authentication, errors, rate limits, cursor behavior, and retry rules in
  terms a client developer can use without reading server code.

### 12. Test observable behavior

- Test the documented success status, headers, schema, and semantics for every
  endpoint.
- Test invalid input, expired or missing credentials, cross-tenant or
  cross-location object access, forbidden field updates, stale writes,
  idempotent retries, limit boundaries, cursor tampering, and rate-limit
  behavior where applicable.
- Test unknown and oversized fields, unsupported media types, missing CSRF,
  another caller's valid object ID, conflicting idempotency keys, conditional
  reads, cache headers, and temporary dependency failure where applicable.
- For state-changing endpoints, test that the database change and required
  event log entry commit or roll back together. For extraction endpoints, test
  that responses contain no personal data and no committed row is skipped over
  a cursor boundary.
- Verify documented OpenAPI against the actual JSON API response and test
  browser form redirects and accessible error rendering. Keep tests
  deterministic and independent of real email or external network.

## Review checklist

- [ ] JSON API routes use the current `/api/v1/...` contract; browser and
      health-check routes remain unversioned.
- [ ] The OpenAPI contract names every request field, response field, status,
      error, authentication requirement, and pagination parameter; browser
      forms document fields, redirects, and rendered errors.
- [ ] The path represents a business resource or documented domain action.
- [ ] The method is safe or idempotent when its HTTP semantics require it.
- [ ] Authorization covers the specific object, its properties, and every
      collection, cursor, and export path.
- [ ] Lists have a bounded limit and stable ordering; mutable lists use an
      opaque cursor.
- [ ] JSON API errors use `application/problem+json`; browser errors are
      accessible, and neither discloses sensitive detail.
- [ ] Media types, input limits, caching, privacy, and rate limits are defined.
- [ ] Concurrent modifications, retries, rate limits, and transaction/event-log
      behavior have been considered and tested.
- [ ] The change is compatible with current clients, or includes a version and
      migration plan.

## Research basis

Research reviewed on 2026-10-17. These are primary specifications and
maintainer guidance. Project-specific rules above adapt them to the PRD.

- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html) —
  safe and idempotent methods, conditional requests, status codes, and
  `Location` on creation.
- [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html) —
  cache directives, privacy, and conditional reuse.
- [RFC 9457: Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html)
  — standard JSON error representation and media type.
- [RFC 3339: Date and Time on the Internet](https://www.rfc-editor.org/rfc/rfc3339.html)
  — unambiguous timestamp representation.
- [RFC 6585: Additional HTTP Status Codes](https://www.rfc-editor.org/rfc/rfc6585.html)
  — `428 Precondition Required` and `429 Too Many Requests`.
- [RFC 9745: Deprecation](https://www.rfc-editor.org/rfc/rfc9745.html) and
  [RFC 8594: Sunset](https://www.rfc-editor.org/rfc/rfc8594.html) —
  communicating endpoint retirement.
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html) —
  machine-readable HTTP contracts.
- [OWASP API Security Top 10, 2023](https://api-security.owasp.org/editions/2023/en/0x11-t10/)
  — object and property authorization, authentication, and resource-consumption
  risks.
- [Google AIP-121: Resource-oriented design](https://google.aip.dev/121) —
  resource hierarchy and separation from storage models.
- [Google AIP-158: Pagination](https://google.aip.dev/158) — bounded list
  responses and opaque continuation tokens.
- [Google AIP-180: Backwards compatibility](https://google.aip.dev/180) —
  stable contracts and compatible evolution.
- [Google AIP-185: API versioning](https://google.aip.dev/185) — major versions
  in the REST API path.
- [Microsoft REST API design guidance](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design)
  — client-oriented resources, API versioning choices, and compatible evolution.
- [OWASP REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)
  and [CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
  — request protection, sensitive data, and endpoint security controls.
