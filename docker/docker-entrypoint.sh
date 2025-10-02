#!/bin/bash
set -e

echo "🚀 Starting Text-to-SQL Assistant..."

# Wait for database to be ready (if using external DB)
if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == postgresql* ]]; then
    echo "⏳ Waiting for database to be ready..."
    python -c "
import time
import psycopg2
from urllib.parse import urlparse
import sys

parsed = urlparse('$DATABASE_URL')
for i in range(30):
    try:
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:]
        )
        conn.close()
        print('✅ Database connection successful')
        break
    except psycopg2.OperationalError:
        print(f'⏳ Waiting for database... ({i+1}/30)')
        time.sleep(2)
else:
    print('❌ Database connection failed')
    sys.exit(1)
"
fi

# Initialize demo database if it doesn't exist
if [ ! -f "/app/data/demo.sqlite" ]; then
    echo "📊 Initializing demo database..."
    python -c "
import sys
sys.path.insert(0, '/app/src')
from db.seed_demo import seed_demo_database
seed_demo_database()
print('✅ Demo database initialized')
"
fi

# Download language model if caching is enabled
if [ "$ENABLE_MODEL_CACHING" = "true" ]; then
    echo "🧠 Pre-loading language model..."
    python -c "
import sys
sys.path.insert(0, '/app/src')
from nlp.generator import T2SQLGenerator
try:
    gen = T2SQLGenerator()
    print('✅ Language model loaded and cached')
except Exception as e:
    print(f'⚠️  Model pre-loading failed: {e}')
    print('Model will be loaded on first use')
"
fi

echo "🎯 Starting Streamlit application..."

# Start Streamlit
exec streamlit run src/service/ui_streamlit.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --browser.gatherUsageStats=false
