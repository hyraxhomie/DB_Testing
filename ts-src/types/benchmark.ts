/**
 * TypeScript type definitions for benchmark results.
 * 
 * This file defines the data structures used throughout the TypeScript
 * implementation of the results analyzer.
 */

/**
 * Represents a single benchmark result from a database operation.
 * 
 * This interface matches the Python BenchmarkResult dataclass structure,
 * ensuring compatibility between Python and TypeScript implementations.
 */
export interface BenchmarkResult {
  /** Name of the operation that was benchmarked (e.g., "insert_single", "select_by_id") */
  operation: string;
  
  /** Name of the database vendor (e.g., "postgresql", "neo4j") */
  database: string;
  
  /** Vendor identifier (typically same as database) */
  vendor: string;
  
  /** Duration of the operation in milliseconds */
  duration_ms: number;
  
  /** Whether the operation completed successfully */
  success: boolean;
  
  /** Number of records affected by the operation (0 for read operations) */
  records_affected: number;
  
  /** Error message if the operation failed (null if successful) */
  error?: string | null;
}

/**
 * Summary statistics for a specific operation and database combination.
 * 
 * Used when aggregating results to compute statistical measures.
 */
export interface OperationStats {
  /** Mean (average) duration in milliseconds */
  mean: number;
  
  /** Median duration in milliseconds */
  median: number;
  
  /** Standard deviation of durations in milliseconds */
  std: number;
  
  /** Minimum duration in milliseconds */
  min: number;
  
  /** Maximum duration in milliseconds */
  max: number;
  
  /** Total number of successful operations */
  count: number;
}

/**
 * Summary structure organized by operation and database.
 * 
 * This matches the JSON structure exported by the Python implementation.
 */
export interface SummaryData {
  [operation: string]: {
    [database: string]: OperationStats;
  };
}

/**
 * Row data structure for CSV export.
 * 
 * Flattened representation of BenchmarkResult suitable for CSV format.
 */
export interface CSVRow {
  operation: string;
  database: string;
  vendor: string;
  duration_ms: number;
  success: boolean;
  records_affected: number;
}

