# Audit — URCs

## Method

URCs are free-form result strings (e.g. `+CMTI: ...`, `RING`, `RDY`).
Unlike AT Commands, they do not follow a strict `AT+X` naming pattern,
so a token-based search is unreliable. The audit was therefore limited
to:

1. Verifying that every URC in `data/urcs.yaml` carries a valid
   `manual_ref` pointing into §18 of V1.12.
2. Verifying that every `enabled_by` / `related_urcs` relation is
   two-way and consistent (enforced by `tools/validate.py`).

## Summary

| Category | Count |
|----------|-------|
| Baseline URCs in YAML | 95 |
| New URCs added | 0 |
| Records removed | 0 |

## Note

A full per-token audit of §18 of V1.12 was out of scope for this
revision because PDF text extraction of URC payload strings
(`<number>`, `<type>`, `<alpha>`, ...) is highly lossy. Records added
in future revisions should be validated against §18 manually.
