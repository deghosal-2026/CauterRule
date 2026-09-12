# PRD 07: Success Metrics

## BLUF

`v0.1.0` is successful if CauterRule can do four things convincingly: extract useful rules from failures, reject bad rules before promotion, measurably reduce repeat failures, and make that improvement visible through demos, reports, and benchmarks. Because `v0.1.0` now includes replay, corpus, scale, safety, and ecosystem surface area, success metrics must cover product usefulness, technical correctness, operational performance, and OSS adoption.

## Metric Categories

| Category | What it answers |
|----------|-----------------|
| **Learning Quality** | Are extracted rules actually good? |
| **Behavior Improvement** | Does the agent repeat failures less often? |
| **Replay & Benchmark Quality** | Is the evaluation harness trustworthy? |
| **Performance & Scale** | Can `v0.1.0` handle realistic local workloads? |
| **Safety & Hygiene** | Does the system avoid promoting bad or unsafe rules? |
| **Developer Experience** | Can a user see value quickly and operate the tool easily? |
| **OSS Traction** | Is the project interesting enough to attract users and contributors? |

## Primary Metrics

| Metric | Target for v0.1.0 | How to Measure |
|--------|-------------------|----------------|
| Rules extracted, tested, promoted per week | >= 5/week on active use | Rule store git log |
| Replay precision | >= 90% | % of promoted rules that help without breaking prior successes |
| Repeat-failure rate | <= 10% recurrence for covered failure classes | Compare post-promotion failures against historical repeats |
| Time from failure to rule promotion | < 5 minutes in auto mode | Timestamps in provenance |
| Promotion precision in live use | >= 80% | % of promoted rules later observed helping in real runs |
| Failure-to-prevention conversion | >= 30% | % of distinct recurring failure classes that end up with at least one validated rule |
| Demo time-to-wow | <= 5 minutes | Time from install to successful `cauterule demo` run |
| Cold-start time to first useful rule | <= 30 minutes | Time from zero-rule state to first promoted rule that later prevents a repeated failure |

## Learning Quality Metrics

| Metric | Target for v0.1.0 | How to Measure |
|--------|-------------------|----------------|
| Candidate validity rate | >= 85% | % of extracted candidates that parse into valid `when X, do Y` structure |
| False lesson rate | <= 20% | % of candidates that sound plausible but fail replay |
| Multi-pass win rate | >= 15% better than single-pass baseline | Compare best-of-3 extraction against single extraction replay pass rate |
| Rule specificity quality | >= 80% acceptable | Human or benchmark scoring of whether promoted rules are neither too vague nor too narrow |
| Human correction conversion rate | >= 75% | % of human corrections successfully converted into testable rule candidates |
| Draft tournament usefulness | >= 60% | % of cases where ranked multi-draft output is judged better than first draft alone |
| Extractor stability | <= 20% major variance on repeat extraction | Re-run extraction on same trajectory and compare candidate consistency |

## Behavior Improvement Metrics

| Metric | Target for v0.1.0 | How to Measure |
|--------|-------------------|----------------|
| Repeat-failure suppression rate | >= 50% reduction for covered classes | Compare pre-rule and post-rule recurrence |
| Rule hit usefulness rate | >= 70% | % of injected rules judged relevant or helpful during the run |
| Missed-rule rate | <= 15% | % of runs where a useful existing rule should have been injected but was not |
| Failure class coverage | >= 40% of recurring classes covered | Count recurring classes with at least one validated active rule |
| Coverage gap detection accuracy | >= 80% | Human review of whether surfaced gaps correspond to real missing coverage |
| Counterfactual prevention estimate quality | Directionally correct in >= 80% of sampled cases | Compare `cauterule counterfactual` estimates to manual inspection |

## Replay & Benchmark Metrics

| Metric | Target for v0.1.0 | How to Measure |
|--------|-------------------|----------------|
| Replay determinism | 100% deterministic on same inputs | Same candidate + same corpus must produce same verdict |
| Gold-family acceptance rate | >= 85% | % of benchmark candidates that fall into acceptable gold rule families |
| Counterexample rejection rate | >= 90% | % of counterexample scenarios where bad rules are correctly rejected |
| Near-miss precision | >= 90% | % of near-miss scenarios where non-applicable rules do not fire |
| Success-regression catch rate | >= 95% | % of rules that would break prior successes and are caught by replay |
| Corpus annotation completeness | 100% for public corpus | Every benchmark trajectory has required metadata and labels |
| Regression benchmark pass rate | 100% for release | All release-blocking benchmark suites pass before cut |

