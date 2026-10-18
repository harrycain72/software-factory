# Domain map

The current business-domain decomposition of Lunch Roulette, maintained under
[bce-architecture.md](../architecture/rules/bce-architecture.md) "Domain map".
Concept names come from [GLOSSARY.md](GLOSSARY.md).

| Domain | Owns these glossary concepts |
|---|---|
| `identity` | Colleague, Admin role, sign-in, account deletion, notification preferences |
| `locations` | Location, Lunch Slot, weekly schedule |
| `rounds` | Round, Sign-up, Cancelled Round |
| `matching` | Match, Lunch Group, Host, Withdrawal |
| `process-log` | process events, success measures |

Outside the business domains:

- The Material Design 3 interface is presentation inside each domain's
  boundaries, plus shared theme assets in `platform`.
- The container, configuration, and PostgreSQL setup belong to `platform` and
  the entry point.
