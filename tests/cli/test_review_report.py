from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from click.testing import CliRunner

from cauterule.cli.app import main
from cauterule.models.rule import Provenance, ReplayEvidence, RuleDo, RuleWhen, StandingRule
from cauterule.store.manager import StoreManager


def _provenance() -> Provenance:
    return Provenance(
        source_trajectory="t",
        extracted_by="m",
        extract_timestamp="2026-09-01T00:00:00Z",
        extraction_pass=1,
    )


def _rule(
    rid: str,
    trigger: str = "git push fails",
    directive: str = "pull first",
    confidence: float = 0.85,
    status: str = "active",
    tags: tuple[str, ...] = ("git",),
    hit_count: int = 0,
    last_match: str | None = None,
    specificity: float | None = None,
    specificity_inputs: dict[str, Any] | None = None,
    taxonomy: str | None = None,
    prevented: int = 0,
    broke: int = 0,
    neutral: int = 0,
    last_outcome: str | None = None,
    last_outcome_at: str | None = None,
    outcome_trend: tuple[int, ...] = (),
    when_context: tuple[str, ...] = (),
    because: str | None = None,
    superseded_by: str | None = None,
    promoted_at: str = "2026-09-01T00:00:00Z",
    replay_evidence: ReplayEvidence | None = None,
) -> StandingRule:
    prov = _provenance()
    if replay_evidence is not None:
        prov = Provenance(
            source_trajectory=prov.source_trajectory,
            extracted_by=prov.extracted_by,
            extract_timestamp=prov.extract_timestamp,
            extraction_pass=prov.extraction_pass,
            replay_evidence=replay_evidence,
        )
    return StandingRule(
        id=rid,
        when=RuleWhen(trigger=trigger, context=when_context),
        do=RuleDo(directive=directive, because=because),
        confidence=confidence,
        provenance=prov,
        status=status,  # type: ignore[arg-type]
        promoted_at=promoted_at,
        hit_count=hit_count,
        last_match=last_match,
        tags=tags,
        taxonomy=taxonomy,
        specificity=specificity,
        specificity_inputs=specificity_inputs or {},
        prevented_count=prevented,
        broke_count=broke,
        neutral_count=neutral,
        last_outcome=last_outcome,
        last_outcome_at=last_outcome_at,
        outcome_trend=outcome_trend,
        superseded_by=superseded_by,
    )


def _seed_store(path: Path, rules: list[StandingRule]) -> None:
    path.mkdir(parents=True, exist_ok=True)
    mgr = StoreManager(base_dir=str(path))
    for r in rules:
        mgr.add_rule(r)


def _write_summary(
    p: Path,
    corpus_type: str,
    provider: str,
    model: str,
    passing: int,
    accepted: int,
    inconclusive: int = 0,
    total_candidates: int = 10,
    done: int = 10,
    gate_dropped: int = 0,
) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "meta": {"corpus_type": corpus_type, "llm_provider": provider, "llm_model": model},
        "passing": passing,
        "safety": {"accepted": accepted},
        "inconclusive": inconclusive,
        "total_candidates": total_candidates,
        "done": done,
        "gate_dropped": gate_dropped,
    }
    p.write_text(json.dumps(data), encoding="utf-8")


# ------------------------------------------------------------------
# review
# ------------------------------------------------------------------


