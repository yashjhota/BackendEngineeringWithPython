test:
	pytest tests/ -v

api:
	uvicorn main:app --reload

lint:
	ruff check . --fix  && ruff format