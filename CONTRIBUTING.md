# Contributing to kdev

Thanks for helping. The full guide lives in the README, under
[Contributing](README.md#contributing): how to set up, how to try a change
against real Kaggle without spending GPU quota, how the code is laid out, and
what a pull request needs.

The short version:

- For anything bigger than a fix, open an issue first.
- `uv sync && uv run pre-commit install`, then `uv run pytest`.
- A bug fix comes with a test that fails without it.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/).
- Note what users will notice under `## [Unreleased]` in `CHANGELOG.md`.
- Security issues go through [SECURITY.md](SECURITY.md), never a public issue.

By taking part you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
