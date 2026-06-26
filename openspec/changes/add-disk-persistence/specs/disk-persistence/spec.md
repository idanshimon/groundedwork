# On-disk persistence

## ADDED Requirements

### Requirement: a built index can be saved and reloaded without re-ingesting
The index MUST support saving to disk and reloading such that a reloaded index produces identical retrieval results to the original without re-ingesting the source documents.

#### Scenario: reload skips re-ingestion
- **WHEN** an index is built, saved to disk, and loaded into a new instance
- **THEN** the loaded instance returns the same hits and scores as the original for any query
- **AND** the source documents are not re-tokenized on load

### Requirement: the on-disk format is cross-language portable
The persisted format MUST be identical across Python and TypeScript so that an index saved by one language loads in the other and produces identical retrieval.

#### Scenario: a Python-saved index loads in TypeScript
- **WHEN** an index is saved by the Python implementation and loaded by the TypeScript implementation
- **THEN** retrieval over the shared fixture produces identical hits and order in both

### Requirement: persistence introduces no runtime dependency or model call
Saving and loading MUST use only standard-library serialization and MUST NOT call any model.

#### Scenario: save and load run with no extra dependency
- **WHEN** `save` and `load` are used on a default install
- **THEN** they succeed using only the language standard library
- **AND** no model is invoked
