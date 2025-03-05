set fallback

install:
    uv sync --frozen

test:
    uv run pytest -s -v

lint:
  uv run ruff check .

clean:
  find . -name '*.pyc' -delete
  rm -rf .pytest_cache .ruff_cache dist

bump-version *args='':
  uv run bumpver update {{args}}
