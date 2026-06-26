# Signature compaction

## ADDED Requirements

### Requirement: compact() strips bodies and keeps the signature skeleton
`compact(text, lang)` MUST return the source reduced to imports, class/def signatures, decorators, and docstring first lines, with function and method bodies replaced by a `...` placeholder.

#### Scenario: a Python function is compacted
- **WHEN** `compact("def add(a, b):\n    total = a + b\n    return total", "python")` is called
- **THEN** the result keeps the `def add(a, b):` signature line
- **AND** the body lines are replaced by a single `...` placeholder

#### Scenario: imports are preserved
- **WHEN** a source file beginning with `import os` and `from x import y` is compacted
- **THEN** both import lines appear unchanged in the output

### Requirement: compaction is a pure dependency-free transform
`compact()` MUST NOT call any model, perform any network access, or require any runtime dependency beyond the language standard library.

#### Scenario: no model or network involved
- **WHEN** `compact()` runs in an environment with no network and no API keys
- **THEN** it returns the skeleton successfully using only local computation

### Requirement: compaction output is identical across Python and TypeScript
`compact()` MUST produce byte-identical skeletons in the Python and TypeScript implementations for every case in the shared compaction fixture.

#### Scenario: parity holds on the shared fixture
- **WHEN** the parity harness runs `compact()` over `fixtures/compaction.json` in both languages
- **THEN** the Python and TypeScript outputs are byte-identical for every case
- **AND** `bench/parity.py` reports the compaction results as IDENTICAL
