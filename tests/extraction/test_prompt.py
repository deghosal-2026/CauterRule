from cauterule.extraction.prompt import build_extraction_prompt
from cauterule.models.trajectory import Step, Trajectory


def _traj() -> Trajectory:
    return Trajectory(
        id="T-001",
        timestamp="2026-09-03T18:25:00Z",
        task="git push fails",
        steps=(Step(step_number=1, tool="bash", error="non-fast-forward"),),
        success=False,
        failure_point="step_1",
        failure_class="git/push",
        tags=("git",),
    )


def test_build_prompt_basic() -> None:
    prompt = build_extraction_prompt(_traj())
    assert "git push fails" in prompt
    assert "non-fast-forward" in prompt
    assert "git/push" in prompt
    assert "when" in prompt.lower()
    assert "do" in prompt.lower()


def test_build_prompt_template() -> None:
    prompt = build_extraction_prompt(_traj(), template="retry")
    assert "retry" in prompt.lower()
    prompt2 = build_extraction_prompt(_traj(), template="verify-then-act")
    assert "verify" in prompt2.lower()
    prompt3 = build_extraction_prompt(_traj(), template="custom")
    assert "custom" in prompt3.lower()


def test_build_prompt_no_template() -> None:
    prompt = build_extraction_prompt(_traj(), template=None)
    assert "Template hint" not in prompt


def test_build_prompt_no_tags() -> None:
    t = Trajectory(id="T-002", timestamp="t", task="task", steps=(), success=True)
    prompt = build_extraction_prompt(t)
    assert "none" in prompt.lower()
