"""Benchmark tests for graph databases."""
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


class GraphBenchmarks:
    """Benchmark suite for graph databases."""
    
    def __init__(self, connection: DatabaseConnection, runner: BenchmarkRunner):
        self.connection = connection
        self.runner = runner
        self.vendor = connection.vendor
    
    def benchmark_create_nodes(self, num_nodes: int = 1000) -> List:
        """Benchmark creating nodes."""
        results = []
        
        if self.vendor == 'neo4j':
            for i in range(num_nodes):
                name = f"User_{i}"
                email = generate_random_email()
                age = random.randint(18, 80)
                
                result = self.runner.run_benchmark(
                    "create_node",
                    lambda: self.connection.execute_query(
                        "CREATE (u:User {id: $id, name: $name, email: $email, age: $age})",
                        {'id': i, 'name': name, 'email': email, 'age': age}
                    )
                )
                results.append(result)
        
        elif self.vendor == 'arangodb':
            batch_size = 100
            for batch_start in range(0, num_nodes, batch_size):
                batch_end = min(batch_start + batch_size, num_nodes)
                docs = []
                for i in range(batch_start, batch_end):
                    docs.append({
                        '_key': str(i),
                        'id': i,
                        'name': f"User_{i}",
                        'email': generate_random_email(),
                        'age': random.randint(18, 80)
                    })
                
                result = self.runner.run_benchmark(
                    "create_node",
                    lambda: self.connection.db.collection('users').import_bulk(docs)
                )
                results.append(result)
        
        return results
    
    def benchmark_create_relationships(self, num_relationships: int = 500) -> List:
        """Benchmark creating relationships/edges."""
        results = []
        
        if self.vendor == 'neo4j':
            # Get existing user IDs
            users = self.connection.execute_query("MATCH (u:User) RETURN u.id LIMIT 1000")
            if not users:
                return results
            
            user_ids = [record['u.id'] for record in users]
            
            for i in range(min(num_relationships, len(user_ids) - 1)):
                user_id = random.choice(user_ids)
                post_id = i
                title = f"Post_{i}"
                
                result = self.runner.run_benchmark(
                    "create_relationship",
                    lambda: self.connection.execute_query(
                        """MATCH (u:User {id: $user_id})
                           CREATE (p:Post {id: $post_id, title: $title})
                           CREATE (u)-[:WRITES]->(p)""",
                        {'user_id': user_id, 'post_id': post_id, 'title': title}
                    )
                )
                results.append(result)
        
        elif self.vendor == 'arangodb':
            # Get existing user keys
            users = list(self.connection.db.collection('users').all(limit=1000))
            if not users:
                return results
            
            user_keys = [u['_key'] for u in users]
            
            for i in range(min(num_relationships, len(user_keys))):
                user_key = random.choice(user_keys)
                post_key = f"post_{i}"
                
                # Create post
                post_doc = {
                    '_key': post_key,
                    'id': i,
                    'title': f"Post_{i}"
                }
                self.connection.db.collection('posts').insert(post_doc)
                
                # Create edge
                result = self.runner.run_benchmark(
                    "create_relationship",
                    lambda: self.connection.db.collection('writes').insert({
                        '_from': f"users/{user_key}",
                        '_to': f"posts/{post_key}"
                    })
                )
                results.append(result)
        
        return results
    
    def benchmark_find_node_by_id(self, num_queries: int = 1000) -> List:
        """Benchmark finding nodes by ID."""
        results = []
        
        if self.vendor == 'neo4j':
            users = self.connection.execute_query("MATCH (u:User) RETURN u.id LIMIT 1000")
            if not users:
                return results
            
            user_ids = [record['u.id'] for record in users]
            
            for _ in range(min(num_queries, len(user_ids))):
                user_id = random.choice(user_ids)
                result = self.runner.run_benchmark(
                    "find_node_by_id",
                    lambda: self.connection.execute_query(
                        "MATCH (u:User {id: $id}) RETURN u",
                        {'id': user_id}
                    )
                )
                results.append(result)
        
        elif self.vendor == 'arangodb':
            users = list(self.connection.db.collection('users').all(limit=1000))
            if not users:
                return results
            
            user_keys = [u['_key'] for u in users]
            
            for _ in range(min(num_queries, len(user_keys))):
                user_key = random.choice(user_keys)
                result = self.runner.run_benchmark(
                    "find_node_by_id",
                    lambda: self.connection.db.collection('users').get(user_key)
                )
                results.append(result)
        
        return results
    
    def benchmark_traverse_relationships(self, num_queries: int = 100) -> List:
        """Benchmark traversing relationships."""
        results = []
        
        if self.vendor == 'neo4j':
            users = self.connection.execute_query("MATCH (u:User) RETURN u.id LIMIT 100")
            if not users:
                return results
            
            user_ids = [record['u.id'] for record in users]
            
            for _ in range(min(num_queries, len(user_ids))):
                user_id = random.choice(user_ids)
                result = self.runner.run_benchmark(
                    "traverse_relationships",
                    lambda: self.connection.execute_query(
                        """MATCH (u:User {id: $id})-[:WRITES]->(p:Post)
                           RETURN u, collect(p) as posts""",
                        {'id': user_id}
                    )
                )
                results.append(result)
        
        elif self.vendor == 'arangodb':
            users = list(self.connection.db.collection('users').all(limit=100))
            if not users:
                return results
            
            user_keys = [u['_key'] for u in users]
            
            for _ in range(min(num_queries, len(user_keys))):
                user_key = random.choice(user_keys)
                result = self.runner.run_benchmark(
                    "traverse_relationships",
                    lambda: self.connection.execute_query(
                        """FOR v, e, p IN 1..1 OUTBOUND @start_id writes
                           RETURN v""",
                        {'start_id': f"users/{user_key}"}
                    )
                )
                results.append(result)
        
        return results
    
    def benchmark_shortest_path(self, num_queries: int = 50) -> List:
        """Benchmark shortest path queries."""
        results = []
        
        if self.vendor == 'neo4j':
            users = self.connection.execute_query("MATCH (u:User) RETURN u.id LIMIT 100")
            if not users or len(users) < 2:
                return results
            
            user_ids = [record['u.id'] for record in users]
            
            for _ in range(min(num_queries, len(user_ids) // 2)):
                start_id = random.choice(user_ids)
                end_id = random.choice([uid for uid in user_ids if uid != start_id])
                
                result = self.runner.run_benchmark(
                    "shortest_path",
                    lambda: self.connection.execute_query(
                        """MATCH path = shortestPath(
                            (start:User {id: $start_id})-[*]-(end:User {id: $end_id})
                           )
                           RETURN path""",
                        {'start_id': start_id, 'end_id': end_id}
                    )
                )
                results.append(result)
        
        elif self.vendor == 'arangodb':
            # ArangoDB shortest path query
            users = list(self.connection.db.collection('users').all(limit=100))
            if not users or len(users) < 2:
                return results
            
            user_keys = [u['_key'] for u in users]
            
            for _ in range(min(num_queries, len(user_keys) // 2)):
                start_key = random.choice(user_keys)
                end_key = random.choice([k for k in user_keys if k != start_key])
                
                result = self.runner.run_benchmark(
                    "shortest_path",
                    lambda: self.connection.execute_query(
                        """FOR v, e, p IN ANY SHORTEST_PATH
                           @start_id TO @end_id
                           writes
                           RETURN p""",
                        {'start_id': f"users/{start_key}", 'end_id': f"users/{end_key}"}
                    )
                )
                results.append(result)
        
        return results
    
    def benchmark_pattern_matching(self, num_queries: int = 100) -> List:
        """Benchmark pattern matching queries."""
        results = []
        
        if self.vendor == 'neo4j':
            for _ in range(num_queries):
                min_age = random.randint(18, 40)
                result = self.runner.run_benchmark(
                    "pattern_matching",
                    lambda: self.connection.execute_query(
                        """MATCH (u:User)-[:WRITES]->(p:Post)
                           WHERE u.age > $min_age
                           RETURN u.name, collect(p.title) as posts
                           ORDER BY size(posts) DESC
                           LIMIT 10""",
                        {'min_age': min_age}
                    )
                )
                results.append(result)
        
        elif self.vendor == 'arangodb':
            for _ in range(num_queries):
                min_age = random.randint(18, 40)
                result = self.runner.run_benchmark(
                    "pattern_matching",
                    lambda: self.connection.execute_query(
                        """FOR u IN users
                           FILTER u.age > @min_age
                           FOR v, e, p IN 1..1 OUTBOUND u writes
                           COLLECT user = u.name INTO posts = v.title
                           SORT LENGTH(posts) DESC
                           LIMIT 10
                           RETURN {user: user, posts: posts}""",
                        {'min_age': min_age}
                    )
                )
                results.append(result)
        
        return results

