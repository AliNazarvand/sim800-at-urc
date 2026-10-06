# Security Policy

## Scope

This project is a **header-only, compile-time database** of AT Commands and
URCs. It has no runtime component, no network code, no dynamic allocation.

The only impact a vulnerability in this project can have is incorrect data
leading to misbehaviour in a downstream firmware that consumes the
generated headers.

## Reporting

Please report suspected issues (including data-correctness issues) via
GitHub Issues on the upstream repository, or privately via the contact
listed on the maintainer profile.

## Disclosure

We aim to acknowledge reports within 7 days and to publish a fix or
clarification within 30 days when feasible.

## Supported versions

Only the latest published release is supported.