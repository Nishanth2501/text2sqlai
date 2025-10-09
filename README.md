# Text-to-SQL Assistant

## Project Insights

This project represents a practical solution to a common problem: making database queries accessible to people who don't know SQL. The system uses Google's FLAN-T5 language model to translate natural language questions into SQL queries, bridging the gap between human language and database query language.

### Technical Achievements

**Cloud-Native Architecture**: Successfully deployed a production-ready AI application on Microsoft Azure with:
- Containerized microservices using Docker and Azure Container Instances
- Automated CI/CD pipelines for seamless deployment
- Infrastructure as Code (IaC) for consistent cloud provisioning
- Production monitoring and logging with Azure Log Analytics

**AI/ML Integration**: Demonstrated practical application of large language models:
- Natural language processing can significantly reduce the barrier to database interaction
- Pre-trained language models like FLAN-T5 work well for structured query generation tasks
- Proper evaluation frameworks are crucial for measuring and improving text-to-SQL accuracy

**DevOps Best Practices**: Implemented modern software development practices:
- Containerization with Docker simplifies deployment and scaling across different environments
- A simple web interface makes complex AI capabilities accessible to end users
- Comprehensive testing and quality assurance processes
- Environment-specific configuration management

The architecture demonstrates how to build production-ready AI applications with proper separation of concerns, comprehensive testing, and enterprise-grade cloud deployment strategies.

## Overview

Convert natural language questions into SQL queries using advanced language processing. This tool helps you query databases using plain English instead of writing complex SQL code.

## Live Demo

**Try it now**: [http://text2sql-app.westus2.azurecontainer.io:8501](http://text2sql-app.westus2.azurecontainer.io:8501)

Simply type questions like:
- "Show me all customers from California"
- "Find products with price greater than $100"
- "What's the total revenue for this month?"

## Quick Start

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

## How It Works

1. **Ask a question** in natural language
2. **The system converts** your question to SQL
3. **Query executes** against the database
4. **Results display** in a clean table format

## Technology Stack

- **Frontend**: Streamlit web interface
- **Backend**: Python with Google's FLAN-T5 language model
- **Database**: SQLite (demo), PostgreSQL/MySQL (production)
- **Deployment**: Docker + Azure Cloud
- **Processing**: Advanced natural language processing

## Features

### Core Capabilities
- Natural language to SQL conversion
- Interactive web interface
- Database schema understanding
- SQL safety validation
- Error handling and suggestions

### Advanced Features
- Multi-table queries with joins
- Aggregate functions (SUM, COUNT, AVG)
- Complex filtering and sorting
- Subqueries and nested operations
- Real-time query execution

## Example Queries

| Natural Language | Generated SQL |
|-----------------|---------------|
| "Show all users" | `SELECT * FROM users` |
| "Customers from USA" | `SELECT * FROM customers WHERE country = 'USA'` |
| "Total sales this year" | `SELECT SUM(amount) FROM orders WHERE YEAR(date) = 2024` |
| "Top 10 products by sales" | `SELECT product_name, SUM(quantity) FROM order_items GROUP BY product_id ORDER BY SUM(quantity) DESC LIMIT 10` |

## Cloud Deployment & DevOps

### Azure Cloud Infrastructure

This project demonstrates full-stack cloud deployment expertise using Microsoft Azure services:

**Production Deployment**: [Live Application](http://text2sql-app.westus2.azurecontainer.io:8501)
- **Azure Container Instances (ACI)**: Scalable containerized deployment with auto-scaling capabilities
- **Azure App Service**: Production-ready web application hosting with integrated CI/CD
- **Azure Container Registry**: Secure container image storage and management
- **Azure Log Analytics**: Comprehensive monitoring and logging for production environments

**Infrastructure as Code**: Automated deployment scripts for consistent cloud provisioning
- Zero-downtime deployments with blue-green deployment strategies
- Environment-specific configuration management
- Automated scaling based on traffic patterns
- Cloud-native security implementations

### Deployment Commands

#### Local Development
```bash
# Start the application locally
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop the application
docker-compose -f docker/docker-compose.yml down
```

#### Cloud Deployment (Azure)
```bash
# Deploy to Azure Container Instances (Production)
./deployments/azure/deploy-to-aci.sh

# Deploy to Azure App Service (Enterprise)
./deployments/azure/deploy-to-appservice.sh

# Quick deployment with custom configuration
./deployments/azure/quick-deploy.sh
```

### Cloud Architecture Benefits

- **Scalability**: Auto-scaling based on CPU and memory usage
- **Reliability**: 99.9% uptime with Azure's managed infrastructure
- **Security**: Built-in Azure security features and compliance standards
- **Cost Optimization**: Pay-per-use model with automatic resource management
- **Monitoring**: Real-time performance metrics and alerting

## Configuration

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

## Performance

- **Query Generation**: 0.5-2 seconds per query
- **Model Loading**: 2-5 seconds with caching
- **Database Queries**: Less than 100ms for simple queries
- **Memory Usage**: Approximately 2GB with model caching enabled

## Development

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

## Use Cases

- **Data Analysis**: Query databases without SQL knowledge
- **Business Intelligence**: Generate reports from natural language
- **Education**: Learn SQL through natural language examples
- **Prototyping**: Quickly test database queries
- **Accessibility**: Make data accessible to non-technical users

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Google's FLAN-T5 language model for text-to-SQL capabilities
- Streamlit for the web interface framework
- SQLAlchemy for database operations
- Docker for containerization support

---

**Built with modern DevOps practices and deployed to Azure Cloud**