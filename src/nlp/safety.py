import re
import sqlglot

DDL_DML = re.compile(r"(?i)\\b(UPDATE|DELETE|DROP|ALTER|INSERT|CREATE|TRUNCATE|GRANT|REVOKE)\\b")

def is_safe_select(sql: str) -> bool:
    if not sql.strip().lower().startswith("select"):
        return False
    if DDL_DML.search(sql):
        return False
    try:
        sqlglot.parse_one(sql)  # syntax check
        return True
    except Exception:
        return False

def ensure_limit(sql: str, default_limit: int = 200) -> str:
    # append LIMIT if none present
    try:
        tree = sqlglot.parse_one(sql)
        if not tree.args.get("limit"):
            return f"{sql.rstrip(';')} LIMIT {default_limit};"
        return sql
    except Exception:
        return f"{sql.rstrip(';')} LIMIT {default_limit};"