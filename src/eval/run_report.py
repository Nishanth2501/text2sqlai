import argparse, json, random, time, platform
from pathlib import Path

import pandas as pd
from datasets import load_dataset
from sqlalchemy import text

from src.db.connect import get_engine
from src.db.introspect import get_schema_summary, to_compact_schema
from src.eval.metrics import exact_match, execution_match
from src.nlp.generator import T2SQLGenerator
from src.nlp.safety import ensure_limit, is_safe_select

# Try to read model name from generator (fallback if not available)
try:
    from src.nlp.generator import BASE_MODEL as _BASE_MODEL
    DEFAULT_MODEL_NAME = _BASE_MODEL
except Exception:
    DEFAULT_MODEL_NAME = "google/flan-t5-base (pretrained)"

def eval_gretel_em(sample_size: int = 75, seed: int = 42) -> dict:
    """Exact-match (string-level) evaluation on Gretel test split subset."""
    ds = load_dataset("gretelai/synthetic_text_to_sql")
    test = ds["test"]
    idxs = list(range(len(test)))
    random.Random(seed).shuffle(idxs)
    idxs = idxs[:sample_size]

    total, correct = 0, 0
    diagnostics = []  # keep a few examples for the report

    for i in idxs:
        ex = test[i]
        # Gretel fields:
        q = (ex.get("sql_prompt") or "").strip()
        gold = (ex.get("sql") or "").strip()
        schema = (ex.get("sql_context") or "").strip()
        if not q or not gold:
            continue

        gen = T2SQLGenerator(schema_txt=schema)
        pred = gen.generate(q).strip()
        pred = ensure_limit(pred)

        total += 1
        is_em = exact_match(pred, gold)
        correct += int(is_em)

        if len(diagnostics) < 8:  # store a handful of examples
            diagnostics.append({
                "question": q,
                "pred_sql": pred,
                "gold_sql": gold,
                "exact_match": bool(is_em)
            })

    acc = correct / total if total else 0.0
    return {
        "samples": total,
        "correct": correct,
        "accuracy": round(acc, 4),
        "examples": diagnostics
    }

def eval_local_exec(local_jsonl: str, db_url: str) -> dict:
    """Execution accuracy against your demo DB using a small local eval set."""
    p = Path(local_jsonl)
    if not p.exists():
        return {"samples": 0, "correct": 0, "accuracy": 0.0, "note": f"missing file: {local_jsonl}"}

    lines = [ln for ln in p.read_text().splitlines() if ln.strip()]
    cases = [json.loads(ln) for ln in lines]

    eng = get_engine(db_url)
    tables, cols = get_schema_summary(eng)
    schema_txt = to_compact_schema(tables, cols)
    gen = T2SQLGenerator(schema_txt=schema_txt)

    total, correct = 0, 0
    diagnostics = []

    for c in cases:
        q = c["question"]
        gold = c["sql"].strip()

        pred = ensure_limit(gen.generate(q).strip())
        if not is_safe_select(pred):
            diagnostics.append({"question": q, "pred_sql": pred, "gold_sql": gold, "executed": False, "match": False, "reason": "safety_block"})
            continue

        total += 1
        match = execution_match(eng, pred, gold)
        correct += int(match)

        if len(diagnostics) < 8:
            diagnostics.append({
                "question": q,
                "pred_sql": pred,
                "gold_sql": gold,
                "executed": True,
                "match": bool(match)
            })

    acc = correct / total if total else 0.0
    return {
        "samples": total,
        "correct": correct,
        "accuracy": round(acc, 4),
        "examples": diagnostics
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gretel_samples", type=int, default=75, help="Number of Gretel test samples for EM")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--local_file", default="artifacts/eval_local.jsonl")
    ap.add_argument("--db", default="sqlite:///data/demo.sqlite")
    ap.add_argument("--out", default="artifacts/eval_report.json")
    args = ap.parse_args()

    Path("artifacts").mkdir(exist_ok=True, parents=True)

    started = time.strftime("%Y-%m-%d %H:%M:%S")
    gretel_em = eval_gretel_em(sample_size=args.gretel_samples, seed=args.seed)
    local_ex = eval_local_exec(args.local_file, args.db)

    report = {
        "timestamp": started,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "model": DEFAULT_MODEL_NAME + " (prompt-only, no fine-tuning)",
        "dataset": {
            "gretel_test_subset": args.gretel_samples,
            "local_eval_file": args.local_file
        },
        "metrics": {
            "exact_match_gretel": gretel_em,
            "execution_accuracy_local": local_ex
        },
        "notes": "Prompt-engineered, schema-aware, few-shot baseline. SELECT-only with enforced LIMIT and SQL parsing safety."
    }

    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"✅ Wrote evaluation report → {args.out}")
    print(json.dumps({
        "EM_gretel": gretel_em["accuracy"],
        "EX_local": local_ex["accuracy"],
        "gretel_samples": gretel_em["samples"],
        "local_samples": local_ex["samples"]
    }, indent=2))

if __name__ == "__main__":
    main()