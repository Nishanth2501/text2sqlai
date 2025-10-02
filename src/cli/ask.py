import argparse
from sqlalchemy import text
import pandas as pd

from src.db.connect import get_engine
from src.db.introspect import get_schema_summary, to_compact_schema
from src.nlp.generator import T2SQLGenerator
from src.nlp.safety import is_safe_select, ensure_limit

def main():
    ap = argparse.ArgumentParser(description="Text-to-SQL dry-run")
    ap.add_argument("question", type=str, help="Natural language question")
    ap.add_argument("--db", default="sqlite:///data/demo.sqlite")
    ap.add_argument("--execute", action="store_true", help="Execute SQL after generation")
    args = ap.parse_args()

    eng = get_engine(args.db)
    tables, cols = get_schema_summary(eng)
    schema_txt = to_compact_schema(tables, cols)

    gen = T2SQLGenerator(schema_txt)
    sql_raw = gen.generate(args.question)
    sql_safe = ensure_limit(sql_raw)

    print("---- Generated SQL ----")
    print(sql_safe)
    print("-----------------------")

    if not is_safe_select(sql_safe):
        print("Blocked: SQL failed safety checks.")
        return

    if args.execute:
        try:
            with eng.begin() as conn:
                df = pd.read_sql(text(sql_safe), conn)
            print(f"\nRows: {len(df)} (showing up to 20)")
            print(df.head(20).to_string(index=False))
        except Exception as e:
            print(f"\nExecution error: {e}")

if __name__ == "__main__":
    main()