# Install all dependencies
install:
	poetry install

# Activate virtualenv
shell:
	poetry shell

# Code format
format:
	blue .
	isort .

lint:
	blue --check .
	isort --check .
	prospector --no-autodetect --with-tool pydocstyle .

# Run tests
test:
	pytest -v

# Run security tests
sec:
	pip-audit
	safety check --full-report

# Export Poetry dependencies to requirements.txt file format
req_export:
	poetry export --without-hashes --format requirements.txt --output requirements.txt

# Export Poetry dependencies to requirements.txt file format with dev dependencies
req_export_with_dev:
	poetry export --without-hashes --dev --format requirements.txt --output requirements.txt

# Clean cache files
clean_cache_files:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -type d | xargs rm -fr
	find . -name '.pytest_cache' -type d | xargs rm -fr