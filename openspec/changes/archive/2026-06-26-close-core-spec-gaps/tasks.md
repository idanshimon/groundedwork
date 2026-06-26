# Tasks — close core-spec gaps

> Documentation of shipped, tested behavior. No code changes. Implementation
> tasks are marked `[x]` because the behavior already exists.

## 1. byom capability
- [x] 1.1 The engine calls no generation model and imports no model SDK (verified: zero runtime dependencies).
- [x] 1.2 The engine holds no API keys / credentials / base_url config (verified: no such config exists).
- [ ] 1.3 Author `specs/byom/spec.md` codifying the guarantee.

## 2. core-retrieval: top_k
- [x] 2.1 `top_k` (default 3) caps the returned working set in both languages (shipped + tested).
- [ ] 2.2 Author the `top_k` ADDED requirement.

## 3. grounding-abstention: custom prompt
- [x] 3.1 A caller-supplied `system_prompt` overrides the default grounding prompt in both languages (shipped + tested by `test_custom_prompt_still_overrides_default`-style cases).
- [ ] 3.2 Author the custom-prompt ADDED requirement.

## 4. Validate + archive
- [ ] 4.1 `openspec validate close-core-spec-gaps --strict` clean.
- [ ] 4.2 Archive so the canonical catalog gains `byom` and the two new requirements; fill any Purpose placeholder.
