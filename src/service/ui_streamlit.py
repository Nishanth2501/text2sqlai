import os
import time
import traceback
import pandas as pd
import streamlit as st
from sqlalchemy import text

# project imports
import sys

sys.path.append("/app")

from src.db.connect import get_engine
from src.db.introspect import get_schema_summary, to_compact_schema
from src.nlp.generator import T2SQLGenerator
from src.nlp.safety import is_safe_select, ensure_limit
from src.utils.logger import get_logger
from src.utils.exceptions import (
    ModelLoadError,
    DatabaseConnectionError,
    SQLGenerationError,
    SQLSafetyError,
)
from config.config import config

# Setup logging
logger = get_logger("text2sql.ui")

# Page configuration
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

if os.getenv("WEBSITE_SITE_NAME"):
    # Running on Azure App Service
    st.markdown(
        """
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


# -------------------------
# Helpers
# -------------------------
@st.cache_data(ttl=300)  # Cache schema for 5 minutes
def get_schema_text(db_url: str) -> str:
    """Get database schema with caching"""
    try:
        eng = get_engine(db_url)
        tables, cols = get_schema_summary(eng)
        schema = to_compact_schema(tables, cols)
        logger.info(f"Schema loaded successfully: {len(tables)} tables")
        return schema
    except Exception as e:
        logger.error(f"Failed to load schema: {str(e)}")
        raise DatabaseConnectionError(f"Failed to load database schema: {str(e)}")


def run_query(db_url: str, sql: str) -> pd.DataFrame:
    """Execute SQL query safely"""
    try:
        eng = get_engine(db_url)
        with eng.begin() as conn:
            df = pd.read_sql(text(sql), conn)
        logger.info(f"Query executed successfully: {len(df)} rows returned")
        return df
    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        raise SQLGenerationError(f"Query execution failed: {str(e)}")


def init_state():
    """Initialize session state"""
    if "history" not in st.session_state:
        st.session_state.history = []
    if "model_info" not in st.session_state:
        st.session_state.model_info = None
    if "error_count" not in st.session_state:
        st.session_state.error_count = 0


def show_error_message(error: Exception, context: str = ""):
    """Display user-friendly error message"""
    st.session_state.error_count += 1

    if isinstance(error, SQLSafetyError):
        st.error(
            "**Safety Check Failed**: This query was blocked for security reasons. Only SELECT statements are allowed."
        )
    elif isinstance(error, DatabaseConnectionError):
        st.error(
            "**Database Error**: Unable to connect to the database. Please check your database URL."
        )
    elif isinstance(error, ModelLoadError):
        st.error(
            "**Model Error**: Unable to load the language model. Please try refreshing the page."
        )
    elif isinstance(error, SQLGenerationError):
        st.error(
            "**Generation Error**: Failed to generate SQL. Please try rephrasing your question."
        )
    else:
        st.error(f"**Error**: {str(error)}")

    if st.checkbox(
        "Show technical details", key=f"show_details_{st.session_state.error_count}"
    ):
        with st.expander("Technical Details"):
            st.code(traceback.format_exc())


init_state()

# -------------------------
# Sidebar
# -------------------------
st.sidebar.title("Settings")

# Database Configuration
st.sidebar.subheader("Database")
db_url = st.sidebar.text_input(
    "Database URL",
    value=config.DATABASE_URL,
    help="SQLAlchemy URL; default points to the demo SQLite DB seeded in this project.",
)

# Model Configuration
st.sidebar.subheader("Language Model")
model_name = st.sidebar.text_input(
    "Model Name",
    value=config.MODEL_NAME,
    help="HuggingFace model identifier",
    disabled=True,  # Keep it simple for deployment
)

# Query Configuration
st.sidebar.subheader("Query Settings")
show_schema = st.sidebar.checkbox("Include schema in prompt", value=True)
show_schema_panel = st.sidebar.checkbox("Show schema panel", value=False)
auto_limit = st.sidebar.number_input(
    "Auto LIMIT (rows)",
    min_value=10,
    max_value=config.MAX_QUERY_LIMIT,
    value=config.DEFAULT_QUERY_LIMIT,
    step=10,
)
execute_toggle = st.sidebar.checkbox("Execute SQL after generation", value=True)
max_rows_display = st.sidebar.number_input(
    "Max rows to display", min_value=5, max_value=1000, value=50, step=5
)

# Advanced Settings
with st.sidebar.expander("Advanced Settings"):
    max_tokens = st.number_input(
        "Max tokens", min_value=32, max_value=512, value=config.MAX_TOKENS
    )
    num_beams = st.number_input(
        "Beam search beams", min_value=1, max_value=8, value=config.NUM_BEAMS
    )
    enable_safety = st.checkbox(
        "Enable safety checks", value=config.ENABLE_SAFETY_CHECKS
    )

st.sidebar.markdown("---")
st.sidebar.caption(f"**{config.APP_NAME}** v{config.APP_VERSION}")
st.sidebar.caption(
    "Tip: Use the demo DB seeder if needed: `python src/db/seed_demo.py`"
)

# -------------------------
# Title & Intro
# -------------------------
st.title("Text-to-SQL Assistant")
st.write(
    "Type a natural-language question, I'll generate **read-only SQL**, "
    "run it on your database (if enabled), and show the results."
)

# Optional schema panel
if show_schema_panel:
    try:
        schema_txt = get_schema_text(db_url)
        with st.expander("Database Schema", expanded=False):
            st.code(schema_txt, language="text")
    except Exception as e:
        st.warning(f"Could not fetch schema: {e}")

# -------------------------
# Suggested Prompts
# -------------------------
st.subheader("Try These Examples")
suggested_prompts = [
    "Show me all users",
    "Top 5 skus by revenue",
    "Orders over 100 dollars",
    "Users from the US",
    "Total revenue by country",
]

# Display suggested prompts as text
cols = st.columns(5)
for i, prompt in enumerate(suggested_prompts):
    with cols[i]:
        st.markdown(f"**{prompt}**")

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
    gen_button = st.button("Generate SQL")
with colB:
    clear_button = st.button("Clear history")

if clear_button:
    st.session_state.history = []
    st.rerun()

# -------------------------
# Main Action
# -------------------------
if gen_button and question.strip():
    st.info(f"Processing question: '{question}'")
    try:
        # Build schema text for prompting (or empty if disabled)
        schema_txt = (
            get_schema_text(db_url) if show_schema else "tables: (schema suppressed)"
        )

        # Initialize model with progress indicator
        with st.spinner(
            "Initializing language model (this may take a moment on first use)..."
        ):
            try:
                gen = T2SQLGenerator(schema_txt=schema_txt)
                st.session_state.model_info = gen.get_model_info()
                logger.info("Model initialized successfully")
            except Exception as e:
                logger.error(f"Model initialization failed: {str(e)}")
                raise ModelLoadError(f"Failed to initialize language model: {str(e)}")

        # Generate SQL with progress indicator
        with st.spinner("Generating SQL..."):
            try:
                t0 = time.time()
                sql_raw = gen.generate(
                    question.strip(), max_new_tokens=max_tokens, num_beams=num_beams
                )
                sql_safe = ensure_limit(sql_raw, default_limit=int(auto_limit))
                gen_ms = int((time.time() - t0) * 1000)
                logger.info(f"SQL generated successfully in {gen_ms}ms")
            except Exception as e:
                logger.error(f"SQL generation failed: {str(e)}")
                raise SQLGenerationError(f"Failed to generate SQL: {str(e)}")

        # Display generated SQL
        st.subheader("Generated SQL")
        st.code(sql_safe, language="sql")

        # Safety check
        if enable_safety:
            try:
                safe = is_safe_select(sql_safe)
                if not safe:
                    raise SQLSafetyError("SQL failed safety checks")
            except SQLSafetyError:
                st.session_state.history.append(
                    {
                        "q": question,
                        "sql": sql_safe,
                        "rows": 0,
                        "ok": False,
                        "took": gen_ms,
                        "error": "safety_block",
                    }
                )
                raise

        # Execute query if enabled
        if execute_toggle:
            try:
                with st.spinner("Executing query..."):
                    t1 = time.time()
                    df = run_query(db_url, sql_safe)
                    exec_ms = int((time.time() - t1) * 1000)

                # Display results
                st.success(
                    f"Executed successfully • {len(df)} rows • Generated in {gen_ms}ms • Executed in {exec_ms}ms"
                )

                if len(df) == 0:
                    st.info("Query returned 0 rows.")
                else:
                    st.dataframe(df.head(max_rows_display))

                    if len(df) > max_rows_display:
                        st.caption(f"Showing {max_rows_display} of {len(df)} rows")

                # Add to history
                st.session_state.history.append(
                    {
                        "q": question,
                        "sql": sql_safe,
                        "rows": int(len(df)),
                        "ok": True,
                        "took": gen_ms + exec_ms,
                        "timestamp": time.time(),
                    }
                )

            except Exception as e:
                logger.error(f"Query execution failed: {str(e)}")
                st.session_state.history.append(
                    {
                        "q": question,
                        "sql": sql_safe,
                        "rows": 0,
                        "ok": False,
                        "took": gen_ms,
                        "error": str(e),
                        "timestamp": time.time(),
                    }
                )
                raise SQLGenerationError(f"Query execution failed: {str(e)}")
        else:
            st.info("Execution disabled. Enable it in the sidebar to run the SQL.")
            st.session_state.history.append(
                {
                    "q": question,
                    "sql": sql_safe,
                    "rows": None,
                    "ok": True,
                    "took": gen_ms,
                    "timestamp": time.time(),
                }
            )

    except (
        ModelLoadError,
        DatabaseConnectionError,
        SQLGenerationError,
        SQLSafetyError,
    ) as e:
        st.error(f"Error occurred: {type(e).__name__}: {str(e)}")
        show_error_message(e)
        logger.error(f"User-facing error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        st.error(
            "**Unexpected Error**: An unexpected error occurred. Please try again or contact support."
        )
        with st.expander("Technical Details"):
            st.code(traceback.format_exc())

# -------------------------
# History Panel
# -------------------------
if st.session_state.history:
    st.subheader("Query History (this session)")
    for i, rec in enumerate(reversed(st.session_state.history), 1):
        with st.expander(f"{i}. {rec['q']}", expanded=False):
            st.markdown("**SQL:**")
            st.code(rec["sql"], language="sql")
            if rec.get("rows") is not None:
                st.markdown(f"**Rows:** {rec['rows']}")
            st.markdown(f"**OK:** {rec['ok']}  •  **Latency:** {rec['took']} ms")
            if rec.get("error"):
                st.error(f"Error: {rec['error']}")
