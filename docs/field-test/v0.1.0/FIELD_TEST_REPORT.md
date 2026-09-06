# FIELD_TEST_REPORT — CauterRule v0.1.0

**Date:** 2026-09-06  
**Milestone:** M30 — Comprehensive Field Test  
**Scope:** consolidated field-test assessment across deterministic validation, corpus preparation, local OMLX evaluation, cloud OpenRouter evaluation, and product-readiness implications.

---

## BLUF

CauterRule is now a **serious, working system with credible evaluation infrastructure**, but it is **not yet ready for a strong claim of safe autonomous rule learning and promotion in production**.

That is the honest conclusion from the total body of evidence.

This conclusion is not based on a single failed benchmark or a narrow interpretation of one model run. It comes from a broad body of evidence: deterministic test results, Docker and export validation, corpus creation and repair work, local OMLX comparisons, cloud OpenRouter comparisons, and the behavior of the system across both curated and raw corpora. In other words, this report is not saying the product is weak because one model underperformed or because one benchmark number looked bad. It is saying the product has now been tested broadly enough that its real profile is visible.

That profile is nuanced. The product is far more mature than a prototype. It has meaningful depth, real supporting infrastructure, and a field-test process that now produces credible signal. But the product is also not yet at the stage where it has earned a high-confidence “safe autonomous memory loop” claim. The exact reason matters: the product is no longer failing mainly because of missing features or broken mechanics. It is falling short because the remaining unsolved problem is the hardest one: reliably distinguishing rules that are merely plausible from rules that are safe, specific, and worth trusting.

This field-test effort proved several important things at once. First, the product is no longer stuck at the stage where basic plumbing, export formats, corpus setup, redaction, or test infrastructure are the limiting factors. Those areas are in much better shape than they were at the start of the exercise. Second, the extraction benchmark is now meaningfully real: after parser, prompt, result-reset, and timestamp fixes, the system can run full-corpus comparisons across local and cloud models and produce interpretable outputs instead of mostly parser noise. Third, once the benchmark became real, it exposed the actual product problem very clearly: **the hard part is no longer getting a rule-shaped output, but proving that the output is safe, specific, useful, and promotable**.

The strongest reading of the results is this:

- CauterRule is **good at extracting lessons from obvious failures**, especially on `golden`, `failures/positive`, and broad raw extraction sets.
- CauterRule is **not yet strong enough at rejecting bad or overly broad lessons**, especially on `successes`, `failures/negative`, and `nearmiss`.
- The product's current risk is not that it fails to do anything. The risk is that it can do something plausible often enough that a team might trust it too early.

That last point is probably the single most important conclusion in the report. A system that never produces useful output is obviously immature. A system that often produces useful-looking output, but still has weak safety boundaries, is more subtle and more dangerous. CauterRule is clearly in the second category. That is not a reason to dismiss the product. It is a reason to be more disciplined about the kinds of claims the project makes and the kinds of automation it enables next.

That distinction matters. A broken product is easy to diagnose. A product that often appears to work but has weak safety boundaries is much more dangerous. The field test successfully moved CauterRule from the first category out of the second: it is clearly no longer broken, but it still needs more work before it earns high-trust automation claims.

---

## TLDR

The product works. The benchmark works. The corpus now runs. The parser problems were real and were fixed. Local small models are usable for internal regression tracking. Cloud models clearly improve quality and reliability. The strongest cloud model tested, `meta-llama/llama-3.1-8b-instruct`, outperformed every local small model and the cheap cloud baseline on most useful corpora.

But the product is still weak where it matters most for trust:

- avoiding harmful or noisy rule extraction from `successes`
- resisting overgeneralization on `failures/negative`
- maintaining precision on `nearmiss`
- converting “plausible” rules into “promotion-worthy” rules

So the current state is:

- **engineering foundation:** strong
- **evaluation foundation:** strong
- **positive-case extraction:** good
- **negative-case safety:** not good enough yet
- **release claim readiness:** not yet

The shortest honest summary is this: the product can now be taken seriously, but not yet fully trusted.

---

## Does This Meet The PRD?

Not fully.

The field test demonstrates that large parts of the `v0.1.0` scope are real, working, and now credibly evaluated. But it does not yet prove the strongest interpretation of the PRD-level release claim.

