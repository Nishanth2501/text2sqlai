import time
import traceback
import pandas as pd
import streamlit as st
from sqlalchemy import text

# project imports
from src.db.connect import get_engine
from src.db.introspect import get_schema_summary, to_compact_schema
from src.nlp.generator import T2SQLGenerator
from src.nlp.safety import is_safe_select, ensure_limit

st.set_page_config(page_title="Text-to-SQL Assistant", layout="wide")

# -------------------------
# Helpers
# -------------------------
def get_schema_text(db_url: str) -> str:
    eng = get_engine(db_url)
    tables, cols = get_schema_summary(eng)
    return to_compact_schema(tables, cols)

def run_query(db_url: str, sql: str) -> pd.DataFrame:
    eng = get_engine(db_url)
    with eng.begin() as conn:
        df = pd.read_sql(text(sql), conn)
    return df

def init_state():
    if "history" not in st.session_state:
        st.session_state.history = []  # list of dicts: {q, sql, rows, ok, took, error}

init_state()

# -------------------------
# Sidebar
# -------------------------
st.sidebar.title("⚙️ Settings")

db_url = st.sidebar.text_input(
    "Database URL",
    value="sqlite:///data/demo.sqlite",
    help="SQLAlchemy URL; default points to the demo SQLite DB seeded in this project.",
)

show_schema = st.sidebar.checkbox("Show schema in prompt", value=True)
show_schema_panel = st.sidebar.checkbox("Show schema panel on UI", value=False)
auto_limit = st.sidebar.number_input("Auto LIMIT (rows)", min_value=10, max_value=10000, value=200, step=10)
execute_toggle = st.sidebar.checkbox("Execute SQL after generation", value=True)
max_rows_display = st.sidebar.number_input("Rows to display", min_value=5, max_value=1000, value=50, step=5)
st.sidebar.markdown("---")
st.sidebar.caption("Tip: Use the demo DB seeder if needed: `python src/db/seed_demo.py`")

# -------------------------
# Title & Intro
# -------------------------
st.title("🧠 Text-to-SQL Assistant")
st.write(
    "Type a natural-language question, I'll generate **read-only SQL**, "
    "run it on your database (if enabled), and show the results."
)

# Optional schema panel
if show_schema_panel:
    try:
        schema_txt = get_schema_text(db_url)
        with st.expander("📄 Database Schema", expanded=False):
            st.code(schema_txt, language="text")
    except Exception as e:
        st.warning(f"Could not fetch schema: {e}")

# -------------------------
# Suggested Prompts
# -------------------------
st.subheader("💡 Try These Examples")
suggested_prompts = [
    "Show me all users",
    "Top 5 skus by revenue", 
    "Orders over 100 dollars",
    "Users from the US",
    "Total revenue by country"
]

# Create columns for the suggested prompts
cols = st.columns(5)
for i, prompt in enumerate(suggested_prompts):
    with cols[i]:
        if st.button(f"💬 {prompt}", key=f"suggest_{i}", help=f"Click to use: {prompt}"):
            st.session_state.current_question = prompt
            st.rerun()

# -------------------------
# Input
# -------------------------
# Initialize current_question if not exists
if "current_question" not in st.session_state:
    st.session_state.current_question = ""

question = st.text_input(
    "Ask me something about your data",
    value=st.session_state.current_question,
    placeholder="e.g., 'show me all users' or 'top 5 skus by revenue'",
    help="Ask about data in your DB. Click a suggestion above or type your own question.",
)

# Update the session state when user types
if question != st.session_state.current_question:
    st.session_state.current_question = question

colA, colB = st.columns([1, 1])
with colA:
    gen_button = st.button("✨ Generate SQL")
with colB:
    clear_button = st.button("🧹 Clear history")

if clear_button:
    st.session_state.history = []
    st.rerun()

# -------------------------
# Main Action
# -------------------------
if gen_button and question.strip():
    try:
        # build schema text for prompting (or empty if disabled)
        schema_txt = get_schema_text(db_url) if show_schema else "tables: (schema suppressed)"
        gen = T2SQLGenerator(schema_txt=schema_txt)

        t0 = time.time()
        sql_raw = gen.generate(question.strip())
        sql_safe = ensure_limit(sql_raw, default_limit=int(auto_limit))
        gen_ms = int((time.time() - t0) * 1000)

        st.subheader("🧾 Generated SQL")
        st.code(sql_safe, language="sql")

        # safety check
        safe = is_safe_select(sql_safe)
        if not safe:
            st.error("Blocked: SQL failed safety checks (only SELECT allowed; no DDL/DML).")
            st.session_state.history.append(
                {"q": question, "sql": sql_safe, "rows": 0, "ok": False, "took": gen_ms, "error": "safety_block"}
            )
        else:
            if execute_toggle:
                try:
                    t1 = time.time()
                    df = run_query(db_url, sql_safe)
                    exec_ms = int((time.time() - t1) * 1000)
                    st.success(f"Executed successfully • {len(df)} rows • gen {gen_ms} ms • exec {exec_ms} ms")
                    if len(df) == 0:
                        st.info("Query returned 0 rows.")
                    else:
                        st.dataframe(df.head(max_rows_display))
                    st.session_state.history.append(
                        {"q": question, "sql": sql_safe, "rows": int(len(df)), "ok": True, "took": gen_ms + exec_ms}
                    )
                except Exception as e:
                    st.error(f"Execution error: {e}")
                    with st.expander("Traceback"):
                        st.code(traceback.format_exc())
                    st.session_state.history.append(
                        {"q": question, "sql": sql_safe, "rows": 0, "ok": False, "took": gen_ms, "error": str(e)}
                    )
            else:
                st.info("Execution disabled. Enable it in the sidebar to run the SQL.")
                st.session_state.history.append(
                    {"q": question, "sql": sql_safe, "rows": None, "ok": True, "took": gen_ms}
                )

    except Exception as e:
        st.error(f"Generation error: {e}")
        with st.expander("Traceback"):
            st.code(traceback.format_exc())

# -------------------------
# History Panel
# -------------------------
if st.session_state.history:
    st.subheader("🧾 Query History (this session)")
    for i, rec in enumerate(reversed(st.session_state.history), 1):
        with st.expander(f"{i}. {rec['q']}", expanded=False):
            st.markdown("**SQL:**")
            st.code(rec["sql"], language="sql")
            if rec.get("rows") is not None:
                st.markdown(f"**Rows:** {rec['rows']}")
            st.markdown(f"**OK:** {rec['ok']}  •  **Latency:** {rec['took']} ms")
            if rec.get("error"):
                st.error(f"Error: {rec['error']}")