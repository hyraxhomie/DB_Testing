# Database Benchmarking Framework

A comprehensive benchmarking framework for testing and comparing performance across different database types and vendors. This project supports both **Relational** and **Graph** databases, allowing you to compare performance between different vendors of the same database type.

## Features

- **Multi-Database Support**: Test relational (PostgreSQL, MySQL, SQLite) and graph (Neo4j, ArangoDB) databases
- **Comprehensive Benchmarks**: Tests include CRUD operations, complex queries, joins, traversals, and more
- **Performance Metrics**: Measures latency, throughput, and generates detailed reports
- **Easy Setup**: Docker Compose configuration for quick database deployment
- **Visualization**: Automatic generation of comparison charts and statistics

## Supported Databases

### Relational Databases
- **PostgreSQL** - Advanced open-source relational database
- **MySQL** - Popular open-source relational database
- **SQLite** - Lightweight file-based database

### Graph Databases
- **Neo4j** - Leading graph database platform
- **ArangoDB** - Multi-model database with strong graph capabilities

## Prerequisites

- Python 3.8 or higher
- Node.js 18+ and npm (for TypeScript implementation)
- Docker and Docker Compose (for running databases)
- pip (Python package manager)

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd DB_Testing
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start databases using Docker Compose**:
   ```bash
   docker-compose up -d
   ```

   This will start:
   - PostgreSQL on port 5432
   - MySQL on port 3306
   - Neo4j on port 7474 (HTTP) and 7687 (Bolt)
   - ArangoDB on port 8529

   Wait a few moments for all databases to be ready. You can check status with:
   ```bash
   docker-compose ps
   ```

5. **Configure database connections** (optional):
   
   Edit `config/databases.yaml` to match your database setup if you're not using Docker Compose defaults.

6. **Install TypeScript dependencies** (optional, for TypeScript implementation):
   ```bash
   npm install
   npm run build
   ```

## Usage

### Running All Benchmarks

Run benchmarks for all configured databases:
```bash
python run_benchmarks.py
```

### Running Specific Database Types

Run only relational database benchmarks:
```bash
python run_benchmarks.py --type relational
```

Run only graph database benchmarks:
```bash
python run_benchmarks.py --type graph
```

### Running Specific Vendors

Test only specific vendors:
```bash
# Test only PostgreSQL and MySQL
python run_benchmarks.py --type relational --vendors postgresql mysql

# Test only Neo4j
python run_benchmarks.py --type graph --vendors neo4j
```

### Command Line Options

- `--type`: Database type to test (`relational`, `graph`, or `all`). Default: `all`
- `--vendors`: Specific vendors to test (e.g., `postgresql mysql`). Default: all configured vendors
- `--config`: Path to database configuration file. Default: `config/databases.yaml`
- `--no-setup`: Skip initial data setup (useful for testing with existing data)
- `--output-dir`: Directory to save results. Default: `results`

### Example Commands

```bash
# Quick test with SQLite (no Docker needed)
python run_benchmarks.py --type relational --vendors sqlite

# Full benchmark suite
python run_benchmarks.py --type all

# Compare PostgreSQL vs MySQL
python run_benchmarks.py --type relational --vendors postgresql mysql
```

## Benchmark Operations

### Relational Database Benchmarks

- **Insert Operations**: Single and batch inserts
- **Select Operations**: By ID, by indexed column (email), with JOINs
- **Update Operations**: Single record updates
- **Delete Operations**: Record deletion
- **Aggregate Queries**: COUNT, AVG, MIN, MAX operations
- **Complex Queries**: Multi-table joins with GROUP BY and HAVING

### Graph Database Benchmarks

- **Node Creation**: Creating nodes/vertices
- **Relationship Creation**: Creating edges/relationships
- **Node Lookup**: Finding nodes by ID
- **Traversal**: Following relationships between nodes
- **Pattern Matching**: Complex graph pattern queries
- **Shortest Path**: Finding shortest paths between nodes

## Results

After running benchmarks, results are saved in the `results/` directory:

- **`benchmark_results.csv`**: Detailed results for all operations
- **`summary.json`**: Summary statistics (mean, median, std dev, min, max, count)
- **`plots/`**: Visualization charts for each operation type

### Viewing Results

Results can be analyzed using the included analyzer (available in both Python and TypeScript) or imported into your preferred data analysis tool:

