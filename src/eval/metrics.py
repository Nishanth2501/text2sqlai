import sqlglot
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

def canonical(sql: str) -> str:
    sql = (sql or "").strip().rstrip(";")
    try:
        return sqlglot.transpile(sql, read="ansi", write="ansi")[0]
    except Exception:
        return " ".join(sql.lower().split())

def exact_match(pred: str, gold: str) -> bool:
    return canonical(pred) == canonical(gold)

def safe_execute(engine: Engine, sql: str) -> pd.DataFrame:
    sql = (sql or "").strip()
    with engine.begin() as conn:
        return pd.read_sql(text(sql), conn)

def execution_match(engine: Engine, pred: str, gold: str) -> bool:
    try:
        a = safe_execute(engine, pred)
        b = safe_execute(engine, gold)
        # normalize ordering for a fair compare
        if list(a.columns) != list(b.columns):
            return False
        if len(a) != len(b):
            return False
        a_sorted = a.sort_values(list(a.columns)).reset_index(drop=True)
        b_sorted = b.sort_values(list(b.columns)).reset_index(drop=True)
        return a_sorted.equals(b_sorted)
    except Exception:
        return False