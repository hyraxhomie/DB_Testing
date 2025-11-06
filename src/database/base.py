"""Base classes for database connections and operations."""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import time
from dataclasses import dataclass


@dataclass
class BenchmarkResult:
    """Container for benchmark results."""
    operation: str
    database: str
    vendor: str
    duration_ms: float
    success: bool
    records_affected: int = 0
    error: Optional[str] = None


class DatabaseConnection(ABC):
    """Abstract base class for database connections."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        self.vendor = config.get('type', 'unknown')
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to database."""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Close database connection."""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute a query and return results."""
        pass
    
    @abstractmethod
    def setup_schema(self) -> bool:
        """Create necessary tables/collections for benchmarking."""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """Remove all test data."""
        pass
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self.connection is not None


class BenchmarkRunner:
    """Runs benchmarks against database connections."""
    
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
        self.results: List[BenchmarkResult] = []
    
    def run_benchmark(self, operation_name: str, operation_func, *args, **kwargs) -> BenchmarkResult:
        """Run a single benchmark operation."""
        start_time = time.perf_counter()
        success = False
        records_affected = 0
        error = None
        
        try:
            result = operation_func(*args, **kwargs)
            if isinstance(result, (int, tuple)):
                records_affected = result if isinstance(result, int) else result[0]
            success = True
        except Exception as e:
            error = str(e)
            success = False
        
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        
        result = BenchmarkResult(
            operation=operation_name,
            database=self.connection.vendor,
            vendor=self.connection.vendor,
            duration_ms=duration_ms,
            success=success,
            records_affected=records_affected,
            error=error
        )
        
        self.results.append(result)
        return result
    
    def get_results(self) -> List[BenchmarkResult]:
        """Get all benchmark results."""
        return self.results
    
    def clear_results(self):
        """Clear all results."""
        self.results = []

