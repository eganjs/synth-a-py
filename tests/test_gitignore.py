from pathlib import Path
from textwrap import dedent

from synth_a_py import Dir, GitIgnore, SimpleFile
from synth_a_py.base import synth


def test_gitignore(tmp_path: Path) -> None:
    with synth(to=tmp_path):
        GitIgnore(
            ignore=[
                ".venv/",
                "*.pyc",
                "*.so",
                "*.py",
            ],
            allow=[
                "needed.so",
            ],
        )

        with Dir("src"):
            SimpleFile(
                "main.py",
                dedent(
                    """\
                    Hello, World!
                    """
                ),
            )

    assert (tmp_path / ".gitignore").read_text() == dedent(
        """\
        .venv/
        *.pyc
        *.so
        *.py
        !.gitignore
        !src/main.py
        !needed.so
        """
    )
