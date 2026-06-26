# core-retrieval Specification

## Purpose
BM25 keyword indexing and relevance-floored retrieval, implemented stdlib-only in `python/groundedwork/__init__.py` and `ts/src/index.ts` (k1=1.5, b=0.75, title weighted 2×). The relevance floor (default min_score=0.5) is the load-bearing safety primitive: weak matches are dropped rather than returned, so an off-topic query yields an empty working set instead of distractors. Ranking is validated against the reference rank_bm25 library.
## Requirements
### Requirement: BM25 keyword indexing with title weighting
The index MUST score documents using BM25 with parameters k1=1.5 and b=0.75, weighting the document title twice relative to the body.

#### Scenario: a matching document is scored and ranked
- **WHEN** a query shares significant terms with a document
- **THEN** that document receives a positive BM25 score
- **AND** it is ranked above documents with fewer or no shared terms

#### Scenario: ranking matches the reference implementation
- **WHEN** the same corpus and query are scored by the reference rank_bm25 library
- **THEN** the top-ranked document from groundedwork matches the reference's top-ranked document

### Requirement: relevance floor suppresses weak matches
Retrieval MUST drop documents whose BM25 score falls below the configured relevance floor (default 0.5), returning an empty result when nothing clears the floor.

#### Scenario: a junk query returns nothing
- **WHEN** a query has no meaningful term overlap with any document
- **THEN** the retrieved working set is empty

#### Scenario: a real query returns its matches
- **WHEN** a query strongly matches a document
- **THEN** that document is returned in the working set

### Requirement: retrieval requires no runtime dependency
The core retrieval path MUST operate using only the language standard library, with no third-party runtime dependency and no network access.

#### Scenario: retrieval runs offline with no dependencies
- **WHEN** groundedwork retrieves on a default install with no network
- **THEN** it returns results using only local, standard-library computation

### Requirement: configurable result-set size caps the working set
Retrieval MUST cap the returned working set at a configurable `top_k` (default 3), returning at most that many documents ordered by descending relevance.

#### Scenario: top_k limits the returned documents
- **WHEN** more than `top_k` documents clear the relevance floor for a query
- **THEN** only the `top_k` highest-scoring documents are returned
- **AND** they are ordered by descending BM25 score

#### Scenario: top_k can be overridden per call
- **WHEN** a caller requests retrieval with an explicit `top_k` larger than the default
- **THEN** up to that many floor-clearing documents are returned

