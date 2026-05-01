.PHONY: setup clean test run app charts sql

PYTHON := .venv/bin/python
PIP := .venv/bin/pip

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

clean:
	rm -f data/processed/*.csv data/processed/*.duckdb data/processed/*.duckdb.wal charts/*.png charts/*.html charts/*.md

run:
	$(PYTHON) src/clean_data.py
	$(PYTHON) src/run_sql_analysis.py
	$(PYTHON) src/visualize.py
	$(PYTHON) src/model.py

sql:
	$(PYTHON) src/run_sql_analysis.py

charts:
	$(PYTHON) src/visualize.py

test:
	$(PYTHON) -m pytest

app:
	$(PYTHON) -m streamlit run app/dashboard.py