That distinction matters because PRD language often compresses two very different things into one sentence: feature scope and quality scope. On feature scope, the product is much further along. The evidence strongly supports that the core system exists, the corpus exists, the export/import layer exists, the runner exists, the evaluation surfaces exist, and the model-comparison workflow is now real. On quality scope, the standard is higher. To say the product truly meets the PRD in a release-ready sense, the field test would need to show not just that the system can extract and evaluate rules, but that it can do so with enough precision and enough safety to justify trust. That second part is where the evidence is still incomplete.

### What the field test demonstrates clearly

The product substantially meets the `v0.1.0` scope on:

- core infrastructure and deterministic validation
- Docker and environment-level validation foundations
- corpus creation, organization, and full-run capability
- rule extraction at scale across both curated and raw corpora
- export/import, redaction, and supporting system behaviors
- meaningful local and cloud model comparison

That is enough to say the product is real, broad, and no longer at prototype-fragility level.

It is also enough to say that CauterRule already has internal value. Even before the strongest release claim is justified, the system has practical use as an engineering memory and evaluation framework. That is not trivial. A lot of experimental systems never get this far. CauterRule has crossed the line into “usable for disciplined internal workflows,” which is a meaningful milestone in itself.

### What the field test does not yet prove

The product does not yet demonstrate PRD-level confidence on:

- safe rule selection
- high-confidence negative-case rejection
- strong near-miss precision
- promotion-quality trust in extracted rules
- enough replay fidelity to support strong autonomous loop claims

So the missing proof is not feature presence. The missing proof is safety, replay trust, and promotion confidence.

This is why the report should not be read as a simple pass/fail on whether the team built what it said it would build. The team did build a substantial amount. The unresolved question is whether the current evidence justifies treating the system as sufficiently trustworthy for the strongest autonomous product story. Right now, it does not.

### Bottom-line PRD judgment

| PRD interpretation | Status | Why |
|---|---|---|
| `v0.1.0` implementation breadth | **Mostly met** | the system, corpus, runner, exports, tests, and benchmark surfaces are substantially implemented |
| `v0.1.0` product-quality and safety claim | **Not yet met** | the field test still shows meaningful weakness on `successes`, `failures/negative`, and `nearmiss` |

Best interpretation:

> `v0.1.0` scope is substantially implemented, but not fully validated to PRD standard.  
> The product has breadth, but it does not yet have enough safety evidence.

If the team wanted to be aggressive, it could argue that `v0.1.0` is already a successful implementation milestone. That would not be unreasonable. But if the team wants to be rigorous, especially in a release-readiness or externally shareable sense, the more honest framing is that `v0.1.0` is substantially built and substantially tested, but still under-validated on the dimensions that matter most for trust.

### Are The Remaining PRD Gaps Missing Features Or Missing Proof?

Mostly missing proof, not missing breadth.

That is a crucial distinction. At this point in the project, it would be misleading to say the product is mainly blocked because the team failed to implement the system. Most of the major surfaces now exist: corpus infrastructure, runners, exports, local/cloud execution paths, and broad extraction flows are all present. The stronger blocker is that the current field test still does not prove the system is safe and precise enough to justify the strongest release claim.

#### What is mostly already built

- corpus infrastructure
- benchmark runner
- local and cloud execution paths
- export/import surfaces
- redaction and supporting validation
- broad extraction loop infrastructure

#### What is still partly a functionality gap

- stronger replay and matcher calibration
- better pre-run corpus/provider validation
- stronger promotion gating logic
- better rule-quality adjudication support

These are real engineering tasks, but they are not the whole story.

#### What is mainly a proof / quality / trust gap

- proving that extracted rules are safe enough on `successes`
- proving that bad candidates are reliably rejected on `failures/negative`
- proving that trigger precision is strong enough on `nearmiss`
- proving that replay outcomes correlate well enough with actual rule quality
- proving that a meaningful subset of extracted candidates are truly promotion-worthy

So the most accurate interpretation is:

> The product is not mainly blocked by missing breadth of implementation.  
> It is mainly blocked by incomplete evidence of safety, replay trust, promotion confidence, and release-grade validation.

---

## Key Points

1. The field-test infrastructure is now credible. Earlier low scores were partly contaminated by parser, prompt, and result-file issues. Those problems were fixed and rerun.
2. The full currently-available corpus is now runnable end to end.
3. Local OMLX models are now good enough to support broad internal corpus evaluation.
4. Cloud models are still useful, not because local runs are impossible anymore, but because cloud models give a better estimate of the product's current quality ceiling.
5. The strongest tested cloud model in this batch was `meta-llama/llama-3.1-8b-instruct`.
6. The product's main remaining weakness is no longer formatting. It is replay quality, rule specificity, and safety.
7. The benchmark is now telling the truth more clearly: CauterRule can extract many plausible rules, but it still lacks enough safety evidence to justify strong autonomous promotion claims.

