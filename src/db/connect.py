from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

def get_engine(url: str = "sqlite:///data/demo.sqlite") -> Engine:
    return create_engine(url, future=True)
