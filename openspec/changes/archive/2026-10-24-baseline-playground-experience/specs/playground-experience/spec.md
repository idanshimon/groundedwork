## ADDED Requirements

### Requirement: Real engine adapters and preserved payloads
The playground MUST use the real Python/server or compiled TypeScript/browser engine and preserve the existing query, terms, floor, scored, grounded, hits, messages, stable_prefix, answer and corpus_size fields.

#### Scenario: Shared queries retain their results
- **WHEN** the five synthetic scenarios run through either adapter
- **THEN** shared fields, source identities and ranked scores agree with the real Python analysis
- **AND** no retrieval algorithm or corpus is replaced by UI code

### Requirement: Explicit fail-closed static assembly
The static builder MUST replace exactly one explicit adapter slot, safely encode embedded JSON, embed the actual compiled engine and reject backend requests in generated output.

#### Scenario: Invalid adapter markers cannot produce a release
- **WHEN** markers are missing, duplicated or reversed
- **THEN** the build fails rather than silently shipping a partially rewritten page

#### Scenario: Generated playground works offline
- **WHEN** the static artifact opens without network access
- **THEN** real retrieval works without /api requests or external runtime dependencies

### Requirement: Populated and honest evidence inspection
The playground MUST populate a real default example and display selected source bodies, actual returned-hit scores, the configured floor and the prompt metadata without implying that an LLM was called or relevance was semantically verified.

#### Scenario: Refund example is inspectable on load
- **WHEN** the engine initializes successfully
- **THEN** the refund query returns its real source extract and score
- **AND** prompt and metadata are available behind a disclosure

#### Scenario: Keyword wrong match is not disguised as abstention
- **WHEN** the delivery paraphrase scenario retrieves Pausing Your Subscription above the floor
- **THEN** the UI states that it is a wrong-source example with grounded=true
- **AND** it does not promise that the lexical threshold or optional hybrid retrieval guarantees correctness

#### Scenario: Scores describe only observed results
- **WHEN** ranked evidence is displayed
- **THEN** score bars share one labeled scale with the real floor marker
- **AND** the UI does not invent below-floor documents or scores absent from the engine payload

### Requirement: Visible per-run completion and user-directed results
The playground MUST visibly acknowledge every successful run, including an unchanged default query, with a changing run receipt and selected-document result; it MUST focus the result after an explicit user action and reveal it when offscreen without taking over startup focus or scroll.

#### Scenario: Repeating the preloaded query is perceptible
- **WHEN** the visitor clicks Run query without editing the populated example
- **THEN** the visible completion and result receipt advance to the next run number
- **AND** feedback is not confined to a clipped accessibility-only region

#### Scenario: A phone query reveals its result
- **WHEN** a user submits via the button, Enter or a scenario and the result is outside the useful viewport
- **THEN** the result receives focus and is brought into view

### Requirement: Busy and failed states are explicit
The playground MUST disable conflicting query controls while busy, label the running state and display failed initialization or query outcomes with a bounded wait and an available recovery action.

#### Scenario: The engine does not initialize
- **WHEN** the adapter fails or fails to start within the bounded startup interval
- **THEN** a visible error and Retry connection action replace indefinite waiting

#### Scenario: Query execution fails
- **WHEN** a server or adapter returns an error
- **THEN** the UI displays the error and does not present a stale result as the new outcome
- **AND** the visitor can submit again

### Requirement: Safe text rendering
The playground MUST render query, document and metadata content as inert text and protect inline corpus JSON from HTML script delimiters.

#### Scenario: Hostile text is not executed
- **WHEN** a query or returned document contains an img tag with an event handler
- **THEN** the text is displayed without creating executable markup or triggering the handler

### Requirement: Accessible narrow and desktop operation
The playground MUST support keyboard submission, visible focus, reduced-motion preference, usable touch controls and readable non-overflowing results at phone and desktop widths.

#### Scenario: Keyboard and touch paths remain usable
- **WHEN** visitors operate the five cases, Enter submission and metadata disclosure on a phone or desktop
- **THEN** exact results remain available, controls have at least 44px height and expanded content does not widen the page

### Requirement: Prominent companion invitation
The playground MUST expose the relative walkthrough destination through an unmistakable play-icon action with a watch verb and 30-second duration, rather than only a plain navigation word.

#### Scenario: The visitor discovers the companion
- **WHEN** the visitor views the header on a phone or desktop
- **THEN** the filled Watch walkthrough action is visibly actionable and links to ./walkthrough/
- **AND** the companion can return the visitor to the working playground
