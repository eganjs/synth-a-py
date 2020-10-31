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
    return `${this.content.map(e => e + "\n").join("")}`;
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
          'echo "::add-path::$HOME/.poetry/bin"',
        ].join("\n"),
      },
      {
        name: "install Poetry using pwsh",
        if: "matrix.os == 'windows'",
        run: [
          "(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python",
          'echo "::add-path::$HOME/.poetry/bin"',
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
      ".cache/",
      ".idea/",
      ".mypy_cache/",
      ".venv/",
      "dist/",
      "node_modules/",
    );

    const srcDir = options.name.replace(/-/g, "_");

    new File(this, `${srcDir}/__init__.py`, {
      content: [`__version__ = "${options.version}"`],
      readonly: false,
    });

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

    new File(this, "README.md", {
      content: [
        `# ${options.name}`,
        "",
        `![Build](${options.repository}/workflows/ci/badge.svg)`,
        "",
        `${options.description}`,
        "",
        "# Updating project config",
        "",
        "To do this make edits to the `.projenrc.js` file in the root of the project and run `npx projen` to update existing or generate new config. Please also use `npx prettier --trailing-comma all --write .projenrc.js` to format this file.",
      ],
      readonly: false,
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
            dependencies: options.dependencies,
            ["dev-dependencies"]: {
              black: "^20.8b1",
              flake8: "^3.8.4",
              isort: "^5.6",
              mypy: "^0.790",
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
            `MYPYPATH=./stubs poetry run mypy --strict ${srcDir} tests`,
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
  }
}

const project = new PoetryProject({
  name: "synth-a-py",
  version: "0.1.0",
  description: "Project configuration as code",
  authors: ["Joseph Egan <joseph.s.egan@gmail.com>"],
  repository: "https://github.com/eganjs/synth-a-py",
  dependencies: {
    python: "^3.6",
  },
  devDependencies: {},
  license: "MIT",
  copyrightOwner: "Joseph Egan",
  copyrightPeriod: "2020",
});

project.synth();
