/**
 * Example usage of the TypeScript ResultsAnalyzer.
 * 
 * This file demonstrates how to use the TypeScript implementation
 * to analyze benchmark results, similar to how the Python version
 * is used in run_benchmarks.py.
 */

import { ResultsAnalyzer, BenchmarkResult } from './index';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Example: Load results from JSON file and analyze them.
 * 
 * This function shows how you might load benchmark results
 * (perhaps exported from the Python implementation) and analyze
 * them using the TypeScript analyzer.
 */
function analyzeFromJSON(jsonPath: string): void {
  // Read and parse JSON file containing benchmark results
  const jsonData = fs.readFileSync(jsonPath, 'utf-8');
  const results: BenchmarkResult[] = JSON.parse(jsonData);

  // Create analyzer instance
  const analyzer = new ResultsAnalyzer(results);

  // Get summary statistics
  console.log('\n=== Summary Statistics ===');
  const stats = analyzer.getSummaryStats();
  
  // Print summary (you can format this however you like)
  for (const [operation, dbStats] of stats.entries()) {
    console.log(`\nOperation: ${operation}`);
    for (const [database, stat] of dbStats.entries()) {
      console.log(`  ${database}: mean=${stat.mean.toFixed(2)}ms, count=${stat.count}`);
    }
  }

  // Export to CSV
  analyzer.exportToCSV('results/benchmark_results_ts.csv');

  // Export summary to JSON
  analyzer.exportSummary('results/summary_ts.json');

  // Generate plots
  console.log('\n=== Generating Plots ===');
  analyzer.plotAllOperations('results/plots_ts');
}

/**
 * Example: Create analyzer from in-memory results.
 * 
 * This shows how to use the analyzer with results
 * generated directly in TypeScript code.
 */
function analyzeInMemory(): void {
  // Create sample benchmark results
  const results: BenchmarkResult[] = [
    {
      operation: 'insert_single',
      database: 'postgresql',
      vendor: 'postgresql',
      duration_ms: 12.5,
      success: true,
      records_affected: 1
    },
    {
      operation: 'insert_single',
      database: 'postgresql',
      vendor: 'postgresql',
      duration_ms: 11.8,
      success: true,
      records_affected: 1
    },
    {
      operation: 'insert_single',
      database: 'mysql',
      vendor: 'mysql',
      duration_ms: 15.2,
      success: true,
      records_affected: 1
    },
    {
      operation: 'select_by_id',
      database: 'postgresql',
      vendor: 'postgresql',
      duration_ms: 2.1,
      success: true,
      records_affected: 0
    }
  ];

  // Create analyzer
  const analyzer = new ResultsAnalyzer(results);

  // Compare specific operation
  console.log('\n=== Comparison: insert_single ===');
  const comparison = analyzer.getComparisonByOperation('insert_single');
  
  for (const [database, stats] of comparison.entries()) {
    console.log(`${database}:`);
    console.log(`  Mean: ${stats.mean.toFixed(2)}ms`);
    console.log(`  Median: ${stats.median.toFixed(2)}ms`);
    console.log(`  Count: ${stats.count}`);
  }

  // Plot comparison
  analyzer.plotOperationComparison('insert_single');
}

/**
 * Example: Load from CSV (if you have CSV from Python implementation).
 * 
 * Note: This is a simple CSV parser. For production use,
 * consider using a library like 'csv-parse'.
 */
function analyzeFromCSV(csvPath: string): void {
  // Read CSV file
  const csvContent = fs.readFileSync(csvPath, 'utf-8');
  const lines = csvContent.split('\n').filter(line => line.trim());
  
  // Parse header
  const headers = lines[0].split(',').map(h => h.trim());
  
  // Parse data rows
  const results: BenchmarkResult[] = [];
  
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',');
    const row: any = {};
    
    headers.forEach((header, index) => {
      row[header] = values[index]?.trim();
    });
    
    // Convert to BenchmarkResult
    results.push({
      operation: row.operation,
      database: row.database,
      vendor: row.vendor,
      duration_ms: parseFloat(row.duration_ms),
      success: row.success === 'true',
      records_affected: parseInt(row.records_affected, 10)
    });
  }

  // Analyze
  const analyzer = new ResultsAnalyzer(results);
  
  // Export summary
  analyzer.exportSummary('results/summary_from_csv.json');
  
  console.log(`Analyzed ${results.length} results`);
}

// Main execution (uncomment to run examples)
if (require.main === module) {
  console.log('TypeScript ResultsAnalyzer Examples\n');
  
  // Example 1: Analyze from in-memory data
  console.log('Example 1: In-memory analysis');
  analyzeInMemory();
  
  // Example 2: Analyze from CSV (if file exists)
  const csvPath = 'results/benchmark_results.csv';
  if (fs.existsSync(csvPath)) {
    console.log('\n\nExample 2: CSV analysis');
    analyzeFromCSV(csvPath);
  }
}

