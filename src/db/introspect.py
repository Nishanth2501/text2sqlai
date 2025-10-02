from sqlalchemy import inspect
from sqlalchemy.engine import Engine

def get_schema_summary(engine: Engine) -> tuple[list[str], dict[str, list[str]]]:
    insp = inspect(engine)
    tables = insp.get_table_names()
    cols = {t: [c["name"] for c in insp.get_columns(t)] for t in tables}
    return tables, cols

def to_compact_schema(tables: list[str], cols: dict[str, list[str]]) -> str:
    lines = ["tables:"]
    for t in tables:
        lines.append(f"  {t}({', '.join(cols[t])})")
    return "\n".join(lines)
