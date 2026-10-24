# Verification and traceability

This retrospective baseline describes source main after PR #1 (merge 0eeace067a5857bb834b2d38246121e8e55ad379). No runtime code, fixture, library API or algorithm is changed by this documentation.

## Executed for this spec update

- `openspec validate baseline-playground-experience --strict --no-interactive`: passed.
- `python3 -m unittest discover -s playground/tests -v`: 9 tests passed using the development Python with Playwright installed.
- `python3 bench/parity.py`: 9 cases, 18 hits; Python/TypeScript scores identical to 9 decimal places. No golden regeneration.
- `openspec archive baseline-playground-experience --yes`: synchronized the real canonical specs; archive/post-archive tasks were completed afterward, not marked done prematurely.
- `openspec validate --all --strict --no-interactive` after archive: 10 items passed, 0 failed (7 canonical capabilities and 3 unrelated active changes). The existing MCP, disk and signature-compaction work was not closed or rewritten.

## Requirement evidence

All browser test names below are in `playground/tests/test_playground.py`.

| Requirement | Code and evidence |
|---|---|
| Real adapters/preserved payloads | `build_static.py:analyze`, `index.html:request` and `test_static_adapter_matches_real_python_all_scenarios`; both-adapter scenario test checks every shared field |
| Fail-closed static assembly | `replace_adapter`, `script_json`, build request guard; `test_build_is_offline_deterministic_and_slot_is_fail_closed` and offline-file test |
| Populated honest evidence | `render` and scenario notes; `test_both_adapters_desktop_mobile_controls_and_scenarios` verifies source bodies, exact scores, returned-hit rows, real floor and mismatch explanation |
| Visible run receipt/result reveal | `run({userInitiated})`, `busy`, visible status and receipt; `test_user_runs_have_visible_receipts_and_reveal_results` exercises repeated default, changed Enter query, focus and phone reveal |
| Busy/error state | `busy`, `bounded`, startup timer, `showError`; failure/recovery and missing-engine tests cover visible error/retry and stale-result hiding. Button disabling and running label are additionally code-inspected, not claimed as a separate timing measurement |
| Inert text | textContent/replaceChildren rendering and encoded JSON; hostile-query, hostile-document and build-delimiter tests |
| Narrow/keyboard accessibility | both-adapter desktop/390px scenario test checks overflow, focus/Enter and 44px controls; reduced-motion CSS is code-inspected |
| Companion invitation | `test_walkthrough_is_a_prominent_invitation` checks Watch verb, duration, filled background, SVG and touch height; real href is checked by the existing both-adapter test |
| Bounded grounded boolean | real mismatch query returns pause at 2.9429 with grounded=true; absent France query returns false; parity and exact adapter comparisons retain this behavior |

The companion's own OpenSpec and `walkthrough/tests/playback.test.mjs` live in `idanshimon/groundedwork-demo`; do not copy its runtime requirements into this capability. Earlier live-origin journeys verified 1440/390/320px query/scenario/navigation behavior. They are dated release evidence, not proof of future deployment state.

## Exclusions

This update does not turn unrelated MCP/older-Node library CI failures into passing results. A Markdown validator establishes structure, not runtime behavior or semantic retrieval correctness. Unrelated active changes remain in flight.
