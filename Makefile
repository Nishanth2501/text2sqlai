.PHONY: install api ui
install:
	python3 -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -r requirements.txt

api:
	. .venv/bin/activate && uvicorn src.service.server:app --reload --host 0.0.0.0 --port 8000

ui:
	. .venv/bin/activate && PYTHONPATH=. streamlit run src/service/ui_streamlit.py

ui-alt:
	. .venv/bin/activate && PYTHONPATH=. streamlit run src/ui/app.py
eval-em:
	. .venv/bin/activate && python -m src.eval.evaluate gretel-em --samples 50

eval-local:
	. .venv/bin/activate && python -m src.eval.evaluate local-exec --file artifacts/eval_local.jsonl --db sqlite:///data/demo.sqlite

serve:
	. .venv/bin/activate && uvicorn src.service.server:app --reload --port 8000

eval-report:
	. .venv/bin/activate && python -m src.eval.run_report --gretel_samples 75 --local_file artifacts/eval_local.jsonl --db sqlite:///data/demo.sqlite --out artifacts/eval_report.json
