#!/usr/bin/env python3
"""Main script to run database benchmarks."""
import yaml
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database import (
    PostgreSQLConnection, MySQLConnection, SQLiteConnection,
    Neo4jConnection, ArangoDBConnection,
    BenchmarkRunner
)
from benchmarks import RelationalBenchmarks, GraphBenchmarks
from results import ResultsAnalyzer


def load_config(config_path: str = 'config/databases.yaml') -> Dict[str, Any]:
    """Load database configuration."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_connection(db_type: str, vendor: str, config: Dict[str, Any]) -> Any:
    """Get appropriate database connection instance."""
    db_config = config.get(db_type, {}).get(vendor, {})
    if not db_config:
        raise ValueError(f"Configuration not found for {db_type}/{vendor}")
    
    db_config['type'] = vendor
    
    if db_type == 'relational':
        if vendor == 'postgresql':
            return PostgreSQLConnection(db_config)
        elif vendor == 'mysql':
            return MySQLConnection(db_config)
        elif vendor == 'sqlite':
            return SQLiteConnection(db_config)
    elif db_type == 'graph':
        if vendor == 'neo4j':
            return Neo4jConnection(db_config)
        elif vendor == 'arangodb':
            return ArangoDBConnection(db_config)
    
    raise ValueError(f"Unsupported database: {db_type}/{vendor}")


def run_relational_benchmarks(vendors: List[str], config: Dict[str, Any], setup_data: bool = True):
    """Run benchmarks for relational databases."""
    all_results = []
    
    for vendor in vendors:
        print(f"\n{'='*60}")
        print(f"Running benchmarks for {vendor.upper()}")
        print(f"{'='*60}\n")
        
        try:
            connection = get_connection('relational', vendor, config)
            
            if not connection.connect():
                print(f"Failed to connect to {vendor}")
                continue
            
            print(f"Connected to {vendor}")
            
            # Setup schema
            print("Setting up schema...")
            if not connection.setup_schema():
                print(f"Failed to setup schema for {vendor}")
                connection.disconnect()
                continue
            
            runner = BenchmarkRunner(connection)
            benchmarks = RelationalBenchmarks(connection, runner)
            
            # Run benchmarks
            print("\nRunning benchmarks...")
            
            if setup_data:
                print("  - Inserting test data...")
                benchmarks.benchmark_insert_batch(batch_size=100, num_batches=10)
                
                # Create some posts for join tests
                user_ids = connection.execute_query("SELECT id FROM users LIMIT 100")
                if user_ids:
                    for i, row in enumerate(user_ids[:50]):
                        user_id = row[0] if isinstance(row, (list, tuple)) else row['id']
                        connection.execute_query(
                            "INSERT INTO posts (user_id, title, content) VALUES (%s, %s, %s)",
                            {'user_id': user_id, 'title': f"Post_{i}", 'content': f"Content_{i}"}
                        )
            
            print("  - Insert single records...")
            benchmarks.benchmark_insert_single(num_records=100)
            
            print("  - Insert batch records...")
            benchmarks.benchmark_insert_batch(batch_size=50, num_batches=5)
            
            print("  - Select by ID...")
            benchmarks.benchmark_select_by_id(num_queries=500)
            
            print("  - Select by email (indexed)...")
            benchmarks.benchmark_select_by_email(num_queries=500)
            
            print("  - Select with JOIN...")
            benchmarks.benchmark_select_with_join(num_queries=100)
            
            print("  - Update operations...")
            benchmarks.benchmark_update(num_updates=500)
            
            print("  - Aggregate queries...")
            benchmarks.benchmark_aggregate_query(num_queries=50)
            
            print("  - Complex queries...")
            benchmarks.benchmark_complex_query(num_queries=25)
            
            print("  - Delete operations...")
            benchmarks.benchmark_delete(num_deletes=50)
            
            all_results.extend(runner.get_results())
            
            # Cleanup
            print("\nCleaning up...")
            connection.cleanup()
            connection.disconnect()
            
        except Exception as e:
            print(f"Error running benchmarks for {vendor}: {e}")
            import traceback
            traceback.print_exc()
    
    return all_results


def run_graph_benchmarks(vendors: List[str], config: Dict[str, Any], setup_data: bool = True):
    """Run benchmarks for graph databases."""
    all_results = []
    
    for vendor in vendors:
        print(f"\n{'='*60}")
        print(f"Running benchmarks for {vendor.upper()}")
        print(f"{'='*60}\n")
        
        try:
            connection = get_connection('graph', vendor, config)
            
            if not connection.connect():
                print(f"Failed to connect to {vendor}")
                continue
            
            print(f"Connected to {vendor}")
            
            # Setup schema
            print("Setting up schema...")
            if not connection.setup_schema():
                print(f"Failed to setup schema for {vendor}")
                connection.disconnect()
                continue
            
            runner = BenchmarkRunner(connection)
            benchmarks = GraphBenchmarks(connection, runner)
            
            # Run benchmarks
            print("\nRunning benchmarks...")
            
            if setup_data:
                print("  - Creating nodes...")
                benchmarks.benchmark_create_nodes(num_nodes=500)
                
                print("  - Creating relationships...")
                benchmarks.benchmark_create_relationships(num_relationships=200)
            
            print("  - Create nodes...")
            benchmarks.benchmark_create_nodes(num_nodes=100)
            
            print("  - Create relationships...")
            benchmarks.benchmark_create_relationships(num_relationships=50)
            
            print("  - Find node by ID...")
            benchmarks.benchmark_find_node_by_id(num_queries=500)
            
            print("  - Traverse relationships...")
            benchmarks.benchmark_traverse_relationships(num_queries=100)
            
            print("  - Pattern matching...")
            benchmarks.benchmark_pattern_matching(num_queries=50)
            
            print("  - Shortest path...")
            benchmarks.benchmark_shortest_path(num_queries=25)
            
            all_results.extend(runner.get_results())
            
            # Cleanup
            print("\nCleaning up...")
            connection.cleanup()
            connection.disconnect()
            
        except Exception as e:
            print(f"Error running benchmarks for {vendor}: {e}")
            import traceback
            traceback.print_exc()
    
    return all_results


def main():
    parser = argparse.ArgumentParser(description='Run database benchmarks')
    parser.add_argument('--type', choices=['relational', 'graph', 'all'], default='all',
                       help='Type of databases to benchmark')
    parser.add_argument('--vendors', nargs='+',
                       help='Specific vendors to test (e.g., postgresql mysql)')
    parser.add_argument('--config', default='config/databases.yaml',
                       help='Path to database configuration file')
    parser.add_argument('--no-setup', action='store_true',
                       help='Skip initial data setup (use existing data)')
    parser.add_argument('--output-dir', default='results',
                       help='Directory to save results')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    all_results = []
    
    # Run relational benchmarks
    if args.type in ['relational', 'all']:
        relational_vendors = args.vendors or list(config.get('relational', {}).keys())
        if relational_vendors:
            results = run_relational_benchmarks(relational_vendors, config, not args.no_setup)
            all_results.extend(results)
    
    # Run graph benchmarks
    if args.type in ['graph', 'all']:
        graph_vendors = args.vendors or list(config.get('graph', {}).keys())
        if graph_vendors:
            results = run_graph_benchmarks(graph_vendors, config, not args.no_setup)
            all_results.extend(results)
    
    # Analyze and export results
    if all_results:
        print(f"\n{'='*60}")
        print("Analyzing results...")
        print(f"{'='*60}\n")
        
        analyzer = ResultsAnalyzer(all_results)
        
        # Print summary
        print("Summary Statistics:")
        print(analyzer.get_summary_stats())
        
        # Export results
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
        analyzer.export_to_csv(f"{args.output_dir}/benchmark_results.csv")
        analyzer.export_summary(f"{args.output_dir}/summary.json")
        
        # Generate plots
        print("\nGenerating plots...")
        analyzer.plot_all_operations(f"{args.output_dir}/plots")
        
        print(f"\nResults saved to {args.output_dir}/")
    else:
        print("No results to analyze.")


if __name__ == '__main__':
    main()

