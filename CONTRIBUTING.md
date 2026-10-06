# Contributing

## Golden rules

1. `data/*.yaml` is the Single Source of Truth. Generated C++ headers must
   never be edited by hand.
2. `include/sim800_at/version.hpp` is **hand-written** and must not be
   produced or overwritten by `tools/generate.py`.
3. All validation rules in `tools/validate.py` must be preserved.
4. Public API in `include/sim800_at/at_api.hpp` is backward-compatible:
   do not change function signatures or behaviour.
5. The `related_urcs` ↔ `enabled_by` relation is two-way and mandatory.

## Adding an AT Command

1. Append a record to `data/at_commands.yaml` with:
   - `name`, `category`, `description`
   - `manual_ref` (format `"V1.12 §x.y.z"`)
   - `source_ref` (ascending, `+`-joined, `V1.02` excluded)
   - exactly one of `all_modules` / `supported_on` / `removed_after`
2. If the record has URCs with non-empty `enabled_by`, update
   `data/urcs.yaml` correspondingly.
3. If it was removed in a later manual, add `removed_after` and
   `version_notes: "Removed in VX.YY."`.
4. Run:

        python tools/validate.py
        python tools/generate.py
        pytest tests/

## Adding a URC

Symmetric to adding a command. Remember to update
`related_urcs` on the enabling command(s).

## Adding a module or category

1. Append to `data/modules.yaml` or `data/categories.yaml`.
2. Category `id` must match `^[A-Za-z0-9_]+$`.
3. Run the pipeline as above.

## Version rules

- `V1.02` must never appear in `source_ref` or `manual_ref`.
- `source_ref` versions must be unique and ascending.
- Compound `manual_ref` uses `;` with descending version order.

## Idempotency

Running `tools/generate.py` twice in a row must not change any generated
file. This is enforced by `tests/test_generate.py`.