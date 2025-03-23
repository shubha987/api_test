# API Testing Framework

A comprehensive testing framework for analyzing and extracting data from an autocomplete API with multiple versions (v1, v2, v3).

## Overview

This project implements multiple approaches to test and analyze an autocomplete API endpoint. The framework includes:

- Response pattern analysis
- Data extraction with different strategies
- API behavior testing
- Rate limiting handling

## Components

### 1. Response Analyzer ([responseanalye.py](src/responseanalye.py))

Analyzes API response patterns including:
- Single character query statistics
- Two character combination tests
- Pagination parameter testing
- Response pattern consistency checks

```python
analyzer = APIResponseAnalyzer()
analysis_results = analyzer.run_analysis()
```

### 2. Data Extractor ([extractor.py](src/extractor.py))

Implements multiple strategies for data extraction:

- **BFS Approach**: Uses breadth-first search to explore name combinations
- **Parallel Extraction**: Makes concurrent API requests for better efficiency
- **Optimized Approach**: Adapts based on API behavior
- **V3 Endpoint Discovery**: Attempts to find special endpoints in v3

```python
extractor = AutocompleteAPIExtractor()
extractor.run_extraction()
```

### 3. API Behavior Testing ([test.py](src/test.py))

Tests various aspects of the API including:
- Version support
- Query length requirements
- Rate limiting behavior
- Character response patterns
- Additional parameter support

## Key Features

- Automatic version detection and support
- Rate limiting handling with exponential backoff
- Multiple extraction strategies
- Parallel request handling
- Results persistence to JSON files
- Comprehensive API behavior analysis

## Usage

1. Run the response analyzer:
```bash
python src/responseanalye.py
```

2. Execute the data extractor:
```bash
python src/extractor.py
```

3. Test API behavior:
```bash
python src/test.py
```

## Results

The framework generates several output files:
- `api_analysis_results.json`: Contains detailed API behavior analysis
- `v1_names.json`: Names extracted from v1 endpoint
- `v2_names.json`: Names extracted from v2 endpoint
- `v3_names.json`: Names extracted from v3 endpoint

## Implementation Details

### Rate Limiting
- Initial wait time: 0.1 seconds
- Exponential backoff on 429 responses
- Maximum retry attempts: 3

### Extraction Strategies
1. **BFS Approach (v1)**
   - Uses character-by-character exploration
   - Maximum depth: 5 levels
   - Adaptive queue management

2. **Parallel Approach (v2)**
   - Concurrent requests with ThreadPoolExecutor
   - Batch size: 10 requests
   - Maximum 5 worker threads

3. **Optimized Approach (v3)**
   - Adaptive prefix length
   - Special endpoint discovery
   - Fallback to optimized sequential requests

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
