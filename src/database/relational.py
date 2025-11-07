"""Relational database implementations."""
import psycopg2
import pymysql
import sqlite3
from typing import Dict, Any, Optional, List
from .base import DatabaseConnection


class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL database connection."""
    
    def connect(self) -> bool:
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            return True
        except Exception as e:
            print(f"PostgreSQL connection error: {e}")
            return False
    
    def disconnect(self) -> bool:
        if self.connection:
            self.connection.close()
            self.connection = None
        return True
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        cursor = self.connection.cursor()
        try:
            if params:
                # PostgreSQL uses %s with psycopg2, expects tuple/list
                # Convert dict to tuple (preserving insertion order in Python 3.7+)
                if isinstance(params, dict):
                    param_tuple = tuple(params.values())
                    cursor.execute(query, param_tuple)
                elif isinstance(params, (list, tuple)):
                    cursor.execute(query, params)
                else:
                    cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                self.connection.commit()
                return cursor.rowcount
        finally:
            cursor.close()
    
    def setup_schema(self) -> bool:
        try:
            queries = [
                """CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    age INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE IF NOT EXISTS posts (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    title VARCHAR(255) NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)""",
                """CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)"""
            ]
            
            for query in queries:
                self.execute_query(query)
            return True
        except Exception as e:
            print(f"PostgreSQL schema setup error: {e}")
            return False
    
    def cleanup(self) -> bool:
        try:
            self.execute_query("DROP TABLE IF EXISTS posts CASCADE")
            self.execute_query("DROP TABLE IF EXISTS users CASCADE")
            return True
        except Exception as e:
            print(f"PostgreSQL cleanup error: {e}")
            return False


class MySQLConnection(DatabaseConnection):
    """MySQL database connection."""
    
    def connect(self) -> bool:
        try:
            self.connection = pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                charset='utf8mb4'
            )
            return True
        except Exception as e:
            print(f"MySQL connection error: {e}")
            return False
    
    def disconnect(self) -> bool:
        if self.connection:
            self.connection.close()
            self.connection = None
        return True
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        cursor = self.connection.cursor()
        try:
            if params:
                # MySQL uses %s with pymysql, expects tuple/list
                # Convert dict to tuple (preserving insertion order in Python 3.7+)
                if isinstance(params, dict):
                    param_tuple = tuple(params.values())
                    cursor.execute(query, param_tuple)
                elif isinstance(params, (list, tuple)):
                    cursor.execute(query, params)
                else:
                    cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                self.connection.commit()
                return cursor.rowcount
        finally:
            cursor.close()
    
    def setup_schema(self) -> bool:
        try:
            queries = [
                """CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    age INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB""",
                """CREATE TABLE IF NOT EXISTS posts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    title VARCHAR(255) NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB""",
                """CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)""",
                """CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)"""
            ]
            
            for query in queries:
                self.execute_query(query)
            return True
        except Exception as e:
            print(f"MySQL schema setup error: {e}")
            return False
    
    def cleanup(self) -> bool:
        try:
            self.execute_query("DROP TABLE IF EXISTS posts")
            self.execute_query("DROP TABLE IF EXISTS users")
            return True
        except Exception as e:
            print(f"MySQL cleanup error: {e}")
            return False


class SQLiteConnection(DatabaseConnection):
    """SQLite database connection."""
    
    def connect(self) -> bool:
        try:
            self.connection = sqlite3.connect(
                self.config['database'],
                check_same_thread=False
            )
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"SQLite connection error: {e}")
            return False
    
    def disconnect(self) -> bool:
        if self.connection:
            self.connection.close()
            self.connection = None
        return True
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        cursor = self.connection.cursor()
        try:
            if params:
                # SQLite uses ? placeholders, not %s
                # Convert %s to ? and params to tuple/list
                if isinstance(params, dict):
                    # Convert dict to tuple/list in order
                    param_list = list(params.values())
                    # Replace %s with ? for SQLite
                    query_processed = query.replace('%s', '?')
                    cursor.execute(query_processed, param_list)
                elif isinstance(params, (list, tuple)):
                    # Replace %s with ? for SQLite
                    query_processed = query.replace('%s', '?')
                    cursor.execute(query_processed, params)
                else:
                    query_processed = query.replace('%s', '?')
                    cursor.execute(query_processed, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                self.connection.commit()
                return cursor.rowcount
        finally:
            cursor.close()
    
    def setup_schema(self) -> bool:
        try:
            queries = [
                """CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    age INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )""",
                """CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)""",
                """CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)"""
            ]
            
            for query in queries:
                self.execute_query(query)
            return True
        except Exception as e:
            print(f"SQLite schema setup error: {e}")
            return False
    
    def cleanup(self) -> bool:
        try:
            self.execute_query("DROP TABLE IF EXISTS posts")
            self.execute_query("DROP TABLE IF EXISTS users")
            return True
        except Exception as e:
            print(f"SQLite cleanup error: {e}")
            return False

