from pathlib import Path
from textwrap import dedent

from synth_a_py import Dir, GitIgnore, Project, SimpleFile


def test_gitignore(tmp_path: Path) -> None:
    spec = Project()
    with spec:
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

    spec.synth(tmp_path)

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
