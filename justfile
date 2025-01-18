default: cpn-cli

alias r := restore-env
alias v := bump-version

restore-env:
  [ -d '.venv' ] || uv sync --all-extras --all-groups

bump-version:
  uv run cz bump --no-verify
  uv run pre-commit run -a
  git commit --amend --no-edit

cpn-cli:
  uv run cpn-cli

clean:
  uvx cleanpy@0.5.1 .

precommit-run-all:
  pre-commit run -a
