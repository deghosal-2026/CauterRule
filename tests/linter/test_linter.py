from cauterule.linter.contradiction import check_contradiction
from cauterule.linter.duplicate import check_duplicate
from cauterule.linter.orchestrator import LinterResult, lint_rule
from cauterule.linter.tautology import check_tautology
from cauterule.linter.unsafe import check_unsafe
from cauterule.linter.untestable import check_untestable
from cauterule.linter.vagueness import check_vagueness
from cauterule.models.rule import Provenance, RuleDo, RuleWhen, StandingRule


def _rule(trigger: str, directive: str) -> StandingRule:
    return StandingRule(
        id="R-001", when=RuleWhen(trigger=trigger), do=RuleDo(directive=directive),
        confidence=0.9, provenance=Provenance(source_trajectory="a", extracted_by="m", extract_timestamp="t", extraction_pass=1),
        status="active", promoted_at="t",
    )


def test_vagueness() -> None:
    assert check_vagueness("be careful") == ["vague: 'be careful'"]
    assert check_vagueness("run git pull") == []
    assert check_vagueness("") == []


def test_tautology() -> None:
    assert check_tautology("same", "same") == ["tautology: trigger and directive are identical"]
    assert check_tautology("when failing", "don't fail") == ["tautology: when failing, don't fail"]
    assert check_tautology("when error", "ignore error") == ["tautology: when error, ignore error"]
    assert check_tautology("git push", "pull --rebase") == []


def test_duplicate() -> None:
    existing = [_rule("git push", "pull --rebase")]
    assert check_duplicate("git push", "pull --rebase", existing) == ["duplicate: matches existing rule R-001"]
    assert check_duplicate("git push", "pull --rebase", []) == []
    assert check_duplicate("docker", "pull", existing) == []


def test_contradiction() -> None:
    existing = [_rule("git push", "pull --rebase")]
    result = check_contradiction("git push", "force push", existing)
    assert len(result) == 1
    assert "contradiction" in result[0] and "R-001" in result[0]
    assert check_contradiction("git push", "pull --rebase", existing) == []
    assert check_contradiction("docker", "pull", existing) == []


def test_untestable() -> None:
    assert check_untestable("think carefully") == ["untestable: 'think carefully'"]
    assert check_untestable("run pull --rebase") == []


def test_unsafe() -> None:
    assert check_unsafe("run rm -rf /") == ["unsafe: use of rm -rf is destructive"]
    assert check_unsafe("run git push --force") == ["unsafe: force push can destroy remote history"]
    assert check_unsafe("run git pull") == []


def test_lint_rule_all_clean() -> None:
    result = lint_rule("git push fails", "run pull --rebase first")
    assert result.passed
    assert result.warnings == ()


def test_lint_rule_vague() -> None:
    result = lint_rule("be careful", "do something")
    assert not result.passed
    assert any("vague" in w for w in result.warnings)


def test_lint_rule_unsafe_blocks() -> None:
    result = lint_rule("delete", "run rm -rf /")
    assert not result.passed
    assert any("unsafe" in w for w in result.warnings)


def test_lint_rule_with_existing() -> None:
    existing = [_rule("git push", "pull --rebase")]
    result = lint_rule("git push", "pull --rebase", existing)
    assert not result.passed
    assert any("duplicate" in w for w in result.warnings)

    result2 = lint_rule("git push", "force push", existing)
    assert not result2.passed
    assert any("contradiction" in w for w in result2.warnings)


def test_linter_result_passed() -> None:
    assert LinterResult().passed
    assert not LinterResult(warnings=("bad",)).passed