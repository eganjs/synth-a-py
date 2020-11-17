from pathlib import Path
from textwrap import dedent

from synth_a_py import IniFile, Project


def test_ini(tmp_path: Path) -> None:
    spec = Project()
    with spec:
        IniFile(
            ".mypy.ini",
            {
                "mypy": {
                    "strict": True,
                    "mypy_path": "stubs",
                    "plugins": "returns.contrib.mypy.returns_plugin",
                },
            },
        )

    spec.synth(tmp_path)

    assert (tmp_path / ".mypy.ini").read_text() == dedent(
        """\
        [mypy]
        strict = True
        mypy_path = stubs
        plugins = returns.contrib.mypy.returns_plugin
        """
    )
