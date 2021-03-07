"use strict";
const {
  FileBase,
  GithubWorkflow,
  License,
  Makefile,
  Project,
  TomlFile,
} = require("projen");

class File extends FileBase {
  constructor(project, name, options) {
    super(project, name, options);

    this.content = options && options.content ? options.content : [];
  }

  synthesizeContent(resolver) {
    return `${this.content.map((e) => e + "\n").join("")}`;
  }
}

class PoetryWorkflow extends GithubWorkflow {
  constructor(project, name, options) {
    super(project, name);

    this.on(options.trigger);

    this.on({
      workflow_dispatch: {}, // allow manual triggering
    });

    const bootstrapSteps = [
      {
        name: "checkout",
        uses: "actions/checkout@v2",
      },
      {
        name: "set up Python ${{ matrix.python-version }}",
        uses: "actions/setup-python@v2",
        with: {
          "python-version": "${{ matrix.python-version }}",
        },
      },
      {
        name: "get full Python version",
        id: "full-python-version",
        run:
          "echo ::set-output name=version::$(python -c \"import sys; print('-'.join(str(v) for v in sys.version_info))\")",
      },
      {
        name: "install Poetry using bash",
        if: "matrix.os == 'ubuntu' || matrix.os == 'macos'",
        run: [
          "curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python",
          'echo "$HOME/.poetry/bin" >> $GITHUB_PATH',
        ].join("\n"),
      },
      {
        name: "install Poetry using pwsh",
        if: "matrix.os == 'windows'",
        run: [
          "(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python",
          'echo "$HOME/.poetry/bin" | Out-File -FilePath $env:GITHUB_PATH -Encoding utf8 -Append',
        ].join("\n"),
      },
      {
        name: "set up cache",
        uses: "actions/cache@v2",
        id: "cache",
        with: {
          path: ".venv",
          key:
            "venv-${{ runner.os }}-${{ steps.full-python-version.outputs.version }}-${{ hashFiles('**/poetry.lock') }}",
        },
      },
      {
        name: "ensure cache is healthy",
        if: "steps.cache.outputs.cache-hit == 'true'",
        shell: "bash",
        run: "timeout 10s poetry run pip --version || rm -rf .venv",
      },
    ];

    const pythonJobs = !!options.pythonJobs ? options.pythonJobs : [];
    for (const job of pythonJobs) {
      const strategy = !!job.strategy ? job.strategy : {};
      strategy.matrix = !!strategy.matrix ? strategy.matrix : {};

      const matrix = strategy.matrix;
      matrix.os = !!matrix.os ? matrix.os : ["ubuntu", "macos", "windows"];
      matrix["python-version"] = !!matrix["python-version"]
        ? matrix["python-version"]
        : ["3.6", "3.7", "3.8", "3.9"];

      this.addJobs({
        [job.name]: {
          needs: !!job.needs ? job.needs : [],
          name: `${job.name} / \${{ matrix.os }} / \${{ matrix.python-version }}`,
          "runs-on": "${{ matrix.os }}-latest",
          strategy: strategy,
          steps: [...bootstrapSteps, ...job.steps],
        },
      });
    }

    const jobs = !!options.jobs ? options.jobs : [];
    for (const job of jobs) {
      this.addJobs({
        [job.name]: job,
      });
    }
  }
}