8. The project's biggest success in this field test was not a single benchmark score. It was turning the evaluation harness into something trustworthy enough that the remaining weak spots now point to the product, not to the test rig.

---

## Observations

### 1. The field test succeeded as an investigation, even if the product did not fully “pass” in a release-gate sense

There is an important distinction between a successful field-test process and a successful product outcome. The field-test process succeeded because it forced the system through realistic comparisons, exposed tooling defects, revealed corpus issues, validated that fixes improved the signal, and produced a coherent view of the remaining problems. That is exactly what a serious field test should do.

The product outcome is more mixed. CauterRule is not failing in a primitive way anymore. It can extract candidates broadly, it can compare models meaningfully, and it has enough infrastructure to support disciplined iteration. But the release-grade question is not “can it produce rules?” The release-grade question is “can it produce rules that are safe enough to trust?” On that question, the answer today is still incomplete.

This is actually a healthy stage for the project to be in. Many systems fail to get far enough for the real question to become visible. CauterRule has progressed to the point where the team is now arguing about safety, calibration, and promotion trust rather than basic viability. That is evidence of progress, even if it is not yet evidence of completion.

### 2. The biggest early problems were in the benchmark itself, and fixing them materially changed the story

The early benchmark picture overstated local-model weakness because several non-model defects were distorting results:

- same-day result-file contamination
- parser sensitivity to trailing commentary
- strict blank-context rejection
- weak prompt specificity
- raw timestamp gaps in some corpora

Once those were fixed, local models became far more usable and cloud comparisons became far more meaningful. This means the project avoided a classic benchmark failure mode: incorrectly blaming the model for problems caused by the evaluation harness.

That is an important credibility win. It means later conclusions in this report are stronger than early impressions would have been. The project now has the right to talk about model quality and product quality with much more confidence, because the benchmark itself became far less distorted.

### 3. The product is strongest on obvious positive cases and weakest on safety-sensitive cases

This is the clearest recurring pattern in both the local and cloud reports.

The product does relatively well when:

- there is a clear failure signature
- the lesson is concrete and actionable
- the trajectory strongly points to a reusable next action

The product is weakest when:

- the trajectory is actually a success and should not become a rule
- the case is a near-miss and should not over-trigger
- the trajectory is a negative/control case and should be rejected

That means the central product challenge has become **precision and restraint**, not recall.

This is exactly the kind of challenge one would expect from a product like CauterRule. Extracting an actionable lesson from a clear failure is the easier half of the problem. Knowing when not to extract, or when not to trust the extracted abstraction, is the harder half. The field test makes it clear that the product is now entering that harder half.

### 4. Cloud models are useful, but not because the local system is unusable

Before the fixes, it would have been fair to say cloud models were needed just to get a readable benchmark. That is no longer true. After the fixes, local OMLX runs are good enough for broad internal comparison and regression tracking.

Cloud models remain useful for a different reason: they reveal the quality ceiling more clearly. They show what happens when formatting and instruction-following are no longer major confounders. In this report, that made one thing obvious: **better models improve extraction quality, but they do not erase the product's safety and replay problems**.

That is exactly why the cloud comparison mattered. If cloud models had solved everything, the conclusion would have been “the product is fine; just use a better model.” That is not what happened. The cloud runs improved a lot, but they still surfaced safety and replay problems. That means the product itself still has meaningful work left, independent of model upgrades.

### 5. The benchmark now exposes the real product problem: judgment quality

At the start of this effort, the most visible failures were parser and asset issues. At the end of this effort, those are no longer central. The visible remaining weakness is judgment quality:

- is the trigger too broad?
- is the directive specific enough?
- does the replay logic correctly interpret the candidate?
- does the product avoid extracting from cases where it should remain silent?

That is a much healthier place to be. It means the project can now spend engineering time on product semantics instead of plumbing.

It also means future progress will be harder won. Plumbing fixes often produce dramatic gains. Judgment-quality improvements usually require more careful scoring, better matcher design, improved negative-case handling, and better human-calibrated evaluation. The project is leaving the easy gains behind and entering the more important work.

