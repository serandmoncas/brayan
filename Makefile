.PHONY: dev test lint install bridge deps

install:
	pip install -r requirements.txt
	cd src/bridge && npm install || true

deps:
	pip install -r requirements.txt

lint:
	ruff check src tests

test:
	pytest -q

dev:
	# Corre orchestrator (FastAPI) y el bridge Node en paralelo
	python3 -m uvicorn src.orchestrator:app --host 0.0.0.0 --port 8000 &
	cd src/bridge && node wa_bridge.js

bridge:
	cd src/bridge && node wa_bridge.js