class TestReview:
    def test_json_empty(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["review", "--json", "--store-dir", str(tmp_path / "rules")])
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload == []

    def test_batch_mode(self, tmp_path: Path) -> None:
        _seed_store(
            tmp_path / "rules",
            [
                _rule("R-001", tags=("git",), confidence=0.9, hit_count=1),
                _rule("R-002", tags=("docker",), confidence=0.6, hit_count=0),
            ],
        )
        runner = CliRunner()
        result = runner.invoke(main, ["review", "--batch", "--store-dir", str(tmp_path / "rules")])
        assert result.exit_code == 0, result.output
        # batch dumps queue_size and candidates[:10] plus extra line
        assert "queue_size" in result.output
        assert "Batch review" in result.output

    def test_batch_with_json_flag(self, tmp_path: Path) -> None:
        _seed_store(tmp_path / "rules", [_rule("R-001", tags=("git",))])
        runner = CliRunner()
        result = runner.invoke(
            main, ["review", "--batch", "--json", "--store-dir", str(tmp_path / "rules")]
        )
        assert result.exit_code == 0, result.output
        assert "Batch review" not in result.output
        payload = json.loads(result.output)
        assert payload["queue_size"] == 1

    def test_export_annotations(self, tmp_path: Path) -> None:
        _seed_store(tmp_path / "rules", [_rule("R-001", tags=("git",))])
        runner = CliRunner()
        result = runner.invoke(
            main, ["review", "--export-annotations", "--store-dir", str(tmp_path / "rules")]
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload[0]["id"] == "R-001"

    def test_filter_by_tag_with_equals(self, tmp_path: Path) -> None:
        _seed_store(
            tmp_path / "rules",
            [
                _rule("R-001", tags=("git",), trigger="git push fail"),
                _rule("R-002", tags=("docker",), trigger="docker fail"),
            ],
        )
        runner = CliRunner()
        result = runner.invoke(
            main, ["review", "--filter", "tag=git", "--json", "--store-dir", str(tmp_path / "rules")]
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert len(payload) == 1 and payload[0]["id"] == "R-001"

    def test_filter_by_tag_without_equals(self, tmp_path: Path) -> None:
        _seed_store(
            tmp_path / "rules",
            [
                _rule("R-001", tags=("GIT",), trigger="git push fail"),
                _rule("R-002", tags=("docker",), trigger="docker fail"),
            ],
        )
        runner = CliRunner()
        result = runner.invoke(
            main, ["review", "--filter", "docker", "--json", "--store-dir", str(tmp_path / "rules")]
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert len(payload) == 1 and payload[0]["id"] == "R-002"

    def test_filter_by_tag_case_insensitive(self, tmp_path: Path) -> None:
        _seed_store(tmp_path / "rules", [_rule("R-001", tags=("Git",))])
        runner = CliRunner()
        result = runner.invoke(
            main, ["review", "--filter", "tag=GIT", "--json", "--store-dir", str(tmp_path / "rules")]
        )
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert len(payload) == 1

    def test_filter_by_status(self, tmp_path: Path) -> None:
        _seed_store(
            tmp_path / "rules",
            [
                _rule("R-001", status="active"),
                _rule("R-002", status="retired"),
            ],
        )
        runner = CliRunner()
        result = runner.invoke(
            main, ["review", "--status", "active", "--json", "--store-dir", str(tmp_path / "rules")]
        )
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert len(payload) == 1 and payload[0]["id"] == "R-001"

    def test_filter_status_all(self, tmp_path: Path) -> None:
        _seed_store(
            tmp_path / "rules",
            [_rule("R-001", status="active"), _rule("R-002", status="retired")],
        )
        runner = CliRunner()
        result = runner.invoke(
            main, ["review", "--status", "all", "--json", "--store-dir", str(tmp_path / "rules")]
        )
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert len(payload) == 2

    def test_confidence_range(self, tmp_path: Path) -> None:
        _seed_store(
            tmp_path / "rules",
            [
                _rule("R-001", confidence=0.9),
                _rule("R-002", confidence=0.5),
                _rule("R-003", confidence=0.75),
            ],
        )
        runner = CliRunner()
        result = runner.invoke(
            main, ["review", "--confidence", "0.7-1.0", "--json", "--store-dir", str(tmp_path / "rules")]
        )
        assert result.exit_code == 0
        payload = json.loads(result.output)
        ids = {r["id"] for r in payload}
        assert ids == {"R-001", "R-003"}

    def test_confidence_single(self, tmp_path: Path) -> None:
        _seed_store(tmp_path / "rules", [_rule("R-001", confidence=0.9), _rule("R-002", confidence=0.5)])
        runner = CliRunner()
        result = runner.invoke(
            main, ["review", "--confidence", "0.8", "--json", "--store-dir", str(tmp_path / "rules")]
        )
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert len(payload) == 1 and payload[0]["id"] == "R-001"

    def test_confidence_invalid_range(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            main, ["review", "--confidence", "bad-1.0", "--store-dir", str(tmp_path / "rules")]
        )
        assert result.exit_code != 0
        assert "confidence must be like" in result.output

    def test_confidence_invalid_numeric(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            main, ["review", "--confidence", "abc", "--store-dir", str(tmp_path / "rules")]
        )
        assert result.exit_code != 0
        assert "confidence must be numeric" in result.output

    def test_confidence_max_filter(self, tmp_path: Path) -> None:
        _seed_store(tmp_path / "rules", [_rule("R-001", confidence=0.95), _rule("R-002", confidence=0.2)])
        runner = CliRunner()
        result = runner.invoke(
            main, ["review", "--confidence", "0.0-0.5", "--json", "--store-dir", str(tmp_path / "rules")]
        )
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert len(payload) == 1 and payload[0]["id"] == "R-002"

    def test_interactive_tui_patched(self, tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        _seed_store(tmp_path / "rules", [_rule("R-001")])
        import cauterule.tui.app as tui_app

        called: dict[str, bool] = {}

        class Dummy:
            def run(self) -> None:
                called["run"] = True

        monkeypatch.setattr(tui_app, "CauterRuleApp", lambda: Dummy())
        runner = CliRunner()
        result = runner.invoke(main, ["review", "--store-dir", str(tmp_path / "rules")])
        assert result.exit_code == 0
        assert called.get("run") is True


# ------------------------------------------------------------------
# report
# ------------------------------------------------------------------


class TestReport:
    def test_no_safety_flag(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["report"])
        assert result.exit_code == 0
        assert "CauterRule Report" in result.output
        assert "Pass --safety-adjusted" in result.output

    def test_missing_results_dir(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            main, ["report", "--safety-adjusted", "--results-dir", str(tmp_path / "missing")]
        )
        assert result.exit_code == 1

    def test_no_summary_files(self, tmp_path: Path) -> None:
        (tmp_path / "results").mkdir()
        runner = CliRunner()
        result = runner.invoke(
            main, ["report", "--safety-adjusted", "--results-dir", str(tmp_path / "results")]
        )
        assert result.exit_code == 0
        assert "No summary.json files found" in result.output

    def test_safety_ranking_two_models(self, tmp_path: Path) -> None:
        results = tmp_path / "results"
        _write_summary(
            results / "successes" / "openai/gpt-4" / "2026-09-01" / "summary.json",
            corpus_type="successes",
            provider="openai",
            model="gpt-4",
            passing=10,
            accepted=2,
        )
        _write_summary(
            results / "failures/negative" / "openai/gpt-4" / "2026-09-01" / "summary.json",
            corpus_type="failures/negative",
            provider="openai",
            model="gpt-4",
            passing=5,
            accepted=1,
        )
        _write_summary(
            results / "successes" / "anthropic/claude" / "2026-09-01" / "summary.json",
            corpus_type="successes",
            provider="anthropic",
            model="claude",
            passing=8,
            accepted=0,
        )
        runner = CliRunner()
        result = runner.invoke(
            main, ["report", "--safety-adjusted", "--results-dir", str(results)]
        )
        assert result.exit_code == 0
        assert "Safety-Adjusted Model Ranking" in result.output
        assert "openai/gpt-4" in result.output
        assert "anthropic/claude" in result.output
        assert "Decision Economics" in result.output
        assert (results / "safety-ranking.md").is_file()

    def test_invalid_json_skipped(self, tmp_path: Path) -> None:
        results = tmp_path / "results"
        good = results / "successes" / "openai/gpt-4" / "2026-09-01" / "summary.json"
        _write_summary(good, "successes", "openai", "gpt-4", passing=5, accepted=1)
        bad = results / "successes" / "openai/gpt-4" / "2026-09-02" / "summary.json"
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.write_text("{not json", encoding="utf-8")
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--safety-adjusted", "--results-dir", str(results)])
        assert result.exit_code == 0
        assert "openai/gpt-4" in result.output

    def test_other_corpus_type(self, tmp_path: Path) -> None:
        results = tmp_path / "results"
        _write_summary(
            results / "other" / "openai/gpt-4" / "2026-09-01" / "summary.json",
            corpus_type="other",
            provider="openai",
            model="gpt-4",
            passing=7,
            accepted=5,
        )
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--safety-adjusted", "--results-dir", str(results)])
        assert result.exit_code == 0
        assert "openai/gpt-4" in result.output

    def test_trajectories_zero(self, tmp_path: Path) -> None:
        results = tmp_path / "results"
        p = results / "successes" / "openai/gpt-4" / "2026-09-01" / "summary.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps(
                {
                    "meta": {"corpus_type": "successes", "llm_provider": "openai", "llm_model": "gpt-4"},
                    "passing": 3,
                    "safety": {"accepted": 1},
                    "inconclusive": 0,
                    "total_candidates": 0,
                    "done": 0,
                    "gate_dropped": 0,
                }
            ),
            encoding="utf-8",
        )
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--safety-adjusted", "--results-dir", str(results)])
        assert result.exit_code == 0
        assert "openai/gpt-4" in result.output


# ------------------------------------------------------------------
# show
# ------------------------------------------------------------------


class TestShow:
    def test_not_found(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["show", "R-999"])
        assert result.exit_code == 0
        assert "not found" in result.output

    def test_basic_show(self, tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        rule = _rule(
            "R-001",
            trigger="git push rejected non-fast-forward",
            directive="run git pull --rebase",
            when_context=("repo",),
            because="keep history linear",
            confidence=0.92,
            tags=("git", "push"),
            taxonomy="git/push",
            hit_count=3,
            last_match="2026-09-01T00:00:00Z",
            specificity=0.88,
            specificity_inputs={
                "trigger_tokens": 4,
                "matched_count": 5,
                "broken_count": 0,
                "breadth_penalty": 0.0,
            },
            replay_evidence=ReplayEvidence(
                failures_prevented=("T-1",), successes_broken=("T-2",), precision=0.9, recall=0.8
            ),
        )
        store = tmp_path / "rules"
        _seed_store(store, [rule])
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(main, ["show", "R-001"])
        assert result.exit_code == 0
        assert "ID: R-001" in result.output
        assert "Context:" in result.output
        assert "Because:" in result.output
        assert "Specificity: 0.88" in result.output
        assert "inputs: trigger_tokens=" in result.output
        assert "Tags: git, push" in result.output
        assert "Taxonomy: git/push" in result.output
        assert "Failures prevented: 1" in result.output

    def test_hits_flag_never(self, tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        rule = _rule("R-001", hit_count=0, last_match=None, tags=())
        store = tmp_path / "rules"
        _seed_store(store, [rule])
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(main, ["show", "R-001", "--hits"])
        assert result.exit_code == 0
        assert "Last match: never" in result.output
        assert "Tags: none" in result.output

    def test_specificity_computed(self, tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        rule = _rule("R-001", specificity=None, status="active", trigger="git push fails")
        store = tmp_path / "rules"
        _seed_store(store, [rule])
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(main, ["show", "R-001"])
        assert result.exit_code == 0
        assert "Specificity:" in result.output
        assert "computed" in result.output

    def test_specificity_not_shown_for_retired(self, tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        rule = _rule("R-001", specificity=None, status="retired")
        store = tmp_path / "rules"
        _seed_store(store, [rule])
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(main, ["show", "R-001"])
        assert result.exit_code == 0
        assert "computed" not in result.output

    def test_outcomes(self, tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        rule = _rule(
            "R-001",
            prevented=2,
            broke=1,
            neutral=1,
            last_outcome="prevented",
            last_outcome_at="2026-09-01T00:00:00Z",
            outcome_trend=(1, -1, 0),
        )
        store = tmp_path / "rules"
        _seed_store(store, [rule])
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(main, ["show", "R-001", "--outcomes"])
        assert result.exit_code == 0
        assert "prevented: 2" in result.output
        assert "broke:" in result.output
        assert "prevented-rate:" in result.output
        assert "trend:" in result.output

    def test_outcomes_empty_trend(self, tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        rule = _rule("R-001", prevented=1, broke=0, neutral=0, outcome_trend=())
        store = tmp_path / "rules"
        _seed_store(store, [rule])
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(main, ["show", "R-001", "--outcomes"])
        assert result.exit_code == 0
        assert "prevented: 1" in result.output

    def test_history(self, tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        r1 = _rule("R-001", status="superseded", superseded_by="R-002")
        r2 = _rule("R-002", status="active", superseded_by=None)
        store = tmp_path / "rules"
        _seed_store(store, [r1, r2])
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(main, ["show", "R-001", "--history"])
        assert result.exit_code == 0
        assert "Supersession chain" in result.output
        assert "R-001" in result.output
        assert "→" in result.output

    def test_history_cycle(self, tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        r1 = _rule("R-001", status="superseded", superseded_by="R-002")
        r2 = _rule("R-002", status="superseded", superseded_by="R-001")
        store = tmp_path / "rules"
        _seed_store(store, [r1, r2])
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(main, ["show", "R-001", "--history"])
        assert result.exit_code == 0
        assert "Error:" in result.output


# ------------------------------------------------------------------
# metrics
# ------------------------------------------------------------------


class TestMetrics:
    def test_default_empty(self, tmp_path: Path) -> None:
        store = tmp_path / "rules"
        store.mkdir()
        runner = CliRunner()
        result = runner.invoke(main, ["metrics", "--store-dir", str(store)])
        assert result.exit_code == 0
        assert "Total rules: 0" in result.output

    def test_default_with_rules(self, tmp_path: Path) -> None:
        _seed_store(
            tmp_path / "rules",
            [
                _rule("R-001", status="active", confidence=0.9, hit_count=1),
                _rule("R-002", status="retired", confidence=0.5, hit_count=0),
            ],
        )
        runner = CliRunner()
        result = runner.invoke(main, ["metrics", "--store-dir", str(tmp_path / "rules")])
        assert result.exit_code == 0
        assert "Total rules: 2" in result.output
        assert "Coverage score:" in result.output

    def test_stale_rules(self, tmp_path: Path) -> None:
        _seed_store(
            tmp_path / "rules",
            [
                _rule("R-001", status="active", hit_count=0, last_match=None),
                _rule("R-002", status="active", hit_count=1, last_match="2026-09-10T00:00:00Z"),
            ],
        )
        runner = CliRunner()
        result = runner.invoke(main, ["metrics", "--store-dir", str(tmp_path / "rules")])
        assert result.exit_code == 0
        assert "Stale rules" in result.output

    def test_coverage_flag(self, tmp_path: Path) -> None:
        _seed_store(tmp_path / "rules", [_rule("R-001", status="active")])
        runner = CliRunner()
        result = runner.invoke(main, ["metrics", "--coverage", "--store-dir", str(tmp_path / "rules")])
        assert result.exit_code == 0
        assert "Coverage score:" in result.output

    def test_by_domain(self, tmp_path: Path) -> None:
        _seed_store(
            tmp_path / "rules",
            [
                _rule("R-001", tags=("git",), hit_count=1),
                _rule("R-002", tags=("docker",), hit_count=0),
                _rule("R-003", tags=("git",), hit_count=0),
            ],
        )
        runner = CliRunner()
        result = runner.invoke(main, ["metrics", "--by-domain", "--store-dir", str(tmp_path / "rules")])
        assert result.exit_code == 0
        assert "git:" in result.output
        assert "docker:" in result.output

    def test_by_domain_empty(self, tmp_path: Path) -> None:
        (tmp_path / "rules").mkdir()
        runner = CliRunner()
        result = runner.invoke(main, ["metrics", "--by-domain", "--store-dir", str(tmp_path / "rules")])
        assert result.exit_code == 0
        assert "No domain coverage" in result.output

    def test_by_class(self, tmp_path: Path) -> None:
        _seed_store(tmp_path / "rules", [_rule("R-001")])
        runner = CliRunner()
        result = runner.invoke(main, ["metrics", "--by-class", "--store-dir", str(tmp_path / "rules")])
        assert result.exit_code == 0
        assert "Class coverage requires trajectories" in result.output

    def test_lowest_spec_empty(self, tmp_path: Path) -> None:
        (tmp_path / "rules").mkdir()
        runner = CliRunner()
        result = runner.invoke(main, ["metrics", "--lowest-spec", "--store-dir", str(tmp_path / "rules")])
        assert result.exit_code == 0
        assert "No rules found" in result.output

    def test_lowest_spec(self, tmp_path: Path) -> None:
        _seed_store(
            tmp_path / "rules",
            [
                _rule("R-001", trigger="fails", status="active"),
                _rule("R-002", trigger="git push rejected non-fast-forward error-code-123", status="active"),
            ],
        )
        runner = CliRunner()
        result = runner.invoke(main, ["metrics", "--lowest-spec", "--store-dir", str(tmp_path / "rules")])
        assert result.exit_code == 0
        assert "Lowest-specificity" in result.output
        assert "R-001" in result.output

    def test_lowest_spec_broad_marker(self, tmp_path: Path) -> None:
        _seed_store(tmp_path / "rules", [_rule("R-001", trigger="fails")])
        runner = CliRunner()
        result = runner.invoke(main, ["metrics", "--lowest-spec", "--store-dir", str(tmp_path / "rules")])
        assert result.exit_code == 0
        assert "BROAD" in result.output

    def test_rule_id(self, tmp_path: Path) -> None:
        _seed_store(
            tmp_path / "rules",
            [
                _rule(
                    "R-001",
                    prevented=2,
                    broke=1,
                    neutral=0,
                    last_outcome="prevented",
                    last_outcome_at="2026-09-01T00:00:00Z",
                    outcome_trend=(1, -1),
                )
            ],
        )
        runner = CliRunner()
        result = runner.invoke(main, ["metrics", "--rule", "R-001", "--store-dir", str(tmp_path / "rules")])
        assert result.exit_code == 0
        assert "Rule: R-001" in result.output
        assert "prevented: 2" in result.output
        assert "trend:" in result.output

    def test_rule_id_no_trend(self, tmp_path: Path) -> None:
        _seed_store(tmp_path / "rules", [_rule("R-001", prevented=1, outcome_trend=())])
        runner = CliRunner()
        result = runner.invoke(main, ["metrics", "--rule", "R-001", "--store-dir", str(tmp_path / "rules")])
        assert result.exit_code == 0
        assert "Rule: R-001" in result.output

    def test_rule_id_last_outcome_none(self, tmp_path: Path) -> None:
        _seed_store(tmp_path / "rules", [_rule("R-001")])
        runner = CliRunner()
        result = runner.invoke(main, ["metrics", "--rule", "R-001", "--store-dir", str(tmp_path / "rules")])
        assert result.exit_code == 0
        assert "last outcome:" in result.output