### 6. The product is not bad, but it is not yet high-trust

The right phrasing here is important. CauterRule is not a bad product. It has real infrastructure, real corpus discipline, real comparative evaluation, and clear signs of value. But it is not yet a product that has earned a strong, safety-forward autonomy claim. The field test suggests the product is **promising and useful**, not yet **finished and trustworthy by default**.

This should influence how the team positions the product. The honest story today is not “we have solved autonomous rule learning.” The honest story is “we have built a serious system, we can evaluate it credibly, we know what it does well, and we know exactly where it still needs to improve before high-trust deployment.” That is a good story, but it is different from a triumphalist one.

---

## Learnings

1. **Parser and prompt quality dramatically affect benchmark truthfulness.** The earlier benchmark could have led to the wrong product conclusions if those issues had not been fixed.
2. **Local small models are more valuable than they first appeared.** After the fixes, they became useful for full internal corpus evaluation.
3. **Cloud models are still worth running.** They do not just improve formatting; they produce a clearer upper bound on current extraction quality.
4. **Safety corpora are the true release gate.** `successes`, `failures/negative`, and `nearmiss` matter more than broad positive-case extraction.
5. **Replay quality is now the main technical bottleneck.** Parsing is largely under control; decision quality is not.
6. **Provider availability and corpus validation must be treated as first-class operational checks.** Failed provider endpoints and malformed corpus assets waste real testing time.
7. **A plausible extracted rule is not the same as a good product outcome.** Promotion-quality claims need stronger evidence than “the model produced something useful-looking.”

---

## Takeaways

- CauterRule has crossed the threshold from fragile prototype to credible system.
- The field-test framework is now strong enough to support real iteration and comparison.
- The benchmark is now mostly measuring product quality rather than parser accidents.
- Stronger models help, but they do not hide the product's remaining safety weaknesses.
- The next major product milestone should be about safe rule selection and replay trust, not extraction formatting.

---

## Model Comparisons

The model comparison story is one of the most important outputs of this field test. The results are not just about which model “won.” They show which models are useful for which purpose, and they also show which weaknesses belong to the product rather than to the model.

At a high level:

- local OMLX 3B-4B models are now usable for internal evaluation and regression tracking
- cloud models are stronger and more stable overall
- the best cloud model tested was `meta-llama/llama-3.1-8b-instruct`
- even the strongest tested model did not solve the safety problem on its own

### Model By Model

#### `omlx-openai-Llama-3.2-3B-Instruct-4bit`

This is the best “small local cheap” model in the current setup. After the parser and prompt fixes, it became much more capable than the earlier benchmark suggested. It handled the curated corpus cleanly enough to become a real internal benchmark tool, especially for `golden` and `failures/positive`.

Where it performed well:

- fast execution
- low-cost repeated runs
- decent curated positive-case extraction
- useful internal regression baseline

Where it remained weak:

- safety-sensitive corpora
- replay reliability on broad raw corpora
- overgeneralization control

Verdict: good default local smoke/regression model, not a sufficient trust model.

#### `omlx-openai-Qwen3-4B-Instruct-2507-4bit`

This model improved substantially after the fixes and was stronger than the local Llama model on some breadth-oriented raw sets and on some curated precision-adjacent corpora. But it was also slower and did not consistently outperform Llama enough to displace it as the best practical local default.

Where it performed well:

- broad raw synthetic handling
- decent general internal comparison model
- stronger than expected after the parser fixes

Where it remained weak:

- speed relative to local Llama
- still mixed quality on safety corpora
- not obviously strong enough to justify replacing the simpler local default

Verdict: useful second local comparator, not the best primary local choice.

#### `openai/gpt-4o-mini`

This was the cheapest stable cloud baseline and behaved exactly like a useful baseline should. It was consistent, parse-stable, relatively fast, and cheap enough to run broadly. It did not dominate every corpus, but it gave the project a clean reference point for “what a reliable low-cost cloud run looks like.”

Where it performed well:

- perfect parse stability in this batch
- fast cloud turnaround
- stable benchmark behavior
- useful `golden` and `failures/positive` performance

Where it remained weak:

- still poor on safety corpora
- not the strongest quality model in the cloud batch

Verdict: best cheap cloud baseline.

#### `meta-llama/llama-3.1-8b-instruct`

