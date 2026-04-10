"""Makefile para comandos comuns"""
.PHONY: help install dev test lint format clean docker-up docker-down docs

help:
	@echo "Comandos disponíveis:"
	@echo "  make install       - Instala dependências"
	@echo "  make dev           - Inicia modo desenvolvimento"
	@echo "  make test          - Executa testes"
	@echo "  make lint          - Verifica código"
	@echo "  make format        - Formata código"
	@echo "  make clean         - Limpa arquivos temporários"
	@echo "  make docker-up     - Inicia Docker Compose"
	@echo "  make docker-down   - Para Docker Compose"
	@echo "  make docs          - Abre documentação"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && pip install -r requirements.txt

dev:
	@echo "Iniciando ambiente de desenvolvimento..."
	@echo "Backend: python main.py"
	@echo "Frontend (outro terminal): streamlit run app.py"

test:
	cd backend && pytest

lint:
	cd backend && flake8 app/ main.py
	cd backend && mypy app/ main.py

format:
	cd backend && black app/ main.py
	cd frontend && black app.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docs:
	@echo "Documentação:"
	@echo "- README.md: Visão geral"
	@echo "- QUICKSTART.md: Início rápido"
	@echo "- docs/API.md: Referência da API"
	@echo "- docs/ARCHITECTURE.md: Arquitetura"
	@echo "- docs/DEPLOYMENT.md: Deploy"
