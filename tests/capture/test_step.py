import pytest

from cauterule.capture.step import StepCollector, create_step


def test_create_step_valid() -> None:
    s = create_step(1, "bash", input="git push", output="ok", error=None, state={"x": 1})
    assert s.step_number == 1
    assert s.tool == "bash"
    assert s.input == "git push"
    assert s.state == {"x": 1}


def test_create_step_validation() -> None:
    with pytest.raises(ValueError, match="step_number"):
        create_step(0, "bash")
    with pytest.raises(ValueError, match="tool"):
        create_step(1, "  ")


def test_step_collector() -> None:
    c = StepCollector()
    assert c.steps() == ()
    s1 = c.add("bash", input="a")
    assert s1.step_number == 1
    s2 = c.add("read", output="b")
    assert s2.step_number == 2
    assert len(c.steps()) == 2
    c.clear()
    assert c.steps() == ()
    s3 = c.add("bash")
    assert s3.step_number == 1


def test_step_collector_state() -> None:
    c = StepCollector()
    c.add("bash", error="boom")
    assert c.steps()[0].error == "boom"
