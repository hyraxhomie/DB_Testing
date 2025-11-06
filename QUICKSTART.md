# Quick Start Guide

Get up and running with database benchmarks in minutes!

## 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Start Databases

```bash
docker-compose up -d
```

Wait for all databases to be ready (about 30 seconds):
```bash
docker-compose ps
```

## 3. Run Your First Benchmark

**Quick test with SQLite** (no Docker needed):
```bash
python run_benchmarks.py --type relational --vendors sqlite
```

**Test all relational databases**:
```bash
python run_benchmarks.py --type relational
```

**Test all graph databases**:
```bash
python run_benchmarks.py --type graph
```

**Full benchmark suite**:
```bash
python run_benchmarks.py
```

## 4. View Results

Results are saved in the `results/` directory:
- `benchmark_results.csv` - Detailed data
- `summary.json` - Statistics summary
- `plots/` - Visualization charts

## Common Commands

```bash
# Compare PostgreSQL vs MySQL
python run_benchmarks.py --type relational --vendors postgresql mysql

# Test only Neo4j
python run_benchmarks.py --type graph --vendors neo4j

# Skip data setup (use existing data)
python run_benchmarks.py --no-setup
```

## Troubleshooting

**Can't connect to databases?**
- Check Docker: `docker-compose ps`
- Check logs: `docker-compose logs postgresql`
- Verify ports aren't in use

**SQLite works but others don't?**
- Make sure Docker containers are running
- Check `config/databases.yaml` settings

**Need help?**
- See full README.md for detailed documentation
- Check database logs: `docker-compose logs <service-name>`