This was the strongest cost-effective model tested in the whole field test. It had near-perfect parse stability, outperformed `gpt-4o-mini` on many of the most useful corpora, and produced the strongest broad benchmark signal overall.

Where it performed well:

- strongest `failures/positive` result
- strongest `golden` result among working cloud models
- strongest `noisy` result
- strongest raw `opencode` and `cross-session` results

Where it remained weak:

- still not strong enough to eliminate safety failures
- still dependent on replay quality for final judgments

Verdict: best current cost/performance benchmark model.

### OMLX Vs Cloud

This comparison is now much clearer than it was before the fixes.

What OMLX models are good for:

- cheap, frequent regression tracking
- validating benchmark plumbing locally
- catching prompt/parser regressions quickly
- broad internal iteration without cloud spend

What cloud models add beyond OMLX:

- stronger curated benchmark performance
- more consistent candidate usefulness
- cleaner evidence for “quality ceiling” analysis
- stronger confidence for shareable benchmark claims

What both local and cloud models still struggle with:

- `successes`
- `failures/negative`
- `nearmiss`
- translating plausible outputs into clearly promotable rules

That last point matters most: the remaining problem is not simply that local models are weak. Even cloud models still expose a product-level safety and replay problem.

### Model Ranking

For the current field-test setup, the practical ranking is:

1. **Best overall benchmark model:** `meta-llama/llama-3.1-8b-instruct`
2. **Best cheap cloud baseline:** `openai/gpt-4o-mini`
3. **Best local default:** `omlx-openai-Llama-3.2-3B-Instruct-4bit`
4. **Best secondary local comparator:** `omlx-openai-Qwen3-4B-Instruct-2507-4bit`

Removed / not recommended:

- `Qwen3.5-4B-4bit` — too slow for practical batch work
- `google/gemini-2.0-flash-001` — unavailable on the tested OpenRouter tier

---

## What Worked Well

### The system foundation

The deterministic and hermetic parts of the product performed well. Existing test results, Docker validation, export/import coverage, redaction coverage, and performance baselines all indicate a strong engineering foundation. That matters because it means the project is not trying to evaluate model behavior on top of a shaky application core.

That foundation deserves real credit. One of the easiest ways to make a field test noisy is to have a weak substrate: unstable commands, poorly defined formats, brittle serialization, or inconsistent environment behavior. CauterRule mostly avoided that. The stronger the substrate, the more trustworthy the downstream evaluation becomes.

### The field-test runner and corpus structure

Once fixed, the field-test runner became a meaningful asset. The corpus can now be run across multiple models, result files are isolated more cleanly, and the outputs are rich enough to support diagnosis. This is a real project capability, not just an experiment.

That is strategically important. It means future iterations can accumulate knowledge rather than rediscovering the same benchmark setup problems every time. A working runner plus a stable corpus is a compounding asset.

### The parser, prompt, and timestamp fixes

These changes had direct measurable value. They moved the benchmark from “mostly noise” toward “mostly signal.” That was one of the most important achievements of the whole effort.

It is worth saying explicitly that this was not cosmetic cleanup. These fixes changed the meaning of the results. Without them, the project risked underestimating local-model value, overestimating parser fragility, and drawing the wrong product conclusions.

### Model comparison breadth

The project now has meaningful evidence across:

- two local small models
- one cheap stable cloud baseline
- one stronger cheap cloud/open-weight comparator

That is enough to reason about product behavior instead of guessing.

That breadth makes the current report much more credible than a single-model narrative would have been. The conclusions here are not driven by one provider, one runtime, or one lucky run.

---

## What Didn't Go Right

### The early benchmark overstated product weakness

The benchmark was initially compromised by toolchain issues. This delayed clear insight and risked misattributing failures to models rather than the evaluation contract.

That matters because a weak benchmark can damage product decision-making. It can send a team after the wrong fix, discourage useful model paths, or produce fake confidence in the wrong direction. The fact that this was caught and corrected is good, but it still cost time and interpretive clarity.

### Some model candidates were operationally unusable

- `Qwen3.5-4B-4bit` was too slow to be practical
- `google/gemini-2.0-flash-001` was unavailable on the OpenRouter tier

This is not catastrophic, but it shows that model selection needs an operational screen before full sweeps.

In other words, not every model failure is a product signal. Some are simply deployment or availability problems. The report needs to separate those cleanly so they do not pollute the product conclusions.

### The product still struggles where trust matters most

Even the stronger cloud models are not obviously safe enough on:

