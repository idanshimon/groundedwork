# Core retrieval

## ADDED Requirements

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
