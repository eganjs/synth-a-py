from contextlib import contextmanager
from os import chdir
from pathlib import Path
from textwrap import dedent
from typing import Iterator

from pytest import raises

from synth_a_py import Dir, Project, SimpleFile
from synth_a_py.base import _context_get, synth


def test_project(tmp_path: Path) -> None:
    Project().synth(to=tmp_path / "my-project")

    assert (tmp_path / "my-project").is_dir()


def test_deep_project(tmp_path: Path) -> None:
    Project().synth(to=tmp_path / "deep" / "my-project")

    assert (tmp_path / "deep" / "my-project").is_dir()


@contextmanager
def chcwd(path: Path) -> Iterator[None]:
    original_cwd = Path.cwd()
    chdir(path)
    yield
    chdir(original_cwd)


def test_no_arg_project(tmp_path: Path) -> None:
    with chcwd(tmp_path):
        Project().synth()

        assert tmp_path.is_dir()


def test_get_context_in_with() -> None:
    project = Project()
    with project:
        context = _context_get()

    assert project == context


def test_get_context_outside_with() -> None:
    with raises(AssertionError):
        _context_get()


def test_get_context_after_with() -> None:
    with raises(AssertionError):
        with Project():
            pass

        _context_get()


def test_example_project(tmp_path: Path) -> None:
    project_path = tmp_path / "my-project"

    with synth(to=project_path):
        with Dir("src"):
            init_content = dedent(
                """\
                __version__ = "0.1.0"
                """
            )
            SimpleFile("__init__.py", init_content)

        with Dir("tests"):
            test_content = dedent(
                """\
                from src import __version__

                def test_version():
                    assert __version__ == "0.1.0"
                """
            )
            SimpleFile("test_version.py", test_content)

    assert (project_path / "src" / "__init__.py").read_text() == init_content
    assert (project_path / "tests" / "test_version.py").read_text() == test_content


def test_subsequent_synth(tmp_path: Path) -> None:
    project_path = tmp_path / "my-project"

    # first pass
    with synth(to=project_path):
        with Dir("subdir"):
            SimpleFile("file.txt", "Hello, World!")

    assert (project_path / "subdir" / "file.txt").read_text() == "Hello, World!\n"
    assert (project_path / "subdir" / "file.txt").lstat().st_mode & 0o777 == 0o444

    # second pass
    with synth(to=project_path):
        with Dir("subdir"):
            SimpleFile("file.txt", "Hello, synth-a-py!")

    assert (project_path / "subdir" / "file.txt").read_text() == "Hello, synth-a-py!\n"
    assert (project_path / "subdir" / "file.txt").lstat().st_mode & 0o777 == 0o444
