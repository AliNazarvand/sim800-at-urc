# Architecture

## Overview

This project ships a static, compile-time database of AT Commands and URCs
for the SIMCom SIM800 Series family, together with ESP32-WROOM-32
integration scaffolding. The database is header-only; all data lives in
ROM/flash when linked into a firmware image.

## Three layers

1. **Source layer** - `data/*.yaml`. Human-edited. The Single Source of
   Truth for modules, categories, AT Commands, and URCs.
2. **Generation layer** - `tools/generate.py`. Reads YAML, writes C++17
   headers under `include/sim800_at/`. Generated files are never edited
   by hand.
3. **Consumption layer** - `include/sim800_at/sim800_at.hpp`. Header-only,
   C++17, `inline constexpr`, no dynamic allocation, no exceptions, no
   Arduino dependencies.

## YAML schema (summary)

### data/modules.yaml

Array of records. Fields: `name`, `display_name`, `hw_ref`. Record order
determines the module index used by every `module_support[]` array.

### data/categories.yaml

Array of records. Fields: `id`, `label`, `manual_chapter`. Record order
determines the `Category` enum values.

**Category ID rule:** `id` must match `^[A-Za-z0-9_]+$`. No spaces,
hyphens, or other special characters are allowed. The `label` field is
free-form and may contain spaces (e.g. `"Bluetooth Application"`).
`tools/validate.py` enforces this rule.

### data/at_commands.yaml

Array of records. Required string fields: `name`, `category`,
`description`, `manual_ref`. Optional list fields: `parameters`,
`responses`, `related_urcs`. Support scope: exactly one of the following three forms.

- `all_modules: true` — the record is supported on every module.
- `supported_on: [<module>, ...]` — the record is supported on a subset.
- `removed_after: "<version>"` — the record existed up to and including
  the named manual version, then was removed. `removed_after` names the
  **last manual version where the record was documented**; removal
  happens in the version(s) after it. The generated `module_support[]`
  array is all-false. `version_notes` is mandatory and records the
  removal. `source_ref` must still list the version(s) where the
  record is documented.

### data/urcs.yaml

Array of records. Required string fields: `name`, `category`,
`description`, `manual_ref`. Optional list fields: `payload`,
`enabled_by`. Support scope: exactly one of the following three forms.

- `all_modules: true` — the record is supported on every module.
- `supported_on: [<module>, ...]` — the record is supported on a subset.
- `removed_after: "<version>"` — the record existed up to and including
  the named manual version, then was removed. `removed_after` names the
  **last manual version where the record was documented**; removal
  happens in the version(s) after it. The generated `module_support[]`
  array is all-false. `version_notes` is mandatory and records the
  removal. `source_ref` must still list the version(s) where the
  record is documented.

## Design decisions

### Variants of an AT Command are one logical record

Test (`AT+X=?`), Read (`AT+X?`), and Write (`AT+X=...`) forms are modeled
as a single logical `ATCommand` record. The `parameters` and `responses`
fields carry the union of all forms. This matches the project's primary
question: *which command is supported on which module*, not *the exact
syntax of each form*.

### Case sensitivity

| Function | Parameter kind | Sensitivity |
|----------|----------------|-------------|
| `find_command(name)` | command name | case-insensitive |
| `find_urc(name)` | URC name | case-sensitive |
| `category_from_id(id)` | category id | case-insensitive |
| `commands_for_module(m)` | module name | case-sensitive |
| `urcs_for_module(m)` | module name | case-sensitive |
| `module_index(m)` | module name | case-sensitive |
| `is_command_supported(c, m)` | module name | case-sensitive |
| `is_urc_supported(u, m)` | module name | case-sensitive |

All functions that take a **module name** are case-sensitive and
consistent.

### Safe behavior on invalid input

- `find_command(nullptr)` -> `nullptr`
- `find_urc(nullptr)` -> `nullptr`
- `module_index(nullptr)` -> `-1`
- `category_from_id(nullptr)` -> `Category::INVALID`
- `is_command_supported(cmd, nullptr)` -> `false`
- `is_urc_supported(urc, nullptr)` -> `false`
- `commands_for_module(nullptr, count)` -> `nullptr`, `count = 0`
- `urcs_for_module(nullptr, count)` -> `nullptr`, `count = 0`
- `module_name_at(index)` with `index >= total_modules()` -> `nullptr`
- `commands_by_category(INVALID/COUNT, count)` -> `nullptr`, `count = 0`
- `urcs_by_category(INVALID/COUNT, count)` -> `nullptr`, `count = 0`

**Invariant:** for every valid `Category c`, `commands_by_category(c, count)`
returns non-`nullptr` **iff** `count > 0`.

### Category enum

- Valid categories are generated from `categories.yaml`, starting at `0`.
- `Category::COUNT` equals the actual number of valid categories.
- `Category::INVALID = 0xFF`, always greater than `COUNT`.
- `validate.py` rejects `len(categories) >= 0xFF`.
- `validate.py` rejects category IDs that do not match `^[A-Za-z0-9_]+$`.
- `category_name(c)` returns the `label`.

### Two-way relationship `related_urcs` / `enabled_by`

