default: cpn-cli

alias r := restore-env
alias v := bump-version

restore-env:
  [ -d '.venv' ] || uv sync --all-extras --no-dev --frozen

bump-version: restore-env
  uv run cz bump --no-verify
  uv run pre-commit run -a
  git commit --amend --no-edit

cpn-cli: restore-env
  uv run cpn-cli

clean: restore-env
  uvx cleanpy@0.5.1 .

precommit-run-all: restore-env
  uv run pre-commit run -a
