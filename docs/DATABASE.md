# Database

## Scope

Static, header-only C++17 database of AT Commands and URCs for the SIM800
Series family, extracted from the SIMCom AT Command Manuals V1.01, V1.10
and V1.12 (plus Hardware Design manuals for module scoping).

## Statistics

| Item            | Count |
|-----------------|-------|
| Modules         | 9     |
| Categories      | 17    |
| AT Commands     | 346   |
| URCs            | 95    |

(This file is a description; the definitive numbers are the constants
`sim800_at::total_commands()`, `sim800_at::total_urcs()`,
`sim800_at::total_modules()` and `sim800_at::total_categories()`.)

## Source references

Each record carries:

- `manual_ref` — `"<version> §<section>"` (compound form uses `;` and
  descending version order).
- `source_ref` — versions in ascending order joined by `+`.
  `V1.02` never appears here.
- `version_notes` — human-readable difference notes; required when
  `removed_after` is set, in format `"Removed in VX.YY."`.

## Module support

Every record declares its support scope using exactly one of:

- `all_modules: true`
- `supported_on: [<module>, ...]`
- `removed_after: "<version>"` (with mandatory `version_notes`)

For removed records, the generated `module_support[]` array is all-false.

## See also

- `docs/ARCHITECTURE.md` — design decisions and schema.
- `docs/API.md` — public C++ API.