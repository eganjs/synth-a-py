# synth-a-py

![Build](https://github.com/eganjs/synth-a-py/workflows/ci/badge.svg)

Project configuration as code

## Example usage

```python
#!/usr/bin/env python
from textwrap import dedent

from synth_a_py import Dir, Project, SimpleFile, TomlFile

project_name = "sample-project"
project_version = "0.1.0"
project_import = project_name.lower().replace("-", "_")

spec = Project()
with spec:
    with Dir(".github"):
        with Dir("workflows"):
            SimpleFile(
                "ci.yml",
                dedent(
                    """\
                    ...
                    """
                ),
            )
            SimpleFile(
                "publish.yml",
                dedent(
                    """\
                    ...
                    """
                ),
            )

    TomlFile(
        "pyproject.toml",
        {
            "build-system": {
                "requires": ["poetry>=0.12"],
                "build-backend": "poetry.masonry.api",
            },
            "tool": {
                "poetry": {
                    "name": project_name,
                    "version": project_version,
                    "description": "A sample project generated using synth-a-py",
                    "authors": ["Joseph Egan"],
                    "dependencies": {
                        "python": "^3.6",
                    },
                    "dev-dependencies": {
                        "pytest": "^6",
                        "pyprojroot": "^0.2.0",
                    },
                },
            },
        },
    )

    SimpleFile(
        "Makefile",
        dedent(
            """\
            .PHONEY: test
            test:
            \tpoetry install
            \tpoetry run pytest
            """
        ),
    )

    with Dir(project_import):
        SimpleFile(
            "__init__.py",
            dedent(
                f"""\
                __version__ = "{project_version}"
                """
            ),
        )

    with Dir("tests"):
        SimpleFile(
            "test_version.py",
            dedent(
                f"""\
		import toml
		from pyprojroot import here

		from {project_import} import __version__


		def test_version() -> None:
		    pyproject = toml.load(here("pyproject.toml"))
		    pyproject_version = pyproject["tool"]["poetry"]["version"]

		    assert __version__ == pyproject_version
                """
            ),
        )

spec.synth()
```

## Goals

- [ ] Use synth-a-py to manage project configs
  - Add support for:
    - [x] LICENSE
    - [x] TOML (for pyproject.toml)
    - [ ] YAML (for GitHub Actions config)
      - [ ] GitHub Action workflow?
    - [ ] INI (for flake8/mypy config)
    - [ ] Makefile
    - [ ] .gitignore
  - Add ./synth.py
- Templates:
  - [ ] Poetry
  - [ ] setup.py
  - [ ] Pipenv
- In-repo examples:
  - [ ] Minimal
  - [ ] Monorepo

## Updating project config

To do this make edits to the `.projenrc.js` file in the root of the project and run `npx projen` to update existing or generate new config. Please also use `npx prettier --trailing-comma all --write .projenrc.js` to format this file.
