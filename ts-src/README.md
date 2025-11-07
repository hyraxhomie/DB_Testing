# TypeScript Implementation

This directory contains the TypeScript implementation of the database benchmarking results analyzer.

## Structure

```
ts-src/
├── types/
│   └── benchmark.ts          # Type definitions for benchmark results
├── results/
│   ├── analyzer.ts           # Main ResultsAnalyzer class implementation
│   └── index.ts              # Results module exports
└── index.ts                  # Main module exports
```

## Overview

This TypeScript implementation mirrors the functionality of the Python implementation in `src/results/analyzer.py`, providing the same analysis capabilities:

- **Data Processing**: Convert and filter benchmark results
- **Statistical Analysis**: Compute mean, median, standard deviation, min, max, and count
- **Comparisons**: Compare database performance by operation type
- **Visualization**: Generate performance comparison summaries
- **Export**: Export results to CSV and JSON formats

## Key Differences from Python Implementation

1. **Data Structures**: Uses TypeScript Maps and arrays instead of pandas DataFrames
2. **File I/O**: Uses Node.js `fs` module instead of Python's file operations
3. **Statistics**: Manual calculation instead of pandas aggregation methods
4. **Visualization**: Currently uses text-based output (can be extended with charting libraries)

## Usage

### Building

```bash
npm install
npm run build
```

### Using in Your Code

```typescript
import { ResultsAnalyzer, BenchmarkResult } from './ts-src';

// Load your benchmark results
const results: BenchmarkResult[] = [
  {
    operation: 'insert_single',
    database: 'postgresql',
    vendor: 'postgresql',
    duration_ms: 12.5,
    success: true,
    records_affected: 1
  },
  // ... more results
];

// Create analyzer
const analyzer = new ResultsAnalyzer(results);

// Get summary statistics
const stats = analyzer.getSummaryStats();

// Export to CSV
analyzer.exportToCSV('results/benchmark_results.csv');

// Export summary to JSON
analyzer.exportSummary('results/summary.json');

// Generate plots
analyzer.plotAllOperations('results/plots');
```

## Extending Visualization

The current implementation uses text-based visualization. To add chart generation, you can:

1. Install a charting library:
   ```bash
   npm install chart.js node-canvas
   ```

2. Modify `plotOperationComparison` to generate actual charts
3. Use libraries like:
   - **Chart.js** with **node-canvas** for server-side rendering
   - **Plotly.js** for interactive charts
   - **D3.js** for custom visualizations

## Type Safety

All types are defined in `types/benchmark.ts` to ensure type safety throughout the implementation. The `BenchmarkResult` interface matches the Python dataclass structure for compatibility.

