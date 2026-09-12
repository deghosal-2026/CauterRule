from cauterule.capture.taxonomy import classify_taxonomy


def test_classify_taxonomy_keywords() -> None:
    assert (
        classify_taxonomy("bash", error="! [rejected] non-fast-forward")
        == "git/push/non-fast-forward"
    )
    assert classify_taxonomy("bash", error="git push") == "git/push"
    assert classify_taxonomy("python", error="ModuleNotFoundError: import foo") == "python/import"
    assert classify_taxonomy("pip", error="pip install failed") == "python/pip"
    assert classify_taxonomy("docker", error="network unreachable") == "docker/network"
    assert classify_taxonomy("bash", output="docker container failed") == "docker/container"
    assert classify_taxonomy("bash", error="rejected") == "git/push"


def test_classify_taxonomy_fallback() -> None:
    assert classify_taxonomy("mytool", error="boom") == "mytool/error"
    assert classify_taxonomy("mytool", error=None, output=None) == "mytool/success"
    assert classify_taxonomy("", error="boom") == "unknown/error"
    assert classify_taxonomy("  ", error=None) == "unknown/success"
    # tool with space
    assert classify_taxonomy("my tool", error="boom") == "my/tool/error"


def test_classify_taxonomy_precedence() -> None:
    # longer keyword should win over shorter
    assert (
        classify_taxonomy("bash", error="git push non-fast-forward rejected")
        == "git/push/non-fast-forward"
    )
