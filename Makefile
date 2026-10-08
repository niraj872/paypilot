.PHONY: up down logs test audit
up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f

test:
	docker compose run --rm backend pytest

audit:
	python scripts/audit.py
