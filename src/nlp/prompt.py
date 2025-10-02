SYSTEM_RULES = """Translate English to SQLite SELECT queries.
Rules: 
- Only SELECT statements
- Use exact table and column names from schema
- No JOINs unless necessary
- Always add LIMIT 200
- Return complete, valid SQL only
- No partial or incomplete queries
"""

def build_prompt(schema_snippet: str, question: str, fewshots: str = "") -> str:
    # Truncate schema if too long to fit within token limits
    max_schema_length = 200
    if len(schema_snippet) > max_schema_length:
        schema_snippet = schema_snippet[:max_schema_length] + "..."
    
    return f"""{SYSTEM_RULES}

Schema:
{schema_snippet}

Examples:
{fewshots}

Q: {question}
SQL:"""