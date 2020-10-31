# Contributing

Contributions are welcome and greatly appreciated!

## Types of Contributions

### Report Bugs

Report bugs using GitHub issues.

If you are reporting a bug, please include:
- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

### Write Documentation

This project could always use more documentation, whether as part of the official docs, in docstrings, or even on the web in blog posts, articles, and such.

### Submit Feedback

Send feedback by filing a GitHub issue.

If you are proposing a feature:
- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this project is driven by the community, and that contributing a Pull Request is the best way to ensure new features are implemented. The following sections explain how this can be done :)

## Get Started!

Ready to contribute? Here's how to get set up for local development.

1.  (Optional) [pyenv](https://github.com/pyenv/pyenv-installer) and it's
    [prerequisites](https://github.com/pyenv/pyenv/wiki/Common-build-problems#prerequisites)
    can be installed to manage python versions on your system. Once installed
    ensure it's configured correctly:
    ```shell script
    pyenv install 3.8.5 # or any prefered version of python
    pyenv global 3.8.5
    ```

2.  Ensure [Poetry](https://python-poetry.org/docs/#installation) is installed. If pyenv
    is installed (as above) then Poetry should automatically use the python version set as
    global to create it's virtual environments.

3.  Fork the repo on GitHub.

4.  Clone your fork locally:
    ```shell script
    git clone git@github.com:<username>/synth-a-py.git
    ```

5.  Install your local copy into a virtual environment. Refer to the
    README for instructions on how to do this.

6.  Create a branch for local development:
    ```shell script
    git checkout -b name-of-your-bugfix-or-feature
    ```
    Now you can make your changes locally.

7.  When you're done making changes, check that your changes pass the checks and tests:
    ```shell script
    make lint
    make test
    ```

8.  Commit your changes and push your branch to GitHub:
    ```shell script
    git add .
    git commit -m "Add / Remove / Fix / Refactor ..."
    git push origin name-of-your-bugfix-or-feature
    ```

9.  Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1.  The pull request should include tests.
2.  If the pull request adds functionality, the docs should be updated. Put your new functionality into a function with a docstring, and update the README.
3.  The pull request should work for all supported Python versions. The build actions in GitHub will help ensure this is the case.

## Publishing

A reminder for maintainers on how to publish. Make sure all your changes are committed and merged into the main branch. Then create a tag:
```shell script
git tag $(poetry version | awk '{print $2}')
git push $(poetry version | awk '{print $2}')
```
GitHub Actions will then verify the tag matches the project version in the commit, create a GitHub release and finally publish to the package repository.