**Python:**
```python
from src.results import ResultsAnalyzer
import pandas as pd

# Load results
df = pd.read_csv('results/benchmark_results.csv')

# View summary
print(df.groupby(['operation', 'database'])['duration_ms'].describe())
```

**TypeScript:**
```typescript
import { ResultsAnalyzer, BenchmarkResult } from './ts-src';
import * as fs from 'fs';

// Load results from JSON
const results: BenchmarkResult[] = JSON.parse(
  fs.readFileSync('results/benchmark_results.json', 'utf-8')
);

// Create analyzer
const analyzer = new ResultsAnalyzer(results);

// Get summary statistics
const stats = analyzer.getSummaryStats();

// Export summary
analyzer.exportSummary('results/summary.json');
```

See `ts-src/README.md` for more details on the TypeScript implementation.

## Project Structure

```
DB_Testing/
├── config/
│   └── databases.yaml          # Database connection configurations
├── src/                        # Python implementation
│   ├── database/               # Database connection implementations
│   │   ├── base.py            # Base classes and interfaces
│   │   ├── relational.py      # Relational DB implementations
│   │   └── graph.py           # Graph DB implementations
│   ├── benchmarks/             # Benchmark test suites
│   │   ├── relational_benchmarks.py
│   │   └── graph_benchmarks.py
│   └── results/                # Results analysis (Python)
│       └── analyzer.py
├── ts-src/                     # TypeScript implementation
│   ├── types/                  # TypeScript type definitions
│   │   └── benchmark.ts       # Benchmark result types
│   ├── results/                # Results analysis (TypeScript)
│   │   ├── analyzer.ts        # ResultsAnalyzer class
│   │   └── index.ts           # Module exports
│   ├── index.ts                # Main TypeScript exports
│   ├── example.ts              # Usage examples
│   └── README.md               # TypeScript implementation docs
├── results/                    # Generated results (gitignored)
├── docker-compose.yml          # Docker setup for databases
├── requirements.txt            # Python dependencies
├── package.json                # Node.js/TypeScript dependencies
├── tsconfig.json               # TypeScript configuration
├── run_benchmarks.py           # Main benchmark runner (Python)
└── README.md
```

## Configuration

### Database Configuration

Edit `config/databases.yaml` to configure database connections:

```yaml
relational:
  postgresql:
    type: postgresql
    host: localhost
    port: 5432
    database: benchmark_db
    user: postgres
    password: postgres

graph:
  neo4j:
    type: neo4j
    uri: bolt://localhost:7687
    user: neo4j
    password: password
```

### Customizing Benchmarks

You can modify the benchmark parameters in `run_benchmarks.py` or create custom benchmark scripts by importing the benchmark classes:

```python
from src.database import PostgreSQLConnection
from src.database import BenchmarkRunner
from src.benchmarks import RelationalBenchmarks

# Create connection
config = {...}  # Your config
conn = PostgreSQLConnection(config)
conn.connect()

# Run benchmarks
runner = BenchmarkRunner(conn)
benchmarks = RelationalBenchmarks(conn, runner)

# Run specific benchmark
results = benchmarks.benchmark_insert_single(num_records=1000)
```

## Troubleshooting

### Database Connection Issues

1. **Check Docker containers are running**:
   ```bash
   docker-compose ps
   ```

2. **Check database logs**:
   ```bash
   docker-compose logs postgresql
   docker-compose logs mysql
   ```

3. **Verify connection settings** in `config/databases.yaml`

### Common Issues

- **Port conflicts**: If ports are already in use, modify `docker-compose.yml` to use different ports
- **Memory issues**: Some databases (especially Neo4j) may require more memory. Adjust Docker resource limits if needed
- **SQLite file permissions**: Ensure write permissions in the directory where SQLite creates its database file

## Contributing

To add support for additional databases:

1. Create a new connection class in `src/database/` (either `relational.py` or `graph.py`)
2. Implement the `DatabaseConnection` interface
3. Add configuration to `config/databases.yaml`
4. Update `run_benchmarks.py` to include the new database

## License

This project is open source and available for benchmarking and research purposes.

## Notes

- Benchmarks are designed to be fair comparisons but actual performance will vary based on hardware, data size, and configuration
- Results should be used as a guide rather than absolute performance guarantees
- For production decisions, run benchmarks with your specific workload and data patterns