- `successes`
- `failures/negative`
- `nearmiss`

This is the most important “what went wrong” item in the whole report.

It is also the one that most directly blocks a strong release claim. If these corpora were strong, the rest of the weaknesses would feel more manageable. Because these corpora are still weak, they dominate the risk picture.

### Raw breadth still exceeds replay clarity

The raw corpora are useful, but broad sets like `raw/ci` generate many inconclusive results. That means the product can process them, but the benchmark does not yet turn that processing into consistently actionable quality signals.

This should temper how much weight raw breadth is given in any external narrative. Broad processing coverage is good, but if it mostly yields inconclusive judgments, it is not yet the strongest evidence of product trustworthiness.

---

## Focus Areas For Next Time

1. **Replay and matcher calibration**
   This is now the highest-value engineering target.

2. **Safety-first quality gates**
   Promote only when `successes`, `failures/negative`, and `nearmiss` support the claim.

3. **Human-reviewed rule quality sampling**
   Add a human check to compare replay judgment against actual rule usefulness.

4. **Provider and corpus preflight checks**
   Fail fast before expensive runs.

5. **Explicit success criteria for field-test pass/fail**
   The product now needs sharper, safety-centered thresholds.

This list matters because it marks the transition from “make the benchmark work” to “make the benchmark enforce the right product standards.” The next iteration should be less about enabling comparison and more about defining what quality bar the product must actually clear.

### Gaps We Need To Close

These are the specific gaps between the current field-test outcome and a stronger `v0.1.0` release-quality claim.

1. **Safety gap**
   The system still performs too weakly on `successes`, `failures/negative`, and `nearmiss`.

2. **Replay-trust gap**
   The matcher and replay engine still produce too many inconclusive or weakly discriminated results, especially on raw corpora.

3. **Promotion-confidence gap**
   The benchmark shows many plausible candidates, but not enough evidence yet that those candidates are consistently safe to promote.

4. **Human-judgment gap**
   The current report still leans on replay heuristics more than human-reviewed rule quality.

5. **Release-criteria gap**
   The field test does not yet have explicit, enforced pass/fail thresholds tied to the safety-sensitive corpora.

6. **Operational-comparison gap**
   We now know which models are promising, but we still need a crisper release benchmark policy for which model class qualifies as authoritative evidence.

These gaps are not all equal. The first three are the real release blockers:

- safety gap
- replay-trust gap
- promotion-confidence gap

The others matter, but those first three define whether the product can honestly claim `v0.1.0` field-test success in the strongest sense.

---

## Conclusions

CauterRule is in a materially better place than it was at the start of this effort.

It now has:

- a reusable corpus layout
- a functioning comparative runner
- validated deterministic foundations
- meaningful local-model evidence
- meaningful cloud-model evidence
- a much clearer picture of where the real product problems live

That is real progress.

At the same time, a strict reading of the field-test objective says the system is not yet fully there. The objective was not just to extract rules, but to show that the full loop is safe, reliable, and strong enough for production confidence. The results do not yet justify that strongest version of the claim.

So the correct conclusion is:

- **The field-test program was successful.**
- **The product improved materially.**
- **The product is not yet fully field-test complete by a strict release gate.**

That is a good outcome for an honest engineering report.

It is also a strategically useful outcome. The team now has a much sharper map of the work ahead. That is better than an ambiguous “maybe it passed” result and better than a false positive success story. The report now supports disciplined prioritization: replay and safety first, trust claims second, polish later.

If the project were forced to ship something now, the honest posture would be to present CauterRule as a strong experimental or internal-facing system with credible evidence of utility, but not as a system that has already earned robust autonomous safety claims. That is the mature conclusion.

---

## Other Miscellaneous Items

- The product now supports a much stronger reporting trail than before.
- The local and cloud reports are both shareable and reproducible.
- The failed Gemini run was still operationally useful because it established that provider availability checks are necessary.
- The local-vs-cloud contrast is now credible enough to guide future model strategy instead of intuition.

- The existence of both a local-model report and a cloud-model report is itself a project asset. It gives future work a baseline not just for “did the code change?” but for “did the product meaningfully improve?”

---

## Data Appendix

Everything below is supporting evidence. It is intentionally pushed down so the report reads as an assessment first and a benchmark notebook second.

### Corpus and model scope

