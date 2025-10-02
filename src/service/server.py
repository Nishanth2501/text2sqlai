from fastapi import FastAPI
from pydantic import BaseModel
from src.db.connect import get_engine
from src.db.introspect import get_schema_summary, to_compact_schema
from src.nlp.generator import T2SQLGenerator
from src.nlp.safety import ensure_limit, is_safe_select
import pandas as pd
from sqlalchemy import text

app = FastAPI(title="Text-to-SQL API", version="0.1.0")

class Health(BaseModel):
    status: str
    tables: list[str] | None = None

class Ask(BaseModel):
    question: str
    execute: bool = True
    db_url: str = "sqlite:///data/demo.sqlite"

@app.get("/health", response_model=Health)
def health():
    try:
        eng = get_engine("sqlite:///data/demo.sqlite")
        tables, _ = get_schema_summary(eng)
        return Health(status="ok", tables=tables)
    except Exception:
        return Health(status="ok", tables=[])

@app.post("/text2sql")
def text2sql(req: Ask):
    eng = get_engine(req.db_url)
    tables, cols = get_schema_summary(eng)
    schema_txt = to_compact_schema(tables, cols)
    gen = T2SQLGenerator(schema_txt=schema_txt)

    sql_raw = gen.generate(req.question)
    sql_safe = ensure_limit(sql_raw)

    if not is_safe_select(sql_safe):
        return {"sql": sql_safe, "error": "Generated SQL failed safety checks."}

    if not req.execute:
        return {"sql": sql_safe}

    try:
        with eng.begin() as conn:
            df = pd.read_sql(text(sql_safe), conn)
        return {
            "sql": sql_safe,
            "rows": int(len(df)),
            "data": df.head(50).to_dict(orient="records")
        }
    except Exception as e:
        return {"sql": sql_safe, "error": str(e)}