class PoetryProject extends Project {
  constructor(options) {
    super();

    this.gitignore.exclude(
      "*.egg",
      "*.egg-info/",
      "*.pyc",
      "*.so",
      ".cache/",
      ".idea/",
      ".mypy_cache/",
      ".venv/",
      "dist/",
      "build/",
      "node_modules/",
    );

    const srcDir = options.name.replace(/-/g, "_");

    new File(this, `${srcDir}/py.typed`);

    new File(this, "tests/__init__.py");

    new File(this, "tests/test_version.py", {
      content: [
        "import toml",
        "from pyprojroot import here",
        "",
        `from ${srcDir} import __version__`,
        "",
        "",
        "def test_version() -> None:",
        '    pyproject = toml.load(here("pyproject.toml"))',
        '    pyproject_version = pyproject["tool"]["poetry"]["version"]',
        "",
        "    assert __version__ == pyproject_version",
      ],
    });

    new File(this, "stubs/pyprojroot.pyi", {
      content: [
        "from typing import Tuple, Optional",
        "from pathlib import Path",
        "",
        "def here(relative_project_path: str) -> Path: ...",
      ],
    });

    new File(this, ".flake8", {
      content: ["[flake8]", "max-line-length = 88", "extend-ignore = E203"],
    });

    new File(this, ".mypy.ini", {
      content: [
        "[mypy]",
        "strict = True",
        "mypy_path = stubs",
        "plugins = returns.contrib.mypy.returns_plugin",
      ],
    });

    new File(this, "build.py", {
      content: [
        "from typing import Any, Dict",
        "",
        "from mypyc.build import mypycify  # type: ignore",
        "",
        "",
        "def build(setup_kwargs: Dict[str, Any]) -> Dict[str, Any]:",
        "    setup_kwargs.update({",
        '        "ext_modules": mypycify(["synth_a_py"], opt_level="3")',
        "    })",
        "    return setup_kwargs",
        "",
        "",
        'if __name__ == "__main__":',
        "    print(build({}))",
      ],
    });

    new TomlFile(this, "pyproject.toml", {
      obj: {
        ["build-system"]: {
          requires: ["poetry>=0.12"],
          ["build-backend"]: "poetry.masonry.api",
        },
        tool: {
          poetry: {
            name: options.name,
            version: options.version,
            description: options.description,
            authors: options.authors,
            license: options.license,
            repository: options.repository,
            readme: "README.md",
            build: {
              script: "build.py",
            },
            dependencies: options.dependencies,
            ["dev-dependencies"]: {
              black: "^20.8b1",
              flake8: "^3.8.4",
              isort: "^5.6",
              mypy: "^0.812",
              pyprojroot: "^0.2.0",
              pytest: "^6",
              toml: "^0.10.1",
              ...(!!options.devDependencies ? options.devDependencies : {}),
            },
            source: options.packageRepositories,
          },
        },
      },
    });

    new TomlFile(this, "poetry.toml", {
      obj: {
        virtualenvs: {
          ["in-project"]: true,
        },
      },
    });

    new License(this, options.license, {
      copyrightOwner: options.copyrightOwner,
      copyrightPeriod: options.copyrightPeriod,
    });

    new Makefile(this, "Makefile", {
      all: ["lint", "test"],
      rules: [
        {
          phony: true,
          targets: ["lint"],
          prerequisites: [".venv"],
          recipe: [
            `poetry run mypy ${srcDir} tests`,
            `poetry run flake8 ${srcDir} tests`,
            `poetry run isort --check-only --profile black ${srcDir} tests`,
            `poetry run black --check --diff ${srcDir} tests`,
          ],
        },
        {
          phony: true,
          targets: ["fmt"],
          prerequisites: [".venv"],
          recipe: [
            `poetry run isort --profile black ${srcDir} tests`,
            `poetry run black ${srcDir} tests`,
          ],
        },
        {
          phony: true,
          targets: ["test"],
          prerequisites: [".venv"],
          recipe: ["poetry run pytest --verbose --capture=no"],
        },
        {
          phony: true,
          targets: ["publish"],
          prerequisites: ["dist"],
          recipe: ["poetry publish"],
        },
        {
          phony: true,
          targets: ["dist"],
          prerequisites: [
            `dist/${options.name}-${options.version}.tar.gz`,
            `dist/${srcDir}-${options.version}-py3-none-any.whl`,
          ],
        },
        {
          targets: [
            `dist/${options.name}-${options.version}.tar.gz`,
            `dist/${srcDir}-${options.version}-py3-none-any.whl`,
          ],
          prerequisites: [`$(shell find ${srcDir} -type f -name '*.py')`],
          recipe: ["poetry build"],
        },
        {
          targets: [".venv"],
          prerequisites: ["poetry.lock"],
          recipe: ["poetry install", "@touch -c .venv"],
        },
        {
          targets: ["poetry.lock"],
          prerequisites: ["pyproject.toml"],
          recipe: ["poetry lock", "@touch -c poetry.lock"],
        },
      ],
    });

    new PoetryWorkflow(this, "ci", {
      trigger: {
        pull_request: {
          branches: ["main"],
        },
        push: {
          branches: ["main"],
        },
      },
      pythonJobs: [
        {
          name: "lint",
          strategy: {
            matrix: {
              os: ["ubuntu"],
              "python-version": ["3.9"],
            },
          },
          steps: [
            {
              name: "lint",
              run: "make lint",
            },
          ],
        },
        {
          name: "test",
          needs: ["lint"],
          steps: [
            {
              name: "test",
              run: "make test",
            },
          ],
        },
      ],
      jobs: [
        {
          if: "github.actor == 'dependabot[bot]'",
          needs: ["lint", "test"],
          name: "dependabot-automerge",
          "runs-on": "ubuntu-latest",
          steps: [
            {
              uses: "actions/github-script@v3",
              with: {
                "github-token": "${{ secrets.GITHUB_TOKEN }}",
                script: [
                  "github.pullRequests.createReview({",
                  "  owner: context.payload.repository.owner.login,",
                  "  repo: context.payload.repository.name,",
                  "  pull_number: context.payload.pull_request.number,",
                  "  event: 'APPROVE'",
                  "})",
                  "github.pullRequests.merge({",
                  "  owner: context.payload.repository.owner.login,",
                  "  repo: context.payload.repository.name,",
                  "  pull_number: context.payload.pull_request.number",
                  "})",
                ].join("\n"),
              },
            },
          ],
        },
      ],
    });

    new PoetryWorkflow(this, "publish", {
      trigger: {
        push: {
          tags: ["*.*.*"],
        },
      },
      pythonJobs: [
        {
          name: "publish",
          strategy: {
            matrix: {
              os: ["ubuntu"],
              "python-version": ["3.8"],
            },
          },
          steps: [
            {
              name: "get tag",
              id: "tag",
              run: "echo ::set-output name=tag::${GITHUB_REF#refs/tags/}",
            },
            {
              name: "build dist",
              run: "make dist",
            },
            {
              name: "check tag matches version",
              run: [
                "ls",
                `dist/${options.name}-\${{ steps.tag.outputs.tag }}.tar.gz`,
                `dist/${options.name}-${options.version}.tar.gz`,
                `dist/${srcDir}-\${{ steps.tag.outputs.tag }}-py3-none-any.whl`,
                `dist/${srcDir}-${options.version}-py3-none-any.whl`,
              ].join(" "),
            },
            {
              name: "create release",
              id: "create_release",
              uses: "actions/create-release@v1",
              env: {
                GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}",
              },
              with: {
                tag_name: "${{ steps.tag.outputs.tag }}",
                release_name: "${{ steps.tag.outputs.tag }}",
                draft: false,
                prerelease: false,
              },
            },
            {
              name: "upload release asset",
              uses: "actions/upload-release-asset@v1",
              env: {
                GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}",
              },
              with: {
                upload_url: "${{ steps.create_release.outputs.upload_url }}",
                asset_path: `dist/${options.name}-${options.version}.tar.gz`,
                asset_name: `${options.name}-${options.version}.tar.gz`,
                asset_content_type: "application/gzip",
              },
            },
            {
              name: "publish to pypi",
              env: {
                POETRY_PYPI_TOKEN_PYPI: "${{ secrets.PYPI_TOKEN }}",
              },
              run: "make publish",
            },
          ],
        },
      ],
    });

    new File(this, "CONTRIBUTING.md", {
      content: [
        "# Contributing",
        "",
        "Contributions are welcome and greatly appreciated!",
        "",
        "## Types of Contributions",
        "",
        "### Report Bugs",
        "",
        "Report bugs using GitHub issues.",
        "",
        "If you are reporting a bug, please include:",
        "- Your operating system name and version.",
        "- Any details about your local setup that might be helpful in troubleshooting.",
        "- Detailed steps to reproduce the bug.",
        "",
        "### Fix Bugs",
        "",
        'Look through the GitHub issues for bugs. Anything tagged with "bug" and "help wanted" is open to whoever wants to implement it.',
        "",
        "### Implement Features",
        "",
        'Look through the GitHub issues for features. Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.',
        "",
        "### Write Documentation",
        "",
        "This project could always use more documentation, whether as part of the official docs, in docstrings, or even on the web in blog posts, articles, and such.",
        "",
        "### Submit Feedback",
        "",
        "Send feedback by filing a GitHub issue.",
        "",
        "If you are proposing a feature:",
        "- Explain in detail how it would work.",
        "- Keep the scope as narrow as possible, to make it easier to implement.",
        "- Remember that this project is driven by the community, and that contributing a Pull Request is the best way to ensure new features are implemented. The following sections explain how this can be done :)",
        "",
        "## Get Started!",
        "",
        "Ready to contribute? Here's how to get set up for local development.",
        "",
        "1.  (Optional) [pyenv](https://github.com/pyenv/pyenv-installer) and it's",
        "    [prerequisites](https://github.com/pyenv/pyenv/wiki/Common-build-problems#prerequisites)",
        "    can be installed to manage python versions on your system. Once installed",
        "    ensure it's configured correctly:",
        "    ```shell script",
        "    pyenv install 3.8.5 # or any prefered version of python",
        "    pyenv global 3.8.5",
        "    ```",
        "",
        "2.  Ensure [Poetry](https://python-poetry.org/docs/#installation) is installed. If pyenv",
        "    is installed (as above) then Poetry should automatically use the python version set as",
        "    global to create it's virtual environments.",
        "",
        "3.  Fork the repo on GitHub.",
        "",
        "4.  Clone your fork locally:",
        "    ```shell script",
        `    git clone git@github.com:<username>/${options.name}.git`,
        "    ```",
        "",
        "5.  Install your local copy into a virtual environment. Refer to the",
        "    README for instructions on how to do this.",
        "",
        "6.  Create a branch for local development:",
        "    ```shell script",
        "    git checkout -b name-of-your-bugfix-or-feature",
        "    ```",
        "    Now you can make your changes locally.",
        "",
        "7.  When you're done making changes, check that your changes pass the checks and tests:",
        "    ```shell script",
        "    make lint",
        "    make test",
        "    ```",
        "",
        "8.  Commit your changes and push your branch to GitHub:",
        "    ```shell script",
        "    git add .",
        '    git commit -m "Add / Remove / Fix / Refactor ..."',
        "    git push origin name-of-your-bugfix-or-feature",
        "    ```",
        "",
        "9.  Submit a pull request through the GitHub website.",
        "",
        "## Pull Request Guidelines",
        "",
        "Before you submit a pull request, check that it meets these guidelines:",
        "",
        "1.  The pull request should include tests.",
        "2.  If the pull request adds functionality, the docs should be updated. Put your new functionality into a function with a docstring, and update the README.",
        "3.  The pull request should work for all supported Python versions. The build actions in GitHub will help ensure this is the case.",
        "",
        "## Publishing",
        "",
        "A reminder for maintainers on how to publish. Make sure all your changes are committed and merged into the main branch. Then create a tag:",
        "```shell script",
        "git tag $(poetry version | awk '{print $2}')",
        "git push $(poetry version | awk '{print $2}')",
        "```",
        "GitHub Actions will then verify the tag matches the project version in the commit, create a GitHub release and finally publish to the package repository.",
      ],
    });
  }
}

const project = new PoetryProject({
  name: "synth-a-py",
  version: "1.6.0",
  description: "Project configuration as code",
  authors: ["Joseph Egan <joseph.s.egan@gmail.com>"],
  repository: "https://github.com/eganjs/synth-a-py",
  dependencies: {
    python: "^3.6",
    returns: "^0.14.0",
    contextvars: {
      version: "^2.4",
      python: "~3.6",
    },
    "ruamel.yaml": "^0.16.12",
    toml: "^0.10.1",
  },
  devDependencies: {
    jedi: "^0.17.2",
    "typing-extensions": "^3.7.4.3",
  },
  license: "MIT",
  copyrightOwner: "Joseph Egan",
  copyrightPeriod: "2020",
});

project.synth();
