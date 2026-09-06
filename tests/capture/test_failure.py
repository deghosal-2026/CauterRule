from cauterule.capture.failure import detect_failure_class, detect_failure_point
from cauterule.models.trajectory import Step


def test_detect_failure_point() -> None:
    steps = [
        Step(step_number=1, tool="bash", output="ok"),
        Step(step_number=2, tool="bash", error="boom"),
        Step(step_number=3, tool="read", error="also boom"),
    ]
    assert detect_failure_point(steps) == "step_2"
    # no failure
    assert detect_failure_point([Step(step_number=1, tool="bash")]) is None
    assert detect_failure_point([]) is None
    # whitespace error not counted
    assert detect_failure_point([Step(step_number=1, tool="bash", error="   ")]) is None


def test_detect_failure_class() -> None:
    # non-fast-forward
    s = Step(step_number=1, tool="bash", error="! [rejected] non-fast-forward")
    assert detect_failure_class([s]) == "git/push/non-fast-forward"
    # rejected
    s2 = Step(step_number=1, tool="bash", error="rejected")
    assert detect_failure_class([s2]) == "git/push/non-fast-forward"
    # import
    s3 = Step(step_number=1, tool="python", error="ModuleNotFoundError: import")
    assert detect_failure_class([s3]) == "python/import"
    # docker
    s4 = Step(step_number=1, tool="docker", error="network error")
    assert detect_failure_class([s4]) == "docker/network"
    s5 = Step(step_number=1, tool="bash", error="docker network failed")
    assert detect_failure_class([s5]) == "docker/network"
    # fallback
    s6 = Step(step_number=1, tool="bash", error="something broke")
    assert detect_failure_class([s6]) == "bash/error"
    # no failure
    assert detect_failure_class([Step(step_number=1, tool="bash")]) is None
    assert detect_failure_class([]) is None
