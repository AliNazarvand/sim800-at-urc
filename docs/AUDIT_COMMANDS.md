# Audit — AT Commands

Manual, per-version comparison of `data/at_commands.yaml` against the
SIM800 Series AT Command Manuals V1.01, V1.10 and V1.12.

## Method

1. Downloaded the three reference PDFs into `.audit_cache/` and
   extracted every `AT+...` token and every section header with
   `tools/audit_pdfs.py` (based on `pdfplumber`).
2. Compared the union of those tokens against the 346 command records
   in `data/at_commands.yaml`.
3. Manually reviewed every candidate that appeared in the PDFs but was
   missing from the YAML, dumping the surrounding pages with ad-hoc
   scripts (removed after the audit concluded).

## Summary

| Category | Count |
|----------|-------|
| Baseline records in YAML | 346 |
| Typos corrected (renamed) | 2 |
| New records added | 0 |
| Referenced-but-not-documented | 3 |
| Non-AT tokens (V.25TER without `AT+` prefix) | 35 |

### 1. Typos corrected

Both commands had dedicated sections in the manuals; only their names
were mis-typed in the YAML.

| Old name in YAML | Correct name in PDF | `manual_ref` after fix |
|------------------|---------------------|------------------------|
| `AT+CEXTERNONE` | `AT+CEXTERNTONE` | `V1.12 §6.2.49; V1.10 §6.2.50; V1.01 §6.2.50` |
| `AT+CHWHTELIST` | `AT+CWHITELIST` | `V1.12 §6.2.51; V1.10 §6.2.52; V1.01 §6.2.52` |

Both were previously single-version `manual_ref` values; they have been
corrected to compound form (three versions) since they appear in all
three manuals.

### 2. Referenced but not documented as dedicated sections

The following commands appear in the manuals only in supporting
context. They were **not** added to the database because the
`manual_ref` format required by `validate.py` needs a real
`§<section>` number, and no dedicated section exists in the three
reference manuals.

| Name | Reference | Reason for exclusion |
|------|-----------|----------------------|
| `AT+CHUP` | V1.10 p.39; V1.12 p.38 (footnote in `ATS0`) | Only mentioned as an alternative to `ATH`; no dedicated section |
| `AT+FSHEX` | V1.10 p.49; V1.12 p.47 (support-matrix entry) | Listed only in the summary table; no dedicated section |
| `AT+FSDRIVE` | V1.10 p.286; V1.12 p.274 (footnote in `AT+FTPGETTOFS`) | Only mentioned as obtaining local drive labels |

Full documentation for `AT+FS*` commands likely lives in a separate
*SIM800 Series File System AT Command Manual*, which is not among the
three reference manuals used by this project.

### 3. Non-AT tokens

The tokens `+++`, `A/`, `AT&C`, `AT&D`, `AT&F`, `AT&V`, `AT&W`,
`AT*CELLLOCK`, `ATA`, `ATD`, `ATD><n>`, `ATD><str>`, `ATDL`, `ATE`,
`ATH`, `ATI`, `ATL`, `ATM`, `ATO`, `ATP`, `ATQ`, `ATS0`, `ATS3`,
`ATS4`, `ATS5`, `ATS6`, `ATS7`, `ATS8`, `ATS10`, `ATT`, `ATV`, `ATX`,
`ATZ` are V.25TER commands that do not carry the `AT+` prefix. They
were flagged as "missing" only because the extraction regex anchored
on `AT\+`. All of them exist in `data/at_commands.yaml` and are
correct.

### 4. Absence of removed records

No record in the three manuals was observed to be present in an
earlier version and removed in a later version, except for the FAX
family (`AT+FCLASS`, `AT+FMI`, `AT+FMM`, `AT+FMR`) which already carry
`removed_after: "V1.01"` and `version_notes: "Removed in V1.02."` in
the YAML.
