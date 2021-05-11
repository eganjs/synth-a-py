from pathlib import Path
from textwrap import dedent

from synth_a_py import TomlFile
from synth_a_py.base import synth


def test_toml(tmp_path: Path) -> None:
    with synth(to=tmp_path):
        TomlFile(
            "pyproject.toml",
            {
                "build-system": {
                    "requires": ["poetry>=0.12"],
                    "build-backend": "poetry.masonry.api",
                },
                "tool": {
                    "poetry": {
                        "name": "my-project",
                        "version": "0.1.0",
                        "description": "It's a great project",
                        "authors": ["Joseph Egan <...>"],
                        "dependencies": {
                            "python": "^3.8",
                            "dep42": {
                                "version": "1.0.0",
                                "extras": ["blue", "green"],
                            },
                        },
                        "dev-dependencies": {},
                    },
                },
            },
        )

    assert (tmp_path / "pyproject.toml").read_text() == dedent(
        """\
        [build-system]
        requires = [ "poetry>=0.12",]
        build-backend = "poetry.masonry.api"

        [tool.poetry]
        name = "my-project"
        version = "0.1.0"
        description = "It's a great project"
        authors = [ "Joseph Egan <...>",]

        [tool.poetry.dependencies]
        python = "^3.8"

        [tool.poetry.dev-dependencies]

        [tool.poetry.dependencies.dep42]
        version = "1.0.0"
        extras = [ "blue", "green",]
        """
    )
