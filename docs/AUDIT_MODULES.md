# Audit — Modules

## Method

Per-module support in this database is expressed through three mutually
exclusive mechanisms:

- `all_modules: true` — supported on every module.
- `supported_on: [<module>, ...]` — supported on a subset.
- `removed_after: "<version>"` — the record existed up to that version,
  then was removed; the generated `module_support[]` is all-false.

## Summary

| Category | Count |
|----------|-------|
| Modules in YAML | 9 |
| Records with `all_modules: true` | majority |
| Records with explicit `supported_on` | delta subset |
| Records with `removed_after` | 5 |

## Status

A systematic page-by-page audit of each Hardware Design manual against
the `supported_on` lists in `at_commands.yaml` and `urcs.yaml` has not
yet been performed. The current `supported_on` values were inherited
from the baseline database and are assumed to be correct; they are
subject to revision in a future audit pass.

## Future work

For each of the nine modules, compare the `supported_on` list against
the corresponding Hardware Design PDF (see `data/modules.yaml` for the
`hw_ref` of each module) and revise where necessary.
