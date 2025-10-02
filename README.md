# Text-to-SQL Assistant

Convert natural language questions into SQL queries using advanced language processing. This tool helps you query databases using plain English instead of writing complex SQL code.

## 🌐 Live Demo

**Try it now**: [http://text2sql-app.westus2.azurecontainer.io:8501](http://text2sql-app.westus2.azurecontainer.io:8501)

Simply type questions like:
- "Show me all customers from California"
- "Find products with price greater than $100"
- "What's the total revenue for this month?"

## 🚀 Quick Start

### Using Docker Desktop (Recommended)

1. **Install Docker Desktop** from [docker.com](https://www.docker.com/products/docker-desktop)

2. **Clone and run**:
   ```bash
   git clone <your-repo-url>
   cd text2sql
   docker-compose -f docker/docker-compose.yml up -d
   ```

3. **Access the app**: http://localhost:8501

### Manual Installation

1. **Install Python 3.11+**
2. **Install dependencies**:
   ```bash
   pip install -r config/requirements.txt
   ```
3. **Run the app**:
   ```bash
   streamlit run src/service/ui_streamlit.py
   ```

## 💡 How It Works

1. **Ask a question** in natural language
2. **The system converts** your question to SQL
3. **Query executes** against the database
4. **Results display** in a clean table format

## 🛠️ Technology Stack

- **Frontend**: Streamlit web interface
- **Backend**: Python with Google's FLAN-T5 language model
- **Database**: SQLite (demo), PostgreSQL/MySQL (production)
- **Deployment**: Docker + Azure Cloud
- **Processing**: Advanced natural language processing

## 📊 Features

### Core Capabilities
- ✅ Natural language to SQL conversion
- ✅ Interactive web interface
- ✅ Database schema understanding
- ✅ SQL safety validation
- ✅ Error handling and suggestions

### Advanced Features
- ✅ Multi-table queries with joins
- ✅ Aggregate functions (SUM, COUNT, AVG)
- ✅ Complex filtering and sorting
- ✅ Subqueries and nested operations
- ✅ Real-time query execution

## 🎯 Example Queries

| Natural Language | Generated SQL |
|-----------------|---------------|
| "Show all users" | `SELECT * FROM users` |
| "Customers from USA" | `SELECT * FROM customers WHERE country = 'USA'` |
| "Total sales this year" | `SELECT SUM(amount) FROM orders WHERE YEAR(date) = 2024` |
| "Top 10 products by sales" | `SELECT product_name, SUM(quantity) FROM order_items GROUP BY product_id ORDER BY SUM(quantity) DESC LIMIT 10` |

## 🐳 Docker Deployment

### Local Development
```bash
# Start the application
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop the application
docker-compose -f docker/docker-compose.yml down
```

### Cloud Deployment
```bash
# Deploy to Azure Container Instances
./deployments/azure/deploy-to-aci.sh

# Deploy to Azure App Service
./deployments/azure/deploy-to-appservice.sh
```

## ⚙️ Configuration

The application uses environment variables for configuration:

```bash
# Application settings
APP_NAME="Text-to-SQL Assistant"
DATABASE_URL="sqlite:///data/demo.sqlite"
MODEL_NAME="google/flan-t5-base"

# Performance settings
MAX_TOKENS=128
NUM_BEAMS=4
ENABLE_MODEL_CACHING=true
LOG_LEVEL=INFO
```

## 📈 Performance

- **Query Generation**: 0.5-2 seconds per query
- **Model Loading**: 2-5 seconds with caching
- **Database Queries**: Less than 100ms for simple queries
- **Memory Usage**: ~2GB with model caching enabled

## 🔧 Development

### Project Structure
```
text2sql/
├── src/
│   ├── service/          # Streamlit web interface
│   ├── nlp/             # Language processing
│   ├── db/              # Database operations
│   └── utils/           # Utilities and helpers
├── docker/              # Docker configuration
├── deployments/         # Cloud deployment scripts
├── eval/               # Evaluation framework
└── config/             # Configuration files
```

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_generator.py
```

### Code Quality
```bash
# Format code
black src/

# Check code style
flake8 src/

# Type checking
mypy src/
```

## 🌟 Use Cases

- **Data Analysis**: Query databases without SQL knowledge
- **Business Intelligence**: Generate reports from natural language
- **Education**: Learn SQL through natural language examples
- **Prototyping**: Quickly test database queries
- **Accessibility**: Make data accessible to non-technical users

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google's FLAN-T5 language model for text-to-SQL capabilities
- Streamlit for the web interface framework
- SQLAlchemy for database operations
- Docker for containerization support

---

**Built with ❤️ using modern DevOps practices and deployed to Azure Cloud**