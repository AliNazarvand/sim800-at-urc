# SIMCom SIM800 Series - AT Command & URC Reference

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

## Requirements

- Python 3.10+
- PyYAML
- CMake 3.16+ and a C++17 toolchain (for host tests)

## Install

    python -m pip install pyyaml

## Usage

    python tools/validate.py
    python tools/generate.py
    cmake -S . -B build
    cmake --build build
    ctest --test-dir build --output-on-failure

## Minimal example

    #include "sim800_at/sim800_at.hpp"

    const sim800_at::ATCommand* c = sim800_at::find_command("AT+CMGS");
    if (c && sim800_at::is_command_supported(c, "SIM800L")) {
        // ...
    }

## Layout

    .
    |-- data/              YAML sources (Single Source of Truth)
    |-- include/sim800_at/  C++ headers (generated + umbrella)
    |-- tools/             generate / validate scripts
    |-- tests/             host-side tests
    `-- docs/              documentation

## Related Project

- [sim800-at-deltas](https://github.com/AliNazarvand/sim800-at-deltas) — per-module hardware and AT differences for the same module family.

