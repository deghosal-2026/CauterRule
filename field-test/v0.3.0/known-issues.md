# Known Issues — CauterRule v0.3.0 Field Test

**Issue:** #671 · **Plan:** §10.6 / Appendix B · **Source:** `docs/field-test/v0.3.0/FIELD_TEST_REPORT.md` §13

---

## KI-1: Quality gate gap — golden & failures/positive below target
**Severity:** blocker
**Area:** core (replay matcher)
**Symptom:** Golden pass rate 10% (target ≥70%) and failures/positive 6-10% (target ≥50%) on all 4 models; precision 100%. Identical on cloud and local → structural, not model capability.
**Reproduction:** `scripts/run-field-test.py --all --llm-model <model>` → `summary.json` pass rates; see `FIELD_TEST_REPORT.md` §2/§8.
**Workaround:** Domain-aware context matching (#677) raised calibration golden recall 0.50→0.90 at precision 1.00; re-run sweep to confirm end-to-end. Full fix is semantic matching (#680, v0.4.0).
**Assignee:** matcher owners
**Status:** partially addressed (#677); release decision tracked by #673

## KI-2: Reference recall 0.02-0.04 (target ≥0.10)
**Severity:** high
**Area:** replay matcher / corpus
**Symptom:** Token-F1 matcher cannot bridge paraphrased triggers, so reference recall stays an order of magnitude below target even after the #489 corpus expansion.
**Reproduction:** `scripts/diagnose_corpus.py` + sweep summaries; see `corpus-diagnostics.md`.
**Workaround:** Opt-in semantic matching (#689, `CAUTERULE_SEMANTIC_MATCHING=1`, extra `[matching]`) adds a MiniLM cosine term. Re-run threshold calibration if enabled.
**Assignee:** replay owners
**Status:** deferred to v0.4.0 (#680)

## KI-3: Cross-session reduction not yet measured
**Severity:** medium
**Area:** lifecycle
**Symptom:** The ≥50% repeat-failure reduction headline metric (#445/#496) has no measured value.
**Reproduction:** `scripts/cross_session.py --baseline ... --intervention ...` (files emitted by the 5-session protocol).
**Workaround:** Tooling complete (`src/cauterule/measurement/cross_session.py`); run the protocol and populate `cross-session-results.md`.
**Assignee:** field-test owners
**Status:** open — tooling ready, measurement pending re-run

## KI-4: Human-vs-replay agreement not yet measured
**Severity:** medium
**Area:** review
**Symptom:** No reviewer agreement figure; the <0.8 human-gate decision is unset.
**Reproduction:** `scripts/human_agreement.py --results field-test/results/0.3.0` then score the filled reviews.
**Workaround:** Sampler + scorer complete (`tests/measurement/test_human_agreement.py`); awaits reviewer scoring.
**Assignee:** field-test owners
**Status:** open — tooling ready, scoring pending

## KI-5: Coverage 83% (target 95%)
**Severity:** medium
**Area:** core (release)
**Symptom:** Total coverage below the 95% `fail_under` gate; worst modules were CLI reporting paths.
**Reproduction:** `pytest --cov=src/cauterule --cov-report=term-missing`.
**Workaround:** #494 closed at 83.15% with +44 CLI/report and +65 integration tests; remaining gap deferred to M8.
**Assignee:** quality owners
**Status:** deferred (M8); `fail_under` reconciliation tracked

## KI-6: 2 Docker compose re-runs failing
**Severity:** low
**Area:** docker
**Symptom:** `test_compose_mcp_accepts` (service never reaches `running`) and `test_compose_test_passes` (in-container pytest exits 1) fail after nuke+rebuild.
**Reproduction:** `pytest tests/field/test_docker_compose.py -m docker -v`; see `docker-test-results.md` §6.
**Workaround:** All other 157/159 docker tests pass; fixes applied (profiles + `pip --user`) but the 2 remain. Long pole is orchestration timing.
**Assignee:** docker owners
**Status:** open (low priority)

## KI-7: OTEL exporter log noise when extra not installed
**Severity:** low (cosmetic)
**Area:** otel
**Symptom:** "opentelemetry.exporter not installed" logged when the `[otel]` extra is absent; emit is correctly non-fatal.
**Reproduction:** `cauterule otel test` without the extra.
**Workaround:** `pip install cauterule[otel]` in dev venv.
**Assignee:** observability owners
**Status:** open (cosmetic)
