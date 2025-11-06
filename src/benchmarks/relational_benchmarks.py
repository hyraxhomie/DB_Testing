"""Benchmark tests for relational databases."""
import random
import string
from typing import List, Dict, Any
from ..database.base import BenchmarkRunner, DatabaseConnection


def generate_random_string(length: int = 10) -> str:
    """Generate a random string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_email() -> str:
    """Generate a random email address."""
    return f"{generate_random_string(8)}@{generate_random_string(6)}.com"


class RelationalBenchmarks:
    """Benchmark suite for relational databases."""
    
    def __init__(self, connection: DatabaseConnection, runner: BenchmarkRunner):
        self.connection = connection
        self.runner = runner
    
    def benchmark_insert_single(self, num_records: int = 1000) -> List:
        """Benchmark single record inserts."""
        results = []
        for i in range(num_records):
            name = f"User_{i}"
            email = generate_random_email()
            age = random.randint(18, 80)
            
            # Use tuple for parameters to work with all databases
            result = self.runner.run_benchmark(
                "insert_single",
                lambda n=name, e=email, a=age: self.connection.execute_query(
                    "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)",
                    {'name': n, 'email': e, 'age': a}
                )
            )
            results.append(result)
        return results
    
    def benchmark_insert_batch(self, batch_size: int = 100, num_batches: int = 10) -> List:
        """Benchmark batch inserts."""
        results = []
        for batch in range(num_batches):
            values = []
            params = []
            for i in range(batch_size):
                name = f"User_{batch}_{i}"
                email = generate_random_email()
                age = random.randint(18, 80)
                values.append("(%s, %s, %s)")
                params.extend([name, email, age])
            
            query = f"INSERT INTO users (name, email, age) VALUES {','.join(values)}"
            result = self.runner.run_benchmark(
                "insert_batch",
                lambda: self.connection.execute_query(query, params)
            )
            results.append(result)
        return results
    
    def benchmark_select_by_id(self, num_queries: int = 1000) -> List:
        """Benchmark SELECT by primary key."""
        results = []
        # First, get some user IDs
        user_ids = self.connection.execute_query("SELECT id FROM users LIMIT 1000")
        if not user_ids:
            return results
        
        ids = [row[0] if isinstance(row, (list, tuple)) else row['id'] for row in user_ids]
        
        for _ in range(min(num_queries, len(ids))):
            user_id = random.choice(ids)
            result = self.runner.run_benchmark(
                "select_by_id",
                lambda: self.connection.execute_query(
                    "SELECT * FROM users WHERE id = %s",
                    {'id': user_id}
                )
            )
            results.append(result)
        return results
    
    def benchmark_select_by_email(self, num_queries: int = 1000) -> List:
        """Benchmark SELECT by indexed column (email)."""
        results = []
        emails = self.connection.execute_query("SELECT email FROM users LIMIT 1000")
        if not emails:
            return results
        
        email_list = [row[0] if isinstance(row, (list, tuple)) else row['email'] for row in emails]
        
        for _ in range(min(num_queries, len(email_list))):
            email = random.choice(email_list)
            result = self.runner.run_benchmark(
                "select_by_email",
                lambda: self.connection.execute_query(
                    "SELECT * FROM users WHERE email = %s",
                    {'email': email}
                )
            )
            results.append(result)
        return results
    
    def benchmark_select_with_join(self, num_queries: int = 100) -> List:
        """Benchmark SELECT with JOIN."""
        results = []
        user_ids = self.connection.execute_query("SELECT id FROM users LIMIT 100")
        if not user_ids:
            return results
        
        ids = [row[0] if isinstance(row, (list, tuple)) else row['id'] for row in user_ids]
        
        for _ in range(min(num_queries, len(ids))):
            user_id = random.choice(ids)
            result = self.runner.run_benchmark(
                "select_with_join",
                lambda: self.connection.execute_query(
                    """SELECT u.id, u.name, u.email, p.id as post_id, p.title 
                       FROM users u 
                       LEFT JOIN posts p ON u.id = p.user_id 
                       WHERE u.id = %s""",
                    {'id': user_id}
                )
            )
            results.append(result)
        return results
    
    def benchmark_update(self, num_updates: int = 1000) -> List:
        """Benchmark UPDATE operations."""
        results = []
        user_ids = self.connection.execute_query("SELECT id FROM users LIMIT 1000")
        if not user_ids:
            return results
        
        ids = [row[0] if isinstance(row, (list, tuple)) else row['id'] for row in user_ids]
        
        for _ in range(min(num_updates, len(ids))):
            user_id = random.choice(ids)
            new_age = random.randint(18, 80)
            result = self.runner.run_benchmark(
                "update",
                lambda: self.connection.execute_query(
                    "UPDATE users SET age = %s WHERE id = %s",
                    {'age': new_age, 'id': user_id}
                )
            )
            results.append(result)
        return results
    
    def benchmark_delete(self, num_deletes: int = 100) -> List:
        """Benchmark DELETE operations."""
        results = []
        user_ids = self.connection.execute_query("SELECT id FROM users LIMIT 1000")
        if not user_ids:
            return results
        
        ids = [row[0] if isinstance(row, (list, tuple)) else row['id'] for row in user_ids]
        
        for _ in range(min(num_deletes, len(ids))):
            user_id = random.choice(ids)
            result = self.runner.run_benchmark(
                "delete",
                lambda: self.connection.execute_query(
                    "DELETE FROM users WHERE id = %s",
                    {'id': user_id}
                )
            )
            results.append(result)
            # Remove from list to avoid trying to delete same ID twice
            if user_id in ids:
                ids.remove(user_id)
        return results
    
    def benchmark_aggregate_query(self, num_queries: int = 100) -> List:
        """Benchmark aggregate queries (COUNT, AVG, etc.)."""
        results = []
        for _ in range(num_queries):
            result = self.runner.run_benchmark(
                "aggregate_query",
                lambda: self.connection.execute_query(
                    """SELECT 
                        COUNT(*) as total_users,
                        AVG(age) as avg_age,
                        MIN(age) as min_age,
                        MAX(age) as max_age
                       FROM users"""
                )
            )
            results.append(result)
        return results
    
    def benchmark_complex_query(self, num_queries: int = 50) -> List:
        """Benchmark complex queries with multiple conditions."""
        results = []
        for _ in range(num_queries):
            min_age = random.randint(18, 40)
            max_age = random.randint(41, 80)
            result = self.runner.run_benchmark(
                "complex_query",
                lambda: self.connection.execute_query(
                    """SELECT u.id, u.name, u.email, COUNT(p.id) as post_count
                       FROM users u
                       LEFT JOIN posts p ON u.id = p.user_id
                       WHERE u.age BETWEEN %s AND %s
                       GROUP BY u.id, u.name, u.email
                       HAVING COUNT(p.id) > 0
                       ORDER BY post_count DESC
                       LIMIT 10""",
                    {'min_age': min_age, 'max_age': max_age}
                )
            )
            results.append(result)
        return results

