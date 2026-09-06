from cauterule.corpus.domains import (
    generate_browser_automation_trajectories,
    generate_coding_trajectories,
    generate_devops_trajectories,
    generate_research_trajectories,
    generate_support_trajectories,
)


def test_generate_coding_trajectories() -> None:
    trajs = generate_coding_trajectories(6)
    assert len(trajs) == 6
    for t in trajs:
        assert t.domain == "coding"
    successes = sum(1 for t in trajs if t.success)
    assert successes == 3
    assert any(t.failure_point is not None for t in trajs if not t.success)


def test_generate_devops_trajectories() -> None:
    trajs = generate_devops_trajectories(4)
    assert len(trajs) == 4
    for t in trajs:
        assert t.domain == "devops"
    successes = sum(1 for t in trajs if t.success)
    assert successes == 2


def test_generate_research_trajectories() -> None:
    trajs = generate_research_trajectories(8)
    assert len(trajs) == 8
    for t in trajs:
        assert t.domain == "research"
    successes = sum(1 for t in trajs if t.success)
    assert successes == 4


def test_generate_support_trajectories() -> None:
    trajs = generate_support_trajectories(2)
    assert len(trajs) == 2
    for t in trajs:
        assert t.domain == "support"
    successes = sum(1 for t in trajs if t.success)
    assert successes == 1


def test_generate_browser_automation_trajectories() -> None:
    trajs = generate_browser_automation_trajectories(10)
    assert len(trajs) == 10
    for t in trajs:
        assert t.domain == "browser_automation"
    successes = sum(1 for t in trajs if t.success)
    assert successes == 5


def test_all_generators_produce_valid_ids() -> None:
    for gen in (
        generate_coding_trajectories,
        generate_devops_trajectories,
        generate_research_trajectories,
        generate_support_trajectories,
        generate_browser_automation_trajectories,
    ):
        trajs = gen(4)
        for t in trajs:
            assert t.id
            assert t.id.count("-") >= 1


def test_generators_default_count() -> None:
    assert len(generate_coding_trajectories()) == 10
    assert len(generate_devops_trajectories()) == 10
    assert len(generate_research_trajectories()) == 10
    assert len(generate_support_trajectories()) == 10
    assert len(generate_browser_automation_trajectories()) == 10
