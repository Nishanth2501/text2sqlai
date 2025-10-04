# Text-to-SQL Assistant: From Natural Language to Database Queries

Ever wondered how to make databases more accessible to non-technical users? This project tackles exactly that challenge by building an intelligent assistant that converts everyday English questions into precise SQL queries. Think of it as a translator between human language and database language.

## What This Project Does

Imagine you have a database full of customer orders, user information, and product details. Instead of needing to learn SQL syntax, you can simply ask questions like "show me all users" or "what are the top 5 products by revenue?" and get instant results. That's exactly what this Text-to-SQL assistant does.

The magic happens through a combination of modern AI techniques and careful engineering. We use Google's Flan-T5 model (a pre-trained language model) combined with smart prompt engineering and few-shot learning to generate accurate SQL queries. The system also includes safety checks to ensure only read-only queries are executed, protecting your data from accidental modifications.

## Why This Approach Works

Rather than training a custom model from scratch (which would require massive datasets and computational resources), this project focuses on prompt engineering. By carefully crafting prompts with examples and providing the right context, we can guide a pre-trained model to generate the SQL we need. It's like teaching someone a new skill by showing them examples rather than starting from zero.

The beauty of this approach is that it's both effective and accessible. You don't need expensive hardware or massive datasets to get impressive results. Instead, you need creativity in prompt design, understanding of your data, and good engineering practices.

## Getting Started

### Quick Setup

First, let's get everything installed and running:

```bash
# Install all dependencies
make install

# Create a demo database with sample data
. .venv/bin/activate && python -m src.db.seed_demo

# Launch the interactive web interface
make ui
```

That's it! You should now have a web interface running at `http://localhost:8503` where you can start asking questions about your data.

### What You'll See

The interface is designed to be intuitive. You'll find:

- **Suggested prompts** at the top - click any of these to see how the system works
- **A text input** where you can type your own questions
- **Generated SQL** that shows exactly what query was created
- **Results table** displaying the data returned from your database
- **Query history** keeping track of all your interactions

## How It Works Under the Hood

### The Data Science Pipeline

This project demonstrates a complete data science workflow:

1. **Data Exploration**: We start by understanding our database structure and extracting schema information
2. **Prompt Engineering**: We design effective prompts that guide the AI model to generate good SQL
3. **Few-Shot Learning**: We provide examples of question-SQL pairs to help the model learn patterns
4. **Safety Validation**: We ensure only safe, read-only queries are executed
5. **Evaluation**: We measure performance using metrics like exact match accuracy

### The Technical Stack

- **AI Model**: Google Flan-T5 (pre-trained, no custom training needed)
- **Database**: SQLite with SQLAlchemy for database operations
- **Web Interface**: Streamlit for the user-friendly demo
- **API**: FastAPI for programmatic access
- **Evaluation**: Custom metrics for measuring SQL generation quality

### Safety First

One of the most important aspects of any Text-to-SQL system is safety. We've implemented multiple layers of protection:

- **Query validation**: Only SELECT statements are allowed
- **Automatic LIMIT**: All queries are capped to prevent overwhelming results
- **SQL parsing**: We validate that generated queries are syntactically correct
- **No data modification**: The system cannot insert, update, or delete data

## Testing the System

### Try These Examples

Once you have the interface running, try these example questions:

- "Show me all users"
- "What are the top 5 products by revenue?"
- "Find orders over $100"
- "List users from the US"
- "Show total revenue by country"

Each question will generate SQL, execute it safely, and display the results in a clean table format.

### Command Line Interface

If you prefer working from the terminal:

```bash
# Ask a question and see the generated SQL
. .venv/bin/activate && python -m src.cli.ask "show me all users"

# Execute the query and see results
. .venv/bin/activate && python -m src.cli.ask "top 5 skus by revenue" --execute
```

### API Access

For integration with other applications:

```bash
# Start the API server
make api

# Test the health endpoint
curl http://localhost:8000/health

# Generate SQL via API
curl -X POST "http://localhost:8000/text2sql" \
  -H "Content-Type: application/json" \
  -d '{"question": "show me all users"}'
```

## Evaluation and Metrics

A good data science project needs solid evaluation. This system includes comprehensive metrics:

### Running Evaluations

```bash
# Generate a complete evaluation report
make eval-report

# Test on the Gretel dataset (75 samples)
make eval-em

# Test on local data with execution
make eval-local
```

The evaluation measures both exact match accuracy (how often the generated SQL exactly matches the expected SQL) and execution accuracy (how often the generated SQL runs successfully and returns correct results).

### Understanding the Results

The evaluation report includes:
- **Sample counts**: How many queries were tested
- **Accuracy metrics**: Both exact match and execution success rates
- **Example outputs**: Sample question-SQL pairs for analysis
- **Performance data**: Generation and execution times

Even if the accuracy numbers seem modest initially, remember that this is a baseline system using only prompt engineering. The real value is in demonstrating the complete pipeline and showing how to measure and improve performance.

## Project Structure

The codebase is organized to be both functional and educational:

```
src/
├── cli/           # Command-line interface for testing
├── db/            # Database connection and schema extraction
├── eval/          # Evaluation metrics and testing framework
├── nlp/           # Natural language processing components
└── service/       # Web API and user interface
```

Each module has a specific purpose, making the codebase easy to understand and extend.

## Key Features

### For Data Scientists
- **Complete evaluation framework** with multiple metrics
- **Prompt engineering examples** showing how to guide AI models
- **Schema-aware generation** that understands your specific database
- **Safety validation** ensuring data protection

### For Developers
- **Clean API design** with FastAPI
- **Modular architecture** easy to extend and maintain
- **Comprehensive error handling** with detailed logging
- **Production-ready deployment** options

### For End Users
- **Intuitive web interface** requiring no technical knowledge
- **Instant feedback** showing generated SQL and results
- **Query history** for tracking and learning
- **Safety guarantees** protecting your data

## Why This Matters

Text-to-SQL systems have real-world applications in business intelligence, data analysis, and making databases more accessible. This project demonstrates that you can build effective systems using modern AI techniques without requiring massive computational resources or custom training.

The approach shown here - combining pre-trained models with smart prompt engineering - is becoming increasingly important in AI applications. It's a practical way to leverage powerful language models while maintaining control over the system's behavior and safety.

## Next Steps

This project provides a solid foundation that could be extended in many directions:

- **Improved prompting strategies** for better SQL generation
- **More sophisticated evaluation metrics** including semantic correctness
- **Integration with different database systems** beyond SQLite
- **User interface enhancements** for better query building
- **Performance optimizations** for faster generation

The beauty of this approach is that improvements can be made incrementally, and each enhancement can be measured and validated using the evaluation framework.

## Getting Help

If you run into issues:

1. **Check the logs** - both the web interface and CLI provide detailed error messages
2. **Verify your database** - make sure the demo database is seeded with `python -m src.db.seed_demo`
3. **Check dependencies** - ensure all packages are installed with `make install`
4. **Review the evaluation report** - it often provides insights into what's working and what isn't

