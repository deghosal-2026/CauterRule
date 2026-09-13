# CauterRule v0.3.1 — Announcements & Article Ideas

**Purpose:** launch content for the v0.3.1 release (#759). Draft/social copy
below can be reused as-is; article outlines are starting points.

---

## Launch announcement (short)

> **CauterRule v0.3.1 is out — the verdict is now trustworthy.**
>
> v0.3.1 is the Accuracy & Trust patch: it fixes the matcher/scorer defects the
> v0.3.0 review found, measures extraction quality directly for the first time,
> and moves the adversarial source-trust gate into production promotion.
>
> Headline field-test result — the first release to clear **every hard quality
> and safety gate** on both models: golden **82–83%**, failures/positive
> **50–52%**, near-miss **0 false accepts**, adversarial **0 promotions**, and
> total pass volume ~**5×** v0.3.0 while safety held flat.
>
> `pip install --upgrade cauterule`
> PyPI: https://pypi.org/project/cauterule/0.3.1/
> Release notes: docs/release/v0.3.1/release-notes.md

## Social posts

- **X / Mastodon:** "v0.3.1 is out: golden pass 30–50% → 82–83%, failures/positive 8–10% → 50–52%, adapters 0/60 → 60/60, 0 adversarial promotions — and extraction accuracy measured directly for the first time. The quality gap was the matcher proxy, not the model. `pip install --upgrade cauterule`"
- **LinkedIn:** "We re-ran our full agent-failure field test after fixing the matcher/scorer. The first release to clear every hard quality and safety gate on both models — 5× the pass volume with 0 adversarial promotions. The lesson: measure extraction directly; a bad proxy will convince you your model is failing."
- **Reddit (r/LocalLLaMA, r/MachineLearning):** "We thought our extractor was bad. It wasn't — our matcher proxy was. After adding an extraction-accuracy metric and fixing the scorer, golden went 30–50% → 82–83% with no model change. v0.3.1 write-up + report."

## Article ideas

1. **"Extraction vs replay: the metric that changed our minds"**
   The v0.3.1 story. v0.3.0 blamed the model for low golden pass; the new
   trigger-only `extraction_agreement` metric showed the model extracted
   correctly (0.74–0.92) while token-F1 under-reported (0.42–0.65). Practical
   lesson: measure the component you actually care about. ~1,200 words.

2. **"Unreachable floors and diluted signatures: why recall was 0.17"**
   Deep dive on #721/#722. A semantic floor no paraphrase could clear plus a
   failure signature diluted by `failure_class` kept recall near zero. Lowering
   the floor to 0.62 against a class-free view roughly doubled it. For anyone
   building replay/eval pipelines.

3. **"The hard part of agent rules is saying no — in production"**
   #727: the adversarial protection that produced "0 promotions" was test-only.
   v0.3.1 moves source-trust taint into `auto_promote` as a hard gate that even
   `force` cannot override. Why test-harness safety ≠ deployed safety.

4. **"43 bugs later: what a full-repo review finds in a shipped system"**
   The v0.3.1 code-review audit — 11 Critical + 32 Important across matcher,
   corpus hashing, promotion gates, MCP auth, pack/export security. A template
   for pre-release audits.

5. **"Field-testing agent infrastructure, take two: 4,742 runs, 40 corpora"**
   Methodology + honest gaps: 0-accepted corpora, llama no-candidates,
   cross-session/human-agreement not yet measured.

## Distribution checklist

- [x] GitHub release published (v0.3.1)
- [x] PyPI 0.3.1 live
- [ ] GitHub Discussion announcement
- [ ] dev.to / Hashnode cross-post of article #1
- [ ] X / Mastodon / LinkedIn announcement
- [ ] Reddit post (appropriate subreddits, no spam)
- [ ] Submit to relevant newsletters (e.g. Python Weekly, TLDR AI)
- [x] README/docs links updated to the v0.3.1 release notes