# Hybrid retrieval

## ADDED Requirements

### Requirement: hybrid mode retrieves paraphrased matches the keyword path misses
Hybrid retrieval MUST retrieve the correct document for a query whose words do not overlap the document's words, in cases where the keyword-only path returns the wrong document or abstains.

#### Scenario: a paraphrased query finds the right doc
- **WHEN** hybrid mode is enabled and a query semantically matches a document but shares no significant words with it
- **THEN** that document is retrieved in the working set
- **AND** the keyword-only path on the same query does not retrieve it (establishing the improvement)

### Requirement: hybrid is opt-in and the keyword default stays zero-dependency
Hybrid retrieval MUST be disabled by default, and the keyword-only default MUST function with no embedding backend installed.

#### Scenario: default install has no embedding dependency
- **WHEN** groundedwork is installed without the optional hybrid extra
- **THEN** the keyword retrieval path works unchanged
- **AND** no embedding model or extra dependency is required

### Requirement: the embedding backend is retrieval-side and does not breach BYOM
The embedding backend MUST be used only for retrieval ranking and MUST NOT be used to generate answers, preserving the BYOM boundary that groundedwork never calls a generation model.

#### Scenario: no generation model is invoked
- **WHEN** hybrid retrieval ranks documents using embeddings
- **THEN** only the retrieval-side embedder runs
- **AND** no generation model is called by groundedwork