| Category | Corpus |
|---|---|
| Curated | `golden`, `failures/positive`, `failures/negative`, `successes`, `nearmiss`, `noisy`, `corrections` |
| Raw | `raw/opencode`, `raw/synthetic`, `raw/ci`, `raw/sibling-repos`, `raw/corrections`, `raw/cross-session` |

| Type | Model |
|---|---|
| Local OMLX | `omlx-openai-Llama-3.2-3B-Instruct-4bit` |
| Local OMLX | `omlx-openai-Qwen3-4B-Instruct-2507-4bit` |
| Cloud OpenRouter | `openai/gpt-4o-mini` |
| Cloud OpenRouter | `meta-llama/llama-3.1-8b-instruct` |

### Deterministic system quality

From the existing field-test summary:

- 844+ deterministic tests passing
- 104/104 Docker tests passing
- export/import validation passing
- redaction validation passing
- gold-family validation passing
- performance baselines within threshold

### Model totals

| Model | Type | Total rows | Total candidates | Pass | Inconclusive | Fail |
|---|---|---:|---:|---:|---:|---:|
| `omlx-openai-Llama-3.2-3B-Instruct-4bit` | local | 393 | 379 | 72 | 189 | 118 |
| `omlx-openai-Qwen3-4B-Instruct-2507-4bit` | local | 373 | 373 | 93 | 209 | 71 |
| `openai/gpt-4o-mini` | cloud | 394 | 394 | 77 | 248 | 69 |
| `meta-llama/llama-3.1-8b-instruct` | cloud | 394 | 392 | 123 | 168 | 101 |

### Curated corpus results

| Model | golden | failures/positive | failures/negative | successes | nearmiss | noisy | corrections |
|---|---|---|---|---|---|---|---|
| Local Llama 3.2B | 8P / 2F | 15P / 3I / 12F | 1P / 2I / 5F | 1P / 16I / 2F | 4P / 4I / 6F | 1P / 3I / 1F | 2P / 2I / 1F |
| Local Qwen 4B | 3P / 4I / 3F | 15P / 9I / 6F | 1P / 4I / 5F | 2P / 8I / 10F | 5P / 5I / 4F | 4P / 1I / 0F | 2P / 1I / 2F |
| Cloud GPT-4o-mini | 6P / 4I / 0F | 14P / 13I / 3F | 0P / 4I / 6F | 0P / 6I / 14F | 2P / 4I / 8F | 1P / 3I / 1F | 3P / 2I / 0F |
| Cloud Llama 3.1 8B | 7P / 0I / 3F | 22P / 5I / 3F | 3P / 1I / 6F | 3P / 6I / 11F | 6P / 1I / 7F | 5P / 0I / 0F | 3P / 1I / 1F |

### Raw corpus results

| Model | raw/opencode | raw/synthetic | raw/ci | raw/sibling-repos | raw/corrections | raw/cross-session |
|---|---|---|---|---|---|---|
| Local Llama 3.2B | 13P / 2I / 9F | 18P / 101I / 26F | 8P / 49I / 52F | 0P / 9I / 1F | 2P / 2I / 1F | 2P / 1I / 2F |
| Local Qwen 4B | 13P / 7I / 5F | 36P / 87I / 22F | 9P / 90I / 11F | 0P / 9I / 1F | 3P / 1I / 1F | 1P / 2I / 2F |
| Cloud GPT-4o-mini | 12P / 10I / 3F | 28P / 91I / 26F | 7P / 99I / 4F | 0P / 7I / 3F | 2P / 3I / 0F | 2P / 2I / 1F |
| Cloud Llama 3.1 8B | 18P / 3I / 4F | 38P / 81I / 25F | 11P / 60I / 39F | 0P / 10I / 0F | 3P / 0I / 1F | 4P / 0I / 1F |

### Model recommendations

| Use case | Recommended model |
|---|---|
| Local regression / smoke benchmark | `omlx-openai-Llama-3.2-3B-Instruct-4bit` |
| Secondary local comparator | `omlx-openai-Qwen3-4B-Instruct-2507-4bit` |
| Cheapest stable cloud baseline | `openai/gpt-4o-mini` |
| Stronger cheap cloud benchmark | `meta-llama/llama-3.1-8b-instruct` |

### Source documents

- `docs/field-test/v0.1.0/results-summary.md`
- `docs/field-test/v0.1.0/corpus-local-models-results.md`
- `docs/field-test/v0.1.0/corpus-cloud-llm-results.md`
- `field-test/results/0.1.0/`
