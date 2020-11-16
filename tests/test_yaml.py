from pathlib import Path
from textwrap import dedent

from synth_a_py import Dir, Project, YamlFile


def test_yaml(tmp_path: Path) -> None:
    spec = Project()
    with spec:
        with Dir(".github"):
            with Dir("workflows"):
                YamlFile(
                    "ci.yaml",
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

    spec.synth(tmp_path)

    assert (tmp_path / ".github" / "workflows" / "ci.yaml").read_text() == dedent(
        """\
        name: ci
        on:
          pull_request:
            branches:
              - main
          push:
            branches:
              - main
        jobs:
          test:
            runs-on: ubuntu-latest
            steps:
              - name: checkout
                uses: actions/checkout@v2
              - name: setup Python
                uses: actions/setup-python@v2
                with:
                  python-version: '3.9'
              - name: test
                run: |
                  pip install poetry
                  make test
        """
    )
