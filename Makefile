.PHONY: up down fclean rebuild migrate migration seed logs status shell test check help

COMPOSE = docker compose
BACKEND = $(COMPOSE) exec backend

up:
	@test -f .env || cp .env.example .env
	$(COMPOSE) up -d --build
	$(MAKE) migrate

down:
	$(COMPOSE) down

fclean:
	$(COMPOSE) down -v --remove-orphans

rebuild:
	$(COMPOSE) down
	$(COMPOSE) up -d --build
	$(MAKE) migrate

migrate:
	$(BACKEND) alembic upgrade head

migration:
	$(BACKEND) alembic revision --autogenerate -m "$(msg)"

seed:
	$(BACKEND) python -m scripts.seed

logs:
	$(COMPOSE) logs -f backend

status:
	$(COMPOSE) ps

shell:
	$(BACKEND) /bin/bash

test:
	$(BACKEND) pytest -v

check:
	@curl -sf http://localhost:8005/health && echo "\nHealth check OK" || (echo "Health check FAILED" && exit 1)

help:
	@echo "Available commands:"
	@echo "  make up                          Start all containers + migrate"
	@echo "  make down                        Stop containers"
	@echo "  make fclean                      Stop + remove volumes"
	@echo "  make rebuild                     Rebuild + restart"
	@echo "  make migrate                     Run Alembic migrations"
	@echo "  make migration msg=\"message\"     Create a new migration"
	@echo "  make seed                        Seed example data"
	@echo "  make logs                        Tail backend logs"
	@echo "  make status                      Show container status"
	@echo "  make shell                       Open shell in backend"
	@echo "  make test                        Run tests"
	@echo "  make check                       Health check"
	@echo "  make help                        Show this help"