The link is two-way and mandatory **except** for URCs with `enabled_by: []`.

### Module scope compatibility (warning, not error)

For every URC `+Y` with `enabled_by: [AT+X, ...]`, the module scope of
`+Y` should be a subset of the scope of `AT+X`. Checked but only emitted
as a **warning**.

### Empty fields

- Mandatory string fields must never be empty.
- Optional list fields may be empty (`[]`).
- `supported_on` must not be empty.

### `A/` and `+++` exception

`validate.py` accepts `A/` and `+++` as valid command names.

## Extending

### Add an AT Command

1. Append a record to `data/at_commands.yaml`.
2. If it has related URCs with non-empty `enabled_by`, update
   `data/urcs.yaml` (two-way).
3. `python tools/validate.py`
4. `cmake -S . -B build && cmake --build build`

### Add a URC

1. Append a record to `data/urcs.yaml`.
2. If `enabled_by` is non-empty, update `data/at_commands.yaml`.
3. `python tools/validate.py`
4. `cmake -S . -B build && cmake --build build`

### Add a module

1. Append a record to `data/modules.yaml`.
2. Check `at_commands.yaml` and `urcs.yaml` for `all_modules: true`.
3. `python tools/validate.py`
4. `cmake -S . -B build && cmake --build build`

### Add a category

1. Append a record to `data/categories.yaml`. The `id` must match
   `^[A-Za-z0-9_]+$`; the `label` is free-form.
2. `python tools/validate.py`.
3. `cmake -S . -B build && cmake --build build`.

## Sources of truth

- `data/modules.yaml` is the only source of truth for module names.
- `data/categories.yaml` is the only source of truth for category ids
  and labels.

## Known limitations

- The database does not mirror the full SIM800 family.
- If `at_commands.yaml` grows very large, it can be split per-category
  in a future revision.

## source_ref (record-level metadata)

Mandatory `source_ref` field on every command and URC record. Value is
one or more version identifiers joined by `+`:

- Single: `V1.01`, `V1.10`, `V1.12`
- Two: `V1.01+V1.10`, `V1.01+V1.12`, `V1.10+V1.12`
- Three: `V1.01+V1.10+V1.12`

Members must appear in ascending order.

`source_ref` is stored only in YAML. Not emitted into C++ headers.

## version_notes (record-level metadata)

Optional string field. Documents differences between manual versions
without polluting `description`. `description` carries only the functional
description. `version_notes` is stored only in YAML.

When a record has `removed_after`, `version_notes` must use the exact
format `"Removed in VX.YY"` (e.g., `"Removed in V1.02."`). The version
named must be the immediate successor of `removed_after` in the known
version order. Enforced by `tools/validate.py`.

Other formats (e.g., `"Deprecated in VX.YY"`) are rejected by
validation. If a record needs deprecation semantics distinct from
removal, a separate field must be introduced in a future revision.

## manual_ref format

`manual_ref` must be `"<version> §<section>"`.

- Single: `"V1.12 §3.3.5"`.
- Compound: `"V1.12 §3.3.5; V1.10 §3.2.28"` (descending version order).

`tools/validate.py` enforces this format.

**Consistency rule:** every version mentioned in `manual_ref`
must also appear in `source_ref`.

## C++ emission rules for source_ref and version_notes

`source_ref` and `version_notes` are never added to `struct ATCommand` or
`struct URC`.

## Manual version priority

V1.12 > V1.10 > V1.01.

## Completeness limitation

Completeness in this project does not mean agreement with any external
reference.
## JSON Schema layer

Four JSON Schemas under `schemas/` describe the on-disk shape of the YAML
sources: `modules.schema.json`, `categories.schema.json`,
`at_commands.schema.json`, `urcs.schema.json`.

Responsibility split between `tools/validate.py` and the schemas:

- **Schema** — data types, required/optional fields, simple regexes
  (`manual_ref`, `source_ref`, category `id`), simple enums
  (`category`, `removed_after`, parameter `type`), in-record constraints
  such as the XOR between `all_modules` / `supported_on` / `removed_after`.
- **Python validator** — cross-record and cross-file rules only:
  two-way `related_urcs` ↔ `enabled_by`, `removed_after` consistency with
  `source_ref`, URC/enabler removal consistency, `manual_ref` consistency
  with `source_ref`.
- Simple in-record rules live in **exactly one** layer. The Python
  validator does not duplicate regexes or enums defined in the schema.

## Generation pipeline

`tools/generate.py` reads `data/*.yaml` and writes C++17 headers under
`include/sim800_at/`. The generated set is exactly:

- `at_types.hpp`
- `at_commands.hpp`
- `urcs.hpp`
- `at_api.hpp`

`include/sim800_at/version.hpp` is hand-written and **explicitly excluded**
from generation; the generator refuses to write it.

## Idempotency

Re-running the generator on unchanged YAML produces byte-identical output.
This is enforced in CI by `tests/test_generate.py`.

## Optional dist outputs

`python tools/generate.py --with-dist` additionally emits JSON, CSV and
Markdown into `dist/`. This is **off by default** and the `dist/` folder is
git-ignored.
