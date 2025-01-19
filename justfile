default: run

alias r := restore-env
alias v := bump-verison
alias p := precommit-run-all

restore-env:
  [ -d '.venv' ] || uv sync --all-extras --all-groups

run:
  uv run cpn-cli

bump-verison:
  uv run cz bump

clean:
  uvx cleanpy@0.5.1 .

precommit-run-all:
  uv run pre-commit run -a
