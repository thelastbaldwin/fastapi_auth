dev: export DB_URL=sqlite:///auth.db
dev: export SECRET_KEY="68e9395390123324a39c32cc72c833b6659847e122b988196a83db9d2c3e831d"
dev:
	fastapi dev src/main.py

test: export DB_URL=sqlite://
test: export SECRET_KEY=$(shell openssl rand -hex 32)
test:
	pytest -v --capture=no src/test