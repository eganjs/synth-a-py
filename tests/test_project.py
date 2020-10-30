from pathlib import Path

from synth_a_py import Project


def test_project(tmp_path: Path) -> None:
    spec = Project()
    spec.synth(tmp_path / "my-project")
    assert (tmp_path / "my-project").is_dir()


def test_deep_project(tmp_path: Path) -> None:
    spec = Project()
    spec.synth(tmp_path / "deep" / "my-project")
    assert (tmp_path / "deep" / "my-project").is_dir()


def test_no_arg_project(tmp_path: Path) -> None:
    spec = Project()
    spec.synth()
    assert tmp_path.is_dir()
