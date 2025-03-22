import requests
import time
import string
import json
from collections import Counter

class APIResponseAnalyzer:
    def __init__(self, base_url="http://35.200.185.69:8000"):
        self.base_url = base_url
        self.versions = ["v1", "v2", "v3"]
        self.rate_limit_wait = 0.2
        
    def analyze_response_patterns(self, version):
        """Analyze patterns in API responses for a given version"""
        print(f"\nAnalyzing response patterns for {version}...")
        
        # Test single character queries
        single_char_stats = {}
        for char in string.ascii_lowercase:
            url = f"{self.base_url}/{version}/autocomplete?query={char}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        single_char_stats[char] = {
                            "count": len(data),
                            "starts_with_query": sum(1 for name in data if name.lower().startswith(char)),
                            "name_lengths": Counter([len(name) for name in data])
                        }
                time.sleep(self.rate_limit_wait)
            except Exception as e:
                print(f"Error analyzing {char}: {e}")
        
        # Test two character queries for a few combinations
        two_char_stats = {}
        test_prefixes = ["aa", "ab", "ba", "ca", "ma", "za"]
        
        for prefix in test_prefixes:
            url = f"{self.base_url}/{version}/autocomplete?query={prefix}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        two_char_stats[prefix] = {
                            "count": len(data),
                            "starts_with_query": sum(1 for name in data if name.lower().startswith(prefix)),
                            "name_lengths": Counter([len(name) for name in data])
                        }
                time.sleep(self.rate_limit_wait)
            except Exception as e:
                print(f"Error analyzing {prefix}: {e}")
        
        # Check possible pagination or limit parameters
        pagination_test = {}
        test_params = [
            {"limit": 10},
            {"offset": 10},
            {"page": 2},
            {"max": 5},
            {"count": 20}
        ]
        
        for params in test_params:
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{self.base_url}/{version}/autocomplete?query=a&{param_str}"
            
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        pagination_test[param_str] = {
                            "status": response.status_code,
                            "count": len(data)
                        }
                time.sleep(self.rate_limit_wait)
            except Exception as e:
                print(f"Error testing pagination {param_str}: {e}")
        
        # Analyze result patterns
        print("\nSingle character query statistics:")
        total_results = sum(stats["count"] for stats in single_char_stats.values())
        chars_with_results = sum(1 for stats in single_char_stats.values() if stats["count"] > 0)
        avg_results = total_results / max(1, chars_with_results)
        
        print(f"- Average results per character: {avg_results:.1f}")
        print(f"- Characters with most results: {sorted(single_char_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:3]}")
        print(f"- Characters with least results: {sorted(single_char_stats.items(), key=lambda x: x[1]['count'])[:3]}")
        
        # Check if results always start with the query
        always_starts_with = all(
            stats["starts_with_query"] == stats["count"] 
            for stats in single_char_stats.values() 
            if stats["count"] > 0
        )
        
        print(f"- Results always start with query: {always_starts_with}")
        
        # Check if pagination appears to work
        print("\nPagination test results:")
        for param, result in pagination_test.items():
            print(f"- {param}: {result['count']} results")
        
        # Return the analysis
        return {
            "single_char_stats": single_char_stats,
            "two_char_stats": two_char_stats,
            "pagination_test": pagination_test,
            "always_starts_with_query": always_starts_with,
            "avg_results_per_char": avg_results
        }
    
    def run_analysis(self):
        """Run analysis on all valid versions"""
        results = {}
        
        for version in self.versions:
            # First check if version exists
            try:
                response = requests.get(f"{self.base_url}/{version}/autocomplete?query=a")
                if response.status_code == 200:
                    results[version] = self.analyze_response_patterns(version)
            except Exception as e:
                print(f"Error checking version {version}: {e}")
        
        # Save analysis results
        with open("api_analysis_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print("\nAnalysis complete. Results saved to api_analysis_results.json")
        return results

# Run the analysis
analyzer = APIResponseAnalyzer()
analysis_results = analyzer.run_analysis()