# SIMCom SIM800 Series - AT Command & URC Reference

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Static, header-only C++17 database of AT Commands and URCs for the
SIMCom SIM800 Series module family, targeting ESP32-WROOM-32 firmware.

## Supported Modules

- SIM800L
- SIM800C
- SIM808
- SIM868
- SIM800A
- SIM800F
- SIM800H
- SIM800
- SIM800C-DS

## Architecture

Three layers:

    [YAML sources] --(tools/generate.py)--> [C++17 headers] --> [firmware]

- `data/*.yaml` is the Single Source of Truth. Edit only these.
- `tools/generate.py` turns the YAML into C++17 `inline constexpr`
  headers under `include/sim800_at/`. Never edit the generated headers.
- `include/sim800_at/sim800_at.hpp` is the hand-written umbrella.

Validation combines JSON Schemas (`schemas/`) with Python cross-record
rules in `tools/validate.py`.

## Requirements

- Python 3.10+
- PyYAML, jsonschema, pytest
- CMake 3.16+ and a C++17 toolchain (for host tests)

## Install

    python -m pip install -r requirements.txt

## Usage

    python tools/validate.py
    python tools/generate.py
    pytest tests/
    cmake -S . -B build -DSIM800_AT_BUILD_TESTS=ON
    cmake --build build
    ctest --test-dir build --output-on-failure

Optional data exports (JSON / CSV / Markdown) into `dist/`:

    python tools/generate.py --with-dist

## Minimal example

    #include "sim800_at/sim800_at.hpp"

    const sim800_at::ATCommand* c = sim800_at::find_command("AT+CMGS");
    if (c && sim800_at::is_command_supported(c, "SIM800L")) {
        // ...
    }

## Layout

    .
    |-- data/              YAML sources (Single Source of Truth)
    |-- schemas/           JSON Schemas for the YAML sources
    |-- include/sim800_at/  C++ headers (generated + umbrella)
    |-- tools/             generate / validate scripts
    |-- tests/             host-side tests
    `-- docs/              documentation

## Documentation

- `docs/API.md` — public API reference
- `docs/DATABASE.md` — data model and conventions
- `docs/ARCHITECTURE.md` — design decisions and pipeline
- `CONTRIBUTING.md` — how to add records
- `SECURITY.md` — disclosure policy

## Related Project

- [sim800-at-deltas](https://github.com/AliNazarvand/sim800-at-deltas)
- [sim800-at-urc](https://github.com/AliNazarvand/sim800-at-urc)
- [sim800-capabilities](https://github.com/AliNazarvand/sim800-capabilities)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.