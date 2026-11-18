# 0003. Three verdicts and mandatory human approval

- Status: accepted
- Date: 2026-11-19

## Context

Ruling on truth in an election invites accusations of bias and legal risk. A machine translation or model error broadcast to thousands of voters would damage trust more than silence.

## Decision

Clarion returns only `confirmed`, `contradicted` or `no_official_statement`, and the first two must cite a stored official passage. Nothing is broadcast without an approved review, approved translations for every target language, and an integrity seal. These rules live in `domain/rules.py` and are pinned by `tests/unit/test_rules.py`.

## Consequences

Slower than fully automatic publishing, which we accept. The demo must show the reviewer approval step. Claims about opinions or candidates always resolve to `no_official_statement`.
