# synth-a-py

![Build](https://github.com/eganjs/synth-a-py/workflows/ci/badge.svg)

Daring to tackle the problem of complex project configuration through code!

_synth-a-py_ is a framework to enable synthesising of project configuration using Python :snake:

The framework provides the means to define a project with multiple modules, that when synthesised, creates files such as `pyproject.toml`, `.github/workflows/{ci,cd}.yml` and `makefile`, all in the right places with consistency.

Although the project is written in Python, it is not limited to generating Python projects. Theoretically, it could be used for any problem that requires consistency between two or more files.

## Example usage

1. Create a new repo
```bash
mkdir my-project
cd my-project
git init
```

2. Add the below configuration as the file `./.synth.py`
```python
#!/usr/bin/env python
from textwrap import dedent

from synth_a_py import Dir, License, Project, SimpleFile, TomlFile, YamlFile

authors = ["Joseph Egan"]

project_name = "my-project"
project_description = "A project generated using synth-a-py"
project_version = "0.1.0"

project_import = project_name.lower().replace("-", "_")

spec = Project()
with spec:

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
                    "description": project_description,
                    "authors": authors,
                    "license": "MIT",
                    "dependencies": {
                        "python": "^3.6",
                    },
                    "dev-dependencies": {
                        "pytest": "^6",
                        "pyprojroot": "^0.2.0",
                        "synth-a-py": "*",
                    },
                },
            },
        },
    )

    License.MIT("2020", ", ".join(authors))

    SimpleFile(
        ".gitignore",
        dedent(
            """\
            *.egg
            *.egg-info/
            *.pyc
            .cache/
            .idea/
            .mypy_cache/
            .venv/
            dist/
            """
        ),
    )

    SimpleFile(
        "Makefile",
        dedent(
            """\
            .PHONEY: test
            test:
            \tpoetry install
            \tpoetry run pytest

            .PHONEY: synth
            synth:
            \tpoetry run ./synth.py
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

    with Dir(".github"):
        with Dir("workflows"):
            YamlFile(
                "ci.yml",
                {
                    "name": "ci",
                    "on": {
                        "pull_request": {
                            "branches": ["main"],
                        },
                        "push": {"branches": ["main"]},
                    },
                    "jobs": {
                        "test": {
                            "runs-on": "ubuntu-latest",
                            "steps": [
                                {
                                    "name": "checkout",
                                    "uses": "actions/checkout@v2",
                                },
                                {
                                    "name": "setup Python",
                                    "uses": "actions/setup-python@v2",
                                    "with": {
                                        "python-version": "3.9",
                                    },
                                },
                                {
                                    "name": "test",
                                    "run": dedent(
                                        """\
                                        pip install poetry
                                        make test
                                        """
                                    ),
                                },
                            ],
                        },
                    },
                },
            )

spec.synth()
```

3. Add execute permissions and run!
```bash
chmod +x ./.synth.py
./.synth.py
```

## Goals

- [ ] Use synth-a-py to manage project configs
  - Add support for:
    - [x] LICENSE
    - [x] TOML (for pyproject.toml)
    - [x] YAML (for GitHub Actions config)
      - [ ] GitHub Action workflow?
    - [x] INI (for flake8/mypy config)
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
