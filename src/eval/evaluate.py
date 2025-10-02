import argparse, random, json
from datasets import load_dataset
from src.nlp.generator import T2SQLGenerator
from src.nlp.safety import ensure_limit, is_safe_select
from src.eval.metrics import exact_match, execution_match
from src.db.connect import get_engine
from src.db.introspect import get_schema_summary, to_compact_schema

def eval_gretel_em(sample_size: int = 200):
    ds = load_dataset("gretelai/synthetic_text_to_sql")
    pool = list(ds["test"])
    random.shuffle(pool)
    pool = pool[:sample_size]

    correct = 0
    total = 0

    for ex in pool:
        q = ex.get("prompt") or ex.get("question") or ""
        gold = ex.get("sql") or ex.get("query") or ""
        schema = ex.get("schema") or ex.get("db_schema") or ""
        if not q or not gold:
            continue

        gen = T2SQLGenerator(schema_txt=schema)
        pred = gen.generate(q)
        pred = ensure_limit(pred)

        total += 1
        if exact_match(pred, gold):
            correct += 1

    acc = correct / total if total else 0.0
    print(f"[Gretel EM] samples={total} exact_match={acc:.3f}")

def eval_local_exec(local_jsonl: str, db_url: str):
    # local file with records: {"question": "...", "sql": "..."}; schema comes from the DB itself
    from pathlib import Path
    from src.eval.metrics import execution_match
    lines = Path(local_jsonl).read_text().strip().splitlines()
    cases = [json.loads(ln) for ln in lines if ln.strip()]

    eng = get_engine(db_url)
    tables, cols = get_schema_summary(eng)
    schema_txt = to_compact_schema(tables, cols)
    gen = T2SQLGenerator(schema_txt=schema_txt)

    ok = 0
    total = 0
    for c in cases:
        q, gold = c["question"], c["sql"]
        pred = ensure_limit(gen.generate(q))
        if not is_safe_select(pred):
            continue
        total += 1
        if execution_match(eng, pred, gold):
            ok += 1
    acc = ok / total if total else 0.0
    print(f"[Local Execution] cases={total} exec_accuracy={acc:.3f}")

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gretel-em", help="Exact-match on Gretel test split")
    g.add_argument("--samples", type=int, default=100)

    l = sub.add_parser("local-exec", help="Execution accuracy on local eval set")
    l.add_argument("--file", default="artifacts/eval_local.jsonl")
    l.add_argument("--db", default="sqlite:///data/demo.sqlite")

    args = ap.parse_args()
    if args.cmd == "gretel-em":
        eval_gretel_em(sample_size=args.samples)
    elif args.cmd == "local-exec":
        eval_local_exec(args.file, args.db)

if __name__ == "__main__":
    main()