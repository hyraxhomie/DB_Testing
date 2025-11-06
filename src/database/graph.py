"""Graph database implementations."""
from typing import Dict, Any, Optional, List
from neo4j import GraphDatabase
from arango import ArangoClient
from .base import DatabaseConnection


class Neo4jConnection(DatabaseConnection):
    """Neo4j graph database connection."""
    
    def connect(self) -> bool:
        try:
            self.driver = GraphDatabase.driver(
                self.config['uri'],
                auth=(self.config['user'], self.config['password'])
            )
            # Verify connectivity
            self.driver.verify_connectivity()
            self.connection = self.driver
            return True
        except Exception as e:
            print(f"Neo4j connection error: {e}")
            return False
    
    def disconnect(self) -> bool:
        if self.driver:
            self.driver.close()
            self.connection = None
            self.driver = None
        return True
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        with self.driver.session() as session:
            if params:
                result = session.run(query, params)
            else:
                result = session.run(query)
            
            # For read queries, return records
            if query.strip().upper().startswith('MATCH'):
                return list(result)
            else:
                # For write queries, return summary
                summary = result.consume()
                return summary.counters.nodes_created + summary.counters.nodes_deleted
    
    def setup_schema(self) -> bool:
        try:
            # Neo4j doesn't require explicit schema, but we can create constraints
            queries = [
                "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
                "CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE",
                "CREATE CONSTRAINT post_id IF NOT EXISTS FOR (p:Post) REQUIRE p.id IS UNIQUE"
            ]
            
            for query in queries:
                try:
                    self.execute_query(query)
                except Exception:
                    # Constraint might already exist
                    pass
            return True
        except Exception as e:
            print(f"Neo4j schema setup error: {e}")
            return False
    
    def cleanup(self) -> bool:
        try:
            self.execute_query("MATCH (n) DETACH DELETE n")
            return True
        except Exception as e:
            print(f"Neo4j cleanup error: {e}")
            return False


class ArangoDBConnection(DatabaseConnection):
    """ArangoDB graph database connection."""
    
    def connect(self) -> bool:
        try:
            client = ArangoClient(hosts=self.config['host'])
            sys_db = client.db('_system', username=self.config['user'], password=self.config['password'])
            
            # Create database if it doesn't exist
            db_name = self.config['database']
            if not sys_db.has_database(db_name):
                sys_db.create_database(db_name)
            
            self.db = client.db(db_name, username=self.config['user'], password=self.config['password'])
            self.connection = self.db
            return True
        except Exception as e:
            print(f"ArangoDB connection error: {e}")
            return False
    
    def disconnect(self) -> bool:
        # ArangoDB client doesn't need explicit close
        self.connection = None
        self.db = None
        return True
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        cursor = self.db.aql.execute(query, bind_vars=params or {})
        if cursor.cached():
            return list(cursor)
        return cursor.count()
    
    def setup_schema(self) -> bool:
        try:
            # Create collections
            if not self.db.has_collection('users'):
                self.db.create_collection('users')
            if not self.db.has_collection('posts'):
                self.db.create_collection('posts')
            
            # Create graph
            if not self.db.has_graph('social_graph'):
                graph = self.db.create_graph('social_graph')
                graph.create_edge_definition(
                    edge_collection='writes',
                    from_vertex_collections=['users'],
                    to_vertex_collections=['posts']
                )
            else:
                graph = self.db.graph('social_graph')
            
            # Create indexes
            users_col = self.db.collection('users')
            if not users_col.has_index('email'):
                users_col.add_index({'type': 'persistent', 'fields': ['email'], 'unique': True})
            
            return True
        except Exception as e:
            print(f"ArangoDB schema setup error: {e}")
            return False
    
    def cleanup(self) -> bool:
        try:
            if self.db.has_graph('social_graph'):
                self.db.delete_graph('social_graph', drop_collections=True)
            if self.db.has_collection('users'):
                self.db.delete_collection('users')
            if self.db.has_collection('posts'):
                self.db.delete_collection('posts')
            return True
        except Exception as e:
            print(f"ArangoDB cleanup error: {e}")
            return False

