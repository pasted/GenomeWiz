.PHONY: dev test fmt lint
dev:
	uvicorn app.main:app --reload

test:
	pytest -q --maxfail=1

fmt:
	ruff check --select I --fix .
	ruff check --fix .

lint:
	ruff check .
	mypy app

test-db:
	genomewiz-init-db && genomewiz-seed-demo && pytest -q