## Field Test Metrics

| Metric | Target for v0.1.0 | How to Measure |
|--------|-------------------|----------------|
| Single-agent coding field test improvement | Visible reduction in repeated coding failures | Before/after field test report |
| Cross-session persistence | 100% in sampled tests | Promoted rule still applies correctly in later fresh sessions |
| Noisy trajectory resilience | >= 75% extraction quality retained | Compare clean vs noisy trajectory benchmark outcomes |
| Human-review acceptance rate | 50-80% | % of replay-passing candidates accepted by human operator |
| Auto vs human promotion agreement | >= 80% | Compare auto-promote verdicts with human review decisions |
| Cold-start bundled-pack usefulness | >= 1 prevented failure within first session | Field test with bundled `pack-git` |

## v0.3.0 Field Test Metrics (2026-09-12)

Scope: 40 corpora × 2 cloud models (gpt-4o-mini, llama-3.1-8b), 4,768 trajectory-runs, 444-trajectory domain-scoped reference pool. Full report: [`docs/field-test/v0.3.0/FIELD_TEST_REPORT.md`](../../field-test/v0.3.0/FIELD_TEST_REPORT.md).

| Metric | v0.3.0 Result | Target | Notes |
|--------|---------------|--------|-------|
| Near-miss precision | 98–100% (was 86–90%) | >= 90% | Near-miss penalty + self-match exclusion + recovery gate |
| Adversarial promotions | 0 (was 2–4 pre-fix) | 0 | `should_reject` override (#714), model-independent |
| Safety silence | 100% (60/60 successes, 60/60 negatives) | 100% | Pre-extraction gate drops clean trajectories |
| Recall | 0.170–0.228 (was 0.087) | — | 2–3× improvement via domain-scoped reference pool (#708) |
| Golden pass rate | 40–50% | >= 70% | Not met — matcher paraphrase gap |
| Failures/positive pass rate | 8–10% | >= 50% | Not met — broad-trigger penalty + matcher gap |
| Curated inconclusive rate | ~75% | < 15% | Not met — matcher paraphrase limitation |
| Generic triggers | 0.7% | < 10% | Met |

### Safety-Adjusted Ranking

Candidates are ranked safety-first: near-miss precision, adversarial rejection, and success-regression evidence come before recall/golden usefulness. A high-recall rule that touches a near-miss reference or breaks a success is demoted before it can outrank a safe rule. This ordering is what keeps the safety metrics above from being traded away for pass-rate gains.

### Release Gate Verdict (v0.3.0): 5/7

| Gate | Status |
|------|--------|
| Safety: 100% silence on successes/negatives | Met |
| Near-miss precision >= 90% | Met (98–100%) |
| Generic triggers < 10% | Met (0.7%) |
| Adversarial: 0 promoted rules | Met |
| Infrastructure (preflight, harness health, cost corpus, Docker, measurement tooling) | Met |
| Golden pass rate >= 70% | Not met (40–50%) |
| Failures/positive pass rate >= 50% | Not met (8–10%) |
| Curated inconclusive < 15% | Not met (~75%) |

Safety + adversarial + specificity + infrastructure pass; extraction quality is the holdout. Carry-over themes (matcher paraphrase bridging / semantic weight, cross-session measurement, human agreement, OpenSSF Scorecard posture) are tracked for v0.4.0.

## Performance & Scale Metrics

| Metric | Target for v0.1.0 | How to Measure |
|--------|-------------------|----------------|
| Rule injection latency p50 | < 100 ms | Pre-task match time with `small` corpus |
| Rule injection latency p95 | < 500 ms | Pre-task match time with `small` corpus |
| Replay latency on `tiny` corpus | < 2 s per candidate | Benchmark run |
| Replay latency on `small` corpus | < 10 s per candidate | Benchmark run |
| Replay throughput | >= 6 candidates/minute on `small` corpus | Batched replay benchmark |
| Conflict detection time at 1k rules | < 5 s | Synthetic rule-store benchmark |
| Incremental reindex time | < 1 s per new rule at 1k rules | Benchmark run |
| Memory footprint on `small` corpus | < 1 GB RAM | Local benchmark |
| Storage growth transparency | Measured and documented | YAML + JSONL disk usage over benchmark runs |
| Concurrent failure ingestion correctness | 0 lost promotions, 0 duplicate IDs | Queue stress test |

## Cost Metrics

| Metric | Target for v0.1.0 | How to Measure |
|--------|-------------------|----------------|
| LLM cost per extracted candidate | Tracked and reported | Provider billing estimate |
| LLM cost per promoted rule | Tracked and reported | Total extraction cost / promoted rule count |
| Cost per prevented repeat failure | Downward trend over time | Total cost / counted prevented repeats |
| Demo run cost | Low enough to be acceptable for public trial | Cost of `cauterule demo` on default provider |

## Safety & Hygiene Metrics

| Metric | Target for v0.1.0 | How to Measure |
|--------|-------------------|----------------|
| Unsafe directive block rate | >= 95% | % of unsafe candidate rules blocked by linter or gate |
| Secret redaction success rate | 100% on redaction corpus | No known secrets survive extraction input preparation |
| Prompt injection resistance | >= 90% | Injection corpus attempts that fail to alter valid extractor output |
| Contradiction detection recall | >= 90% | % of seeded contradictory rules surfaced by conflict detection |
| Rule linter precision | >= 80% | % of linter findings judged genuinely useful |
| Provenance completeness | 100% of promoted rules | Every promoted rule includes source trajectory, replay evidence, timestamps |
| Validation pass rate before release | 100% | `cauterule validate` passes on release artifact |

## Developer Experience Metrics

| Metric | Target for v0.1.0 | How to Measure |
|--------|-------------------|----------------|
| Install success rate | >= 95% on supported environments | Test matrix across macOS/Linux/CI |
| Time to first successful demo | <= 5 minutes | New-user trial timing |
| Time to integrate with existing agent | <= 15 minutes | Trial using `@cauterule.watch` on a simple agent |
| Export usefulness | >= 80% | User validation that exported `CLAUDE.md` / `.cursorrules` are usable as-is |
| CLI task completion rate | >= 90% for core commands | Usability tests or scripted smoke flows |
| Report readability | Positive qualitative feedback | Review of generated markdown reports and learning journals |

## OSS Traction Metrics

| Metric | Target for v0.1.0 launch window | How to Measure |
|--------|-------------------------------|----------------|
| Stars | 100+ in first meaningful launch wave | GitHub analytics |
| Forks | 10+ | GitHub analytics |
| Issues filed by external users | 10+ useful issues | GitHub issues |
| External PRs | >= 2 | GitHub pull requests |
| Demo/benchmark mentions | Growing weekly | Social and issue references |
| Pack/community submissions | >= 1 external corpus, pack, or scenario contribution | Repo contributions |

## Derived Scores

These scores make the product easier to reason about at a glance.

| Score | Formula Idea | Why it matters |
|-------|--------------|----------------|
| **Rule Coverage Score** | weighted blend of failure-class coverage, near-miss precision, and stale-rule ratio | Summarizes how protected the agent is |
| **Learning Efficiency Score** | promoted rules / extraction cost | Shows whether the loop is economically useful |
| **Trust Score** | replay precision + provenance completeness + linter pass rate | Indicates whether rules are safe to rely on |
| **Safety-Adjusted Ranking** | rank candidates by safety evidence (near-miss precision, adversarial rejection, success-regression) before usefulness (recall, golden pass) | Prevents high-recall rules from jumping ahead of safe ones |
| **DX Score** | install success + time-to-wow + CLI completion rate | Reflects whether new users can actually adopt the tool |

## Release Gates for v0.1.0

`v0.1.0` is not good enough unless all of the following are true:

- `cauterule demo` runs successfully end-to-end on supported environments
- At least one field test shows a measurable repeat-failure reduction
- Replay precision is >= 90% on the public benchmark corpus
- Counterexample rejection rate is >= 90%
- Secret redaction passes on the redaction corpus
- Conflict detection catches seeded contradictions reliably
- `cauterule validate` passes on the shipped example rule store
- Install + demo flow works in under five minutes for a new user
- Documentation includes benchmark, corpus, and field-test methodology

## Metrics to Track but Not Gate on for v0.1.0

These are useful, but should inform iteration rather than block release:

- OSS traction (stars, forks, mentions)
- Cost per prevented repeat failure
- Model bake-off results
- Human vs LLM lesson comparison
- Long-horizon task improvement
- Multi-environment variance

## Why These Metrics Fit v0.1.0

The expanded `v0.1.0` scope is unusually ambitious: it includes not just the learning loop, but replay, corpus management, scale testing, adversarial evaluation, reports, export/import, and first-run demos. That means success cannot be measured only by "number of rules promoted." The release has to prove four things simultaneously:

1. **The rules are good.**
2. **The rules make the agent better.**
3. **The evaluation is trustworthy.**
4. **The product is usable enough that people will actually try it.**
