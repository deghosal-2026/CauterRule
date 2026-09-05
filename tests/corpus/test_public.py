import json
from pathlib import Path

from cauterule.corpus.public import load_public_corpus
from cauterule.models.trajectory import Step, Trajectory


def test_load_public_corpus_no_directory(tmp_path: Path) -> None:
    corpus = load_public_corpus(str(tmp_path / "nonexistent"))
    assert corpus == []


def test_load_public_corpus_empty_directory(tmp_path: Path) -> None:
    d = tmp_path / "public"
    d.mkdir()
    corpus = load_public_corpus(str(d))
    assert corpus == []


def test_load_public_corpus_with_data(tmp_path: Path) -> None:
    d = tmp_path / "public"
    d.mkdir()
    t = Trajectory(
        id="pub-001", timestamp="t", task="test", steps=(Step(step_number=1, tool="bash", input="echo hi"),), success=True
    )
    f = d / "sample.jsonl"
    with f.open("w") as fh:
        fh.write(json.dumps(t.to_dict()) + "\n")
    corpus = load_public_corpus(str(d))
    assert len(corpus) == 1
    assert corpus[0].id == "pub-001"


def test_load_public_corpus_multiple_files(tmp_path: Path) -> None:
    d = tmp_path / "multi"
    d.mkdir()
    for i in range(3):
        t = Trajectory(
            id=f"pub-{i:03d}", timestamp="t", task="task", steps=(Step(step_number=1, tool="bash", input="x"),), success=True
        )
        f = d / f"file{i}.jsonl"
        with f.open("w") as fh:
            fh.write(json.dumps(t.to_dict()) + "\n")
    corpus = load_public_corpus(str(d))
    assert len(corpus) == 3
    assert {t.id for t in corpus} == {"pub-000", "pub-001", "pub-002"}


def test_load_public_corpus_default_path() -> None:
    # When no path given, should not crash (returns empty if dir doesn't exist)
    corpus = load_public_corpus()
    assert isinstance(corpus, list)


def test_load_public_corpus_skips_non_jsonl(tmp_path: Path) -> None:
    d = tmp_path / "mixed"
    d.mkdir()
    t = Trajectory(id="pub-only", timestamp="t", task="t", steps=(), success=True)
    f = d / "data.jsonl"
    with f.open("w") as fh:
        fh.write(json.dumps(t.to_dict()) + "\n")
    # Non-jsonl file
    (d / "readme.txt").write_text("hello")
    corpus = load_public_corpus(str(d))
    assert len(corpus) == 1
