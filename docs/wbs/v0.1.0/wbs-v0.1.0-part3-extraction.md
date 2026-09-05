# v0.1.0 — WBS Part 3: Rule Extraction & Clustering

**Milestones:** M6-M8

## M6: Failure Clustering

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 6.1 | Similarity scorer | `src/cauterule/extraction/clustering/similarity.py` | Compares failure class, tool sequence, error message | ✅ |
| 6.2 | Clusterer | `src/cauterule/extraction/clustering/clusterer.py` | Groups similar failures; one extraction per cluster | ✅ |
| 6.3 | Cluster config | `src/cauterule/extraction/clustering/config.py` | Similarity threshold (default 0.85), enabled/disabled | ✅ |

### M6 Exit Gate

- [x] Run all tests: `pytest` — all pass (144 passed)
- [x] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [x] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing` — 98.81%
- [x] Update all docs affected by this milestone
- [x] Verify all issues in this milestone are done
- [x] Close all completed issues
- [x] Commit with message: `milestone: M6 complete`
- [x] Push to main

## M7: Single-Pass Extraction

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 7.1 | Extraction prompt builder | `src/cauterule/extraction/prompt.py` | Builds prompt with trajectory, failure point, failure class, template request | ✅ |
| 7.2 | LLM extraction call | `src/cauterule/extraction/extractor.py` | Calls LLM, parses structured output into `CandidateRule` | ✅ |
| 7.3 | Quality checks | `src/cauterule/extraction/quality.py` | Valid structure, references trajectory, not tautological, confidence >= 0.6 | ✅ |
| 7.4 | Fallback handler | `src/cauterule/extraction/fallback.py` | Flag for human review if LLM cannot produce valid rule | ✅ |

### M7 Exit Gate

- [x] Run all tests: `pytest` — all pass (168 passed)
- [x] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [x] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing` — 98.51%
- [x] Update all docs affected by this milestone
- [x] Verify all issues in this milestone are done
- [x] Close all completed issues
- [x] Commit with message: `milestone: M7 complete`
- [x] Push to main

## M8: Multi-Pass & Draft Tournament

| # | Task | Files | Behavior | Status |
|---|------|-------|----------|--------|
| 8.1 | Multi-pass orchestrator | `src/cauterule/extraction/multipass.py` | Runs extraction 3x with temperatures [0.2, 0.5, 0.8] | ⬜ |
| 8.2 | Candidate deduplication | `src/cauterule/extraction/dedup.py` | Removes semantically identical candidates across passes | ⬜ |
| 8.3 | Draft tournament runner | `src/cauterule/extraction/tournament.py` | Replay-tests all candidates, ranks by precision > recall > confidence > specificity | ⬜ |
| 8.4 | Tournament ranking | `src/cauterule/extraction/ranking.py` | Produces ranked list with evidence reports | ⬜ |
| 8.5 | Close-call detection | `src/cauterule/extraction/closecall.py` | If top 2 within 5%, both held for human review | ⬜ |
| 8.6 | Dry-run mode | `src/cauterule/extraction/dryrun.py` | Shows what would be extracted without LLM call (cached/pattern only) | ⬜ |
| 8.7 | Human correction capture | `src/cauterule/extraction/human_correction.py` | Parses "next time do X" into candidate rule using trajectory context | ⬜ |
| 8.8 | Cross-failure pattern detection | `src/cauterule/extraction/patterns.py` | If Nth failure of same class, extract stronger rule addressing the pattern | ⬜ |

### M8 Exit Gate

- [ ] Run all tests: `pytest` — all pass
- [ ] Lint strict clean: `ruff check` + `mypy src/` — zero errors
- [ ] Test coverage total > 95%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Update all docs affected by this milestone
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Commit with message: `milestone: M8 complete`
- [ ] Push to main
