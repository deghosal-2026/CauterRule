# CauterRule v0.3.0 — Announcements & Article Ideas

**Purpose:** launch content for the v0.3.0 release (#675). Draft/social copy
below can be reused as-is; article outlines are starting points.

---

## Launch announcement (short)

> **CauterRule v0.3.0 is out.**
> Agents that never make the same mistake twice — now hardened end to end.
>
> v0.3.0 closes the silent-corruption bugs from the v0.2.0 field test, adds
> first-class adapters for **LangGraph, CrewAI, and PydanticAI**, rule
> lifecycle management (specificity, outcomes, supersession, retirement), a
> **pack ecosystem**, and a 40-corpus field test across two cloud models.
>
> Headline safety result: **near-miss precision 98–100%**, **0 adversarial
> promotions**, **100% silence on clean trajectories**.
>
> `pip install --upgrade cauterule`
> PyPI: https://pypi.org/project/cauterule/0.3.0/
> Changelog: CHANGELOG.md

## Social posts

- **X / Mastodon:** "v0.3.0 ships: adapters for LangGraph/CrewAI/PydanticAI, rule lifecycle, packs, and a field test where the safety gate silenced 100% of clean runs and promoted 0 adversarial rules. `pip install --upgrade cauterule` 🚀"
- **LinkedIn:** "We field-tested 40 agent-failure corpora across two models. The hard part isn't extraction — it's knowing when *not* to promote a rule. CauterRule v0.3.0 reduced near-miss false passes from 5–7 to 0–1 per model. Release notes + report in the repo."
- **Reddit (r/LocalLLaMA, r/MachineLearning):** "We built a standing-rule extractor for agent failures and learned unit-green ≠ deployment-safe. A Docker field test caught an MCP auth guard that never ran. Write-up + v0.3.0 release."

## Article ideas

1. **"Unit-green, deployment-broken: the MCP auth bug that shipped through CI"**
   Narrative on #601 — a package import swallowed by a blanket `try/except`
   made every HTTP request look like local stdio. Lesson: test the deployed
   artifact, not just the class. ~1,200 words.

2. **"The hard part of agent rules is saying no"**
   Why safety (silence on clean trajectories, adversarial overrides, near-miss
   penalties) matters more than extraction quality, and how v0.3.0 measures it.
   Include the 5/7 gate table.

3. **"Domain-scoped replay: why recall was near-zero and how we fixed it"**
   Deep dive on #708. Testing candidates against an undifferentiated 230-item
   pool made recall ~0.05; scoping references to the source domain gave a 2–3×
   improvement. Practical lesson for anyone building replay/eval pipelines.

4. **"Building framework adapters that don't leak secrets"**
   The adapter conformance kit: one contract (fail-twice → extract → inject →
   no-repeat) plus redaction-on-disk, applied to generic `@watch`/`inject`,
   LangGraph, CrewAI, and PydanticAI.

5. **"A pack ecosystem for agent rules: semver, certification, supply chain"**
   How pack install/create/publish + safety certification work, and why
   checksums + provenance matter for shared agent behavior.

6. **"Field-testing agent infrastructure: 4,768 runs, 40 corpora, 2 models"**
   Methodology post — what we measured, what broke, what the data said (and
   what it didn't). Honest about the golden/failures-positive gap.

## Distribution checklist

- [ ] GitHub release published (v0.3.0)
- [ ] PyPI 0.3.0 live
- [ ] dev.to / Hashnode cross-post of article #1
- [ ] X / Mastodon / LinkedIn announcement
- [ ] Reddit post (appropriate subreddits, no spam)
- [ ] Submit to relevant newsletters (e.g. Python Weekly, TLDR AI)
- [ ] Update README/docs links to the release notes
