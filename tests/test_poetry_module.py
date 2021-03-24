from pathlib import Path
from textwrap import dedent

from synth_a_py import Dir, PoetryModule, auto_synth
from synth_a_py.poetry.versions import Managed


def test_python_module_poetry(tmp_path: Path) -> None:
    with auto_synth(tmp_path):
        common_metadata = {
            "version": "1.0.0",
            "authors": ["Joseph Egan <...>"],
            "license": "MIT",
            "dependency_management": {
                "pandas": "1.2.0",
            },
        }

        common_dependencies = {
            "python": "^3.8",
        }

        common_dev_dependencies = {
            "pytest": "^5",
        }

        PoetryModule(
            name="deployment",
            description="Code to deploy lambdas",
            **common_metadata,  # type: ignore
            dependencies={},
            dev_dependencies={
                **common_dev_dependencies,
            },
        )

        with Dir("lambdas"):
            PoetryModule(
                name="alpha",
                description="Alpha lambda",
                **common_metadata,  # type: ignore
                dependencies={
                    **common_dependencies,
                    "dep42": {
                        "version": "1.0.0",
                        "extras": ["blue", "green"],
                    },
                },
                dev_dependencies={
                    **common_dev_dependencies,
                },
            )

            PoetryModule(
                name="beta",
                description="Beta lambda",
                **common_metadata,  # type: ignore
                dependencies={
                    **common_dependencies,
                    "dep42": {
                        "version": "1.0.0",
                        "extras": ["blue", "green"],
                    },
                    "pandas": Managed,
                },
                dev_dependencies={
                    **common_dev_dependencies,
                },
            )

    file_path = tmp_path / "file"
    assert file_path.stat().st_mode & 0o777 == 0o444
    assert file_path.read_text() == dedent(
        """\
        Lorem ipsum dolor sit amet
        consectetur adipiscing elit
        Cras eros purus
        aliquet ac magna ut
        fermentum cursus turpis
        """
    )
