from pathlib import Path
from textwrap import dedent

from synth_a_py import IniFile
from synth_a_py.base import synth


def test_ini(tmp_path: Path) -> None:
    with synth(to=tmp_path):
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

    assert (tmp_path / ".mypy.ini").read_text() == dedent(
        """\
        [mypy]
        strict = True
        mypy_path = stubs
        plugins = returns.contrib.mypy.returns_plugin
        """
    )
