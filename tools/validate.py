#!/usr/bin/env python3
"""Static validation of the SIM800 AT Command & URC database.

Layered validation:
  1. JSON Schema  — structural: types, required fields, regexes, enums,
     required-key XOR between the three scope keys.
  2. Python rules — cross-record and cross-file rules, plus cross-field
     rules that are not expressible in JSON Schema Draft 7 (notably the
     strict "exactly one truthy scope" rule, which also rejects
     ``all_modules: false`` together with no other scope key set).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    import jsonschema
except ImportError:
    print("jsonschema is required. Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SCHEMA_DIR = PROJECT_ROOT / "schemas"

# ---------------------------------------------------------------------------
# Version tables
# ---------------------------------------------------------------------------
ALL_VERSIONS = {
    "V1.01": 0,
    "V1.02": 1,
    "V1.10": 2,
    "V1.12": 3,
}
SOURCE_REF_VERSIONS = {"V1.01", "V1.10", "V1.12"}

MANUAL_REF_SINGLE = re.compile(r"^V1\.(01|10|12) §[\d\.]+$")
REMOVAL_VERSION_PATTERN = re.compile(
    r"\bRemoved\s+in\s+(V\d\.\d\d)\b",
    re.IGNORECASE,
)


def load_yaml(name):
    p = DATA_DIR / name
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def load_schema(name):
    p = SCHEMA_DIR / name
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_schema(instance, schema, label, errors):
    validator = jsonschema.Draft7Validator(schema)
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.path)):
        path = "/".join(str(x) for x in err.path) or "<root>"
        errors.append(f"schema[{label}] {path}: {err.message}")


# ---------------------------------------------------------------------------
# Python-layer rules
# ---------------------------------------------------------------------------
def _check_ref_consistency(where, manual_ref, source_ref, errors):
    if not isinstance(source_ref, str) or not source_ref:
        return
    src_set = set(source_ref.split("+"))
    for part in [p.strip() for p in manual_ref.split(";")]:
        ver = part.split(" ")[0] if part else ""
        if ver and ver in SOURCE_REF_VERSIONS and ver not in src_set:
            errors.append(f"{where}: manual_ref version {ver!r} not in source_ref")


def _validate_manual_ref(value):
    """Format + ordering rule for manual_ref.

    Restored from the pre-upgrade validator; must not be weakened.
    """
    if not isinstance(value, str) or not value:
        return "manual_ref must be a non-empty string"
    parts = [p.strip() for p in value.split(";")]
    if not parts or any(not p for p in parts):
        return f"manual_ref has empty segment: {value!r}"
    for part in parts:
        if not MANUAL_REF_SINGLE.match(part):
            return f"manual_ref segment invalid: {part!r}"
    if len(parts) > 1:
        ranks = [ALL_VERSIONS.get(part.split(" ")[0], -1) for part in parts]
        if any(r < 0 for r in ranks):
            return f"manual_ref contains unknown version: {value!r}"
        if ranks != sorted(ranks, reverse=True):
            return f"manual_ref versions must be descending: {value!r}"
    return None


def _validate_support_scope(rec, where, mod_set, errors):
    """Strictly-one-of three-state scope rule.

    Uses the *truthiness* of ``all_modules`` and the *presence* of the
    ``supported_on`` / ``removed_after`` keys, so ``all_modules: false``
    with nothing else is correctly rejected.
    """
    has_all     = bool(rec.get("all_modules"))
    has_list    = rec.get("supported_on") is not None
    has_removed = rec.get("removed_after") is not None

    if sum([has_all, has_list, has_removed]) != 1:
        errors.append(
            f"{where}: exactly one of all_modules/supported_on/removed_after must be set"
        )
        return

    if has_list:
        lst = rec.get("supported_on") or []
        if not lst:
            errors.append(f"{where}: supported_on must not be empty")
        for m in lst:
            if m not in mod_set:
                errors.append(f"{where}: supported_on contains unknown module {m!r}")


def _validate_removed_after(rec, where, errors):
    has_removed = rec.get("removed_after") is not None
    vnotes = rec.get("version_notes") or ""

    if REMOVAL_VERSION_PATTERN.search(vnotes) and not has_removed:
        errors.append(
            f"{where}: version_notes mentions removal but removed_after not set"
        )

    if not has_removed:
        return

    ra = rec["removed_after"]
    if ra not in ALL_VERSIONS:
        errors.append(f"{where}: removed_after={ra!r} unknown")
        return

    if vnotes.strip() == "":
        errors.append(f"{where}: removed_after requires non-empty version_notes")

    src = rec.get("source_ref")
    if isinstance(src, str) and src:
        src_versions = [v for v in src.split("+") if v in SOURCE_REF_VERSIONS]
        if src_versions:
            src_max_rank = max(ALL_VERSIONS[v] for v in src_versions)
            if ALL_VERSIONS[ra] != src_max_rank:
                errors.append(
                    f"{where}: removed_after={ra} must equal highest version in "
                    f"source_ref={src!r}"
                )

    if vnotes.strip() == "":
        return

    m = REMOVAL_VERSION_PATTERN.search(vnotes)
    if not m:
        errors.append(
            f"{where}: removed_after requires version_notes in format "
            f"'Removed in VX.YY'"
        )
        return

    removed_in = m.group(1).upper()
    if removed_in not in ALL_VERSIONS:
        errors.append(
            f"{where}: version_notes mentions unknown version {removed_in!r}"
        )
        return

    versions_sorted = sorted(ALL_VERSIONS, key=lambda v: ALL_VERSIONS[v])
    ra_idx = versions_sorted.index(ra)
    if ra_idx + 1 >= len(versions_sorted):
        errors.append(
            f"{where}: removed_after={ra} is latest known version; "
            f"removal version cannot be determined"
        )
        return
    next_version = versions_sorted[ra_idx + 1]
    if removed_in != next_version:
        errors.append(
            f"{where}: removed_after={ra} implies next version {next_version!r}, "
            f"but version_notes says 'Removed in {removed_in}'"
        )


def _check_urc_removal_consistency(urcs, cmd_by_name, errors):
    for u in urcs:
        enabled = u.get("enabled_by") or []
        if not enabled:
            continue
        enablers = [cmd_by_name[c] for c in enabled if c in cmd_by_name]
        if not enablers:
            continue
        all_removed = all(c.get("removed_after") for c in enablers)
        urc_removed = u.get("removed_after")
        if all_removed and not urc_removed:
            errors.append(
                f"urcs: {u['name']}: all enabled_by commands are removed "
                f"but URC has no removed_after"
            )
            continue
        if urc_removed and not all_removed:
            errors.append(
                f"urcs: {u['name']}: has removed_after but some enabled_by "
                f"command is not removed"
            )
            continue
        if not urc_removed:
            continue
        max_ra = None
        max_rank = -1
        for c in enablers:
            c_ra = c.get("removed_after")
            if not c_ra:
                continue
            r = ALL_VERSIONS.get(c_ra, -1)
            if r > max_rank:
                max_rank = r
                max_ra = c_ra
        if max_ra and urc_removed != max_ra:
            errors.append(
                f"urcs: {u['name']}.removed_after={urc_removed} must equal "
                f"latest enabled_by command's removed_after={max_ra}"
            )


def main() -> int:
    errors = []
    warnings = []

    # 1) Schema validation
    schema_map = {
        "modules.yaml":     "modules.schema.json",
        "categories.yaml":  "categories.schema.json",
        "at_commands.yaml": "at_commands.schema.json",
        "urcs.yaml":        "urcs.schema.json",
    }

    loaded = {}
    for data_file, schema_file in schema_map.items():
        data = load_yaml(data_file)
        schema = load_schema(schema_file)
        validate_schema(data, schema, data_file, errors)
        loaded[data_file] = data

    modules     = loaded["modules.yaml"]
    categories  = loaded["categories.yaml"]
    commands    = loaded["at_commands.yaml"]
    urcs        = loaded["urcs.yaml"]

    # 2) Python-layer rules
    mod_names = [m["name"] for m in modules]
    if len(mod_names) != len(set(mod_names)):
        errors.append("Duplicate module name in modules.yaml")

    cat_ids = [c["id"] for c in categories]
    if len(cat_ids) != len(set(cat_ids)):
        errors.append("Duplicate category id in categories.yaml")

    if len(categories) >= 0xFF:
        errors.append("Too many categories; max 254 allowed.")

    cat_set = set(cat_ids)
    mod_set = set(mod_names)

    cmd_names = []
    for i, c in enumerate(commands):
        where = f"at_commands[{i}] name={c.get('name')!r}"
        name = c.get("name")
        if not name or not isinstance(name, str):
            continue
        cmd_names.append(name)

        if not (name.startswith("AT") or name == "A/" or name == "+++"):
            errors.append(f"{where}: name must start with 'AT' or be 'A/' or '+++'")

        if c.get("category") not in cat_set:
            errors.append(f"{where}: unknown category {c.get('category')!r}")

        if c.get("manual_ref"):
            err = _validate_manual_ref(c["manual_ref"])
            if err:
                errors.append(f"{where}: {err}")

        if c.get("manual_ref") and c.get("source_ref"):
            _check_ref_consistency(where, c["manual_ref"], c["source_ref"], errors)

        _validate_support_scope(c, where, mod_set, errors)
        _validate_removed_after(c, where, errors)

        for u in (c.get("related_urcs") or []):
            if u not in {x["name"] for x in urcs}:
                errors.append(f"{where}: related_urcs references unknown URC {u!r}")

    if len(cmd_names) != len(set(cmd_names)):
        errors.append("Duplicate command name in at_commands.yaml")

    urc_names = []
    for i, u in enumerate(urcs):
        where = f"urcs[{i}] name={u.get('name')!r}"
        name = u.get("name")
        if not name or not isinstance(name, str):
            continue
        urc_names.append(name)

        if not (name.startswith("+") or name.startswith("*") or name[0].isupper()):
            errors.append(f"{where}: URC name must start with '+' or uppercase letter")

        if u.get("category") not in cat_set:
            errors.append(f"{where}: unknown category {u.get('category')!r}")

        if u.get("manual_ref"):
            err = _validate_manual_ref(u["manual_ref"])
            if err:
                errors.append(f"{where}: {err}")

        if u.get("manual_ref") and u.get("source_ref"):
            _check_ref_consistency(where, u["manual_ref"], u["source_ref"], errors)

        _validate_support_scope(u, where, mod_set, errors)
        _validate_removed_after(u, where, errors)

        for e in (u.get("enabled_by") or []):
            if e not in set(cmd_names):
                errors.append(f"{where}: enabled_by references unknown command {e!r}")

    if len(urc_names) != len(set(urc_names)):
        errors.append("Duplicate URC name in urcs.yaml")

    urc_by_name = {u["name"]: u for u in urcs}
    cmd_by_name = {c["name"]: c for c in commands}

    for c in commands:
        cname = c["name"]
        for uname in c.get("related_urcs") or []:
            u = urc_by_name.get(uname)
            if u is None:
                continue
            eb = u.get("enabled_by") or []
            if eb and cname not in eb:
                errors.append(
                    f"two-way: {cname} lists related_urc {uname}, "
                    f"but {uname}.enabled_by does not list {cname}"
                )

    for u in urcs:
        uname = u["name"]
        for cname in u.get("enabled_by") or []:
            c = cmd_by_name.get(cname)
            if c is None:
                continue
            ruc = c.get("related_urcs") or []
            if uname not in ruc:
                errors.append(
                    f"two-way: {uname}.enabled_by lists {cname}, "
                    f"but {cname}.related_urcs does not list {uname}"
                )

    _check_urc_removal_consistency(urcs, cmd_by_name, errors)

    for u in urcs:
        uname = u["name"]
        u_scope = set(mod_names) if u.get("all_modules") else set(u.get("supported_on") or [])
        for cname in u.get("enabled_by") or []:
            c = cmd_by_name.get(cname)
            if c is None:
                continue
            c_scope = set(mod_names) if c.get("all_modules") else set(c.get("supported_on") or [])
            outside = u_scope - c_scope
            if outside:
                warnings.append(
                    f"scope: URC {uname} supported on {sorted(outside)} "
                    f"outside of {cname}.supported_on"
                )

    for w in warnings:
        print(f"WARN: {w}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())