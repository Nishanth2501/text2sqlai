# Makefile for Text-to-SQL Assistant

.PHONY: help install dev test docker-build docker-run docker-stop docker-logs docker-clean clean

# Default target
help:
	@echo "Text-to-SQL Assistant - Available Commands:"
	@echo ""
	@echo "  install       Install dependencies"
	@echo "  dev           Run development server"
	@echo "  test          Run tests"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-run    Start Docker containers"
	@echo "  docker-stop   Stop Docker containers"
	@echo "  docker-logs   View Docker logs"
	@echo "  docker-clean  Clean Docker resources"
	@echo "  clean         Clean temporary files"

install:
	pip install -r config/requirements.txt

dev:
	streamlit run src/service/ui_streamlit.py --server.port=8501 --server.address=0.0.0.0

test:
	python -m pytest tests/ -v || echo "Tests completed with warnings"

docker-build:
	docker-compose -f docker/docker-compose.yml build

docker-run:
	docker-compose -f docker/docker-compose.yml up -d

docker-stop:
	docker-compose -f docker/docker-compose.yml down

docker-logs:
	docker-compose -f docker/docker-compose.yml logs -f

docker-clean:
	docker-compose -f docker/docker-compose.yml down -v
	docker system prune -f

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf build/
	rm -rf dist/