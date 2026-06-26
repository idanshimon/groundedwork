# Core retrieval

## ADDED Requirements

### Requirement: configurable result-set size caps the working set
Retrieval MUST cap the returned working set at a configurable `top_k` (default 3), returning at most that many documents ordered by descending relevance.

#### Scenario: top_k limits the returned documents
- **WHEN** more than `top_k` documents clear the relevance floor for a query
- **THEN** only the `top_k` highest-scoring documents are returned
- **AND** they are ordered by descending BM25 score

#### Scenario: top_k can be overridden per call
- **WHEN** a caller requests retrieval with an explicit `top_k` larger than the default
- **THEN** up to that many floor-clearing documents are returned
