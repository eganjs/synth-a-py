from pathlib import Path
from textwrap import dedent
from typing import List

from typing_extensions import TypedDict

from synth_a_py import Dir, PoetryModule, auto_synth
from synth_a_py.poetry.versions import DependencyDict, Managed


# allows mypy to correctly type check `**` statements
class CommonMetadata(TypedDict):
    version: str
    authors: List[str]
    license: str
    dependency_management: DependencyDict


def test_python_module_poetry(tmp_path: Path) -> None:
    with auto_synth(tmp_path):
        common_metadata: CommonMetadata = {
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
            **common_metadata,
            dependencies={},
            dev_dependencies={
                **common_dev_dependencies,
            },
        )

        with Dir("lambdas"):
            PoetryModule(
                name="alpha",
                description="Alpha lambda",
                **common_metadata,
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
                **common_metadata,
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

    assert (tmp_path / "deployment" / "pyproject.toml").read_text() == dedent(
        """\
        [build-system]
        requires = [ "poetry-core>=1.0.0",]
        build-backend = "poetry.core.masonry.api"

        [tool.poetry]
        name = "deployment"
        description = "Code to deploy lambdas"
        version = "1.0.0"
        authors = [ "Joseph Egan <...>",]
        license = "MIT"

        [tool.poetry.dev-dependencies]
        pytest = "^5"
        """
    )

    assert (tmp_path / "lambdas" / "alpha" / "pyproject.toml").read_text() == dedent(
        """\
        [build-system]
        requires = [ "poetry-core>=1.0.0",]
        build-backend = "poetry.core.masonry.api"

        [tool.poetry]
        name = "alpha"
        description = "Alpha lambda"
        version = "1.0.0"
        authors = [ "Joseph Egan <...>",]
        license = "MIT"

        [tool.poetry.dependencies]
        python = "^3.8"

        [tool.poetry.dev-dependencies]
        pytest = "^5"

        [tool.poetry.dependencies.dep42]
        version = "1.0.0"
        extras = [ "blue", "green",]
        """
    )

    assert (tmp_path / "lambdas" / "beta" / "pyproject.toml").read_text() == dedent(
        """\
        [build-system]
        requires = [ "poetry-core>=1.0.0",]
        build-backend = "poetry.core.masonry.api"

        [tool.poetry]
        name = "beta"
        description = "Beta lambda"
        version = "1.0.0"
        authors = [ "Joseph Egan <...>",]
        license = "MIT"

        [tool.poetry.dependencies]
        python = "^3.8"
        pandas = "1.2.0"

        [tool.poetry.dev-dependencies]
        pytest = "^5"

        [tool.poetry.dependencies.dep42]
        version = "1.0.0"
        extras = [ "blue", "green",]
        """
    )
