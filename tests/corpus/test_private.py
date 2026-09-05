import json
from pathlib import Path

import pytest

from cauterule.corpus.private import PrivateCorpus
from cauterule.models.trajectory import Step, Trajectory


def _write_trajectory(path: Path, t: Trajectory) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(t.to_dict()) + "\n")


def test_private_corpus_invalid_dir(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="root_dir must be an existing directory"):
        PrivateCorpus(str(tmp_path / "nonexistent"))


def test_private_corpus_empty_dir(tmp_path: Path) -> None:
    d = tmp_path / "empty_corpus"
    d.mkdir()
    pc = PrivateCorpus(str(d))
    assert pc.count() == 0
    assert pc.trajectories() == []


def test_private_corpus_single_file(tmp_path: Path) -> None:
    d = tmp_path / "single"
    d.mkdir()
    t = Trajectory(id="priv-001", timestamp="t", task="test", steps=(Step(step_number=1, tool="bash", input="echo"),), success=True)
    _write_trajectory(d / "traces.jsonl", t)
    pc = PrivateCorpus(str(d))
    assert pc.count() == 1
    assert pc.trajectories()[0].id == "priv-001"


def test_private_corpus_root_dir_property(tmp_path: Path) -> None:
    d = tmp_path / "prop_test"
    d.mkdir()
    pc = PrivateCorpus(str(d))
    assert pc.root_dir == str(d)


def test_private_corpus_filter_by_domain(tmp_path: Path) -> None:
    d = tmp_path / "filter_domain"
    d.mkdir()
    t1 = Trajectory(id="a", timestamp="t", task="t1", steps=(), success=True, domain="coding")
    t2 = Trajectory(id="b", timestamp="t", task="t2", steps=(), success=True, domain="devops")
    _write_trajectory(d / "data.jsonl", t1)
    _write_trajectory(d / "data.jsonl", t2)
    pc = PrivateCorpus(str(d))
    coding = pc.trajectories(domain="coding")
    assert len(coding) == 1
    assert coding[0].id == "a"


def test_private_corpus_filter_by_quality_label(tmp_path: Path) -> None:
    d = tmp_path / "filter_label"
    d.mkdir()
    t1 = Trajectory(id="a", timestamp="t", task="t1", steps=(), success=True, quality_label="clear")
    t2 = Trajectory(id="b", timestamp="t", task="t2", steps=(), success=True, quality_label="ambiguous")
    _write_trajectory(d / "data.jsonl", t1)
    _write_trajectory(d / "data.jsonl", t2)
    pc = PrivateCorpus(str(d))
    clear = pc.trajectories(quality_label="clear")
    assert len(clear) == 1
    assert clear[0].id == "a"


def test_private_corpus_filter_by_success(tmp_path: Path) -> None:
    d = tmp_path / "filter_success"
    d.mkdir()
    t1 = Trajectory(id="a", timestamp="t", task="t1", steps=(), success=True)
    t2 = Trajectory(id="b", timestamp="t", task="t2", steps=(), success=False, failure_point="s1", failure_class="err")
    _write_trajectory(d / "data.jsonl", t1)
    _write_trajectory(d / "data.jsonl", t2)
    pc = PrivateCorpus(str(d))
    succeeded = pc.trajectories(success=True)
    assert len(succeeded) == 1
    assert succeeded[0].id == "a"
    failed = pc.trajectories(success=False)
    assert len(failed) == 1
    assert failed[0].id == "b"


def test_private_corpus_reload(tmp_path: Path) -> None:
    d = tmp_path / "reload"
    d.mkdir()
    t1 = Trajectory(id="v1", timestamp="t", task="t", steps=(), success=True)
    _write_trajectory(d / "data.jsonl", t1)
    pc = PrivateCorpus(str(d))
    assert pc.count() == 1
    # Add another
    t2 = Trajectory(id="v2", timestamp="t", task="t", steps=(), success=True)
    _write_trajectory(d / "data.jsonl", t2)
    # Before reload, still sees old count (cached)
    assert pc.count() == 1
    pc.reload()
    assert pc.count() == 2


def test_private_corpus_multiple_jsonl_files(tmp_path: Path) -> None:
    d = tmp_path / "multi_file"
    d.mkdir()
    for i in range(3):
        t = Trajectory(id=f"pf-{i}", timestamp="t", task="t", steps=(), success=True)
        _write_trajectory(d / f"file{i}.jsonl", t)
    pc = PrivateCorpus(str(d))
    assert pc.count() == 3
