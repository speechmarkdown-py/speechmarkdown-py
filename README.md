# SpeechMarkdown

[![PyPI version](https://img.shields.io/pypi/v/speechmarkdown.svg)](https://pypi.org/project/speechmarkdown/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/speechmarkdown)
[![Documentation](https://img.shields.io/badge/docs-speechmarkdown-blue?label=documentation)](https://speechmarkdown-py.github.io/speechmarkdown-py/)

Speech Markdown library for Python. 
This is a Python port of the original [speechmarkdown-js](https://github.com/speechmarkdown/speechmarkdown-js).

## Installation

```bash
$ pip install speechmarkdown
```

## Usage

For usage, please consult the [docs](docs/README.md).

## Development Setup

We use [`mise`](https://mise.jdx.dev/) for managing the development environment and tooling, and `poetry` for python package dependency management.

1. Install `mise`, if you haven't already.
2. In the project root, run `mise install` to install python and poetry.
3. Run `poetry install`
4. Run tests with `make test` or full CI suite with `make lint-type-test`.
