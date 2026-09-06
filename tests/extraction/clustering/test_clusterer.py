import pytest

from cauterule.extraction.clustering.clusterer import cluster_trajectories
from cauterule.extraction.clustering.config import ClusteringConfig
from cauterule.models.trajectory import Step, Trajectory


def _traj(id: str, failure_class: str, error: str) -> Trajectory:
    return Trajectory(
        id=id,
        timestamp="t",
        task="task",
        steps=(Step(step_number=1, tool="bash", error=error),),
        success=False,
        failure_class=failure_class,
    )


def test_cluster_basic() -> None:
    a = _traj("T-1", "git/push", "non-fast-forward")
    b = _traj("T-2", "git/push", "non-fast-forward")
    c = _traj("T-3", "python/import", "import error")
    clusters = cluster_trajectories([a, b, c], threshold=0.85)
    assert len(clusters) == 2
    assert len(clusters[0]) == 2  # a,b
    assert len(clusters[1]) == 1  # c


def test_cluster_disabled() -> None:
    trajs = [_traj(f"T-{i}", "git/push", "error") for i in range(3)]
    clusters = cluster_trajectories(trajs, config=ClusteringConfig(enabled=False))
    assert len(clusters) == 3
    assert all(len(c) == 1 for c in clusters)


def test_cluster_threshold() -> None:
    a = _traj("T-1", "git/push", "error A")
    b = _traj("T-2", "git/push", "error B")
    # low threshold groups together
    assert len(cluster_trajectories([a, b], threshold=0.1)) == 1
    # high threshold splits
    assert len(cluster_trajectories([a, b], threshold=0.99)) == 2


def test_cluster_empty() -> None:
    assert cluster_trajectories([]) == []


def test_cluster_single() -> None:
    a = _traj("T-1", "git/push", "error")
    assert cluster_trajectories([a]) == [[a]]


def test_cluster_invalid_threshold() -> None:
    a = _traj("T-1", "git/push", "error")
    with pytest.raises(ValueError, match="threshold"):
        cluster_trajectories([a], threshold=1.5)
    with pytest.raises(ValueError, match="threshold"):
        cluster_trajectories([a], threshold=-0.1)
