from sqlalchemy import create_engine, text
from pathlib import Path

DB_PATH = "data/demo.sqlite"

DDL_SQL = """
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS items;

CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  name TEXT,
  country TEXT
);

CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  created_at TEXT,
  total REAL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE items (
  id INTEGER PRIMARY KEY,
  order_id INTEGER,
  sku TEXT,
  price REAL,
  FOREIGN KEY(order_id) REFERENCES orders(id)
);
"""

SEED_SQL = """
INSERT INTO users(id, name, country) VALUES
 (1,'Alice','US'),
 (2,'Bob','IN'),
 (3,'Chloe','GB'),
 (4,'Diego','US');

INSERT INTO orders(id, user_id, created_at, total) VALUES
 (100,1,'2024-11-03',120.00),
 (101,1,'2025-01-15',250.50),
 (102,2,'2025-02-20', 99.99),
 (103,3,'2025-03-05',310.00),
 (104,4,'2025-03-18', 75.25);

INSERT INTO items(id, order_id, sku, price) VALUES
 (1000,100,'SKU-RED', 60.00),
 (1001,100,'SKU-BLU', 60.00),
 (1002,101,'SKU-RED',120.50),
 (1003,101,'SKU-GRN',130.00),
 (1004,102,'SKU-RED', 99.99),
 (1005,103,'SKU-YLW',310.00),
 (1006,104,'SKU-BLU', 75.25);
"""

def main():
    Path("data").mkdir(parents=True, exist_ok=True)
    eng = create_engine(f"sqlite:///{DB_PATH}", future=True)
    with eng.begin() as conn:
        for stmt in DDL_SQL.strip().split(";"):
            if stmt.strip():
                conn.execute(text(stmt))
        for stmt in SEED_SQL.strip().split(";"):
            if stmt.strip():
                conn.execute(text(stmt))
    print(f"✅ Demo DB created at {DB_PATH}")

if __name__ == "__main__":
    main()