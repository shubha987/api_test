import requests
import time
import string
import json
from collections import deque, Counter
import concurrent.futures

class AutocompleteAPIExtractor:
    def __init__(self, base_url="http://35.200.185.69:8000"):
        self.base_url = base_url
        self.versions = ["v1", "v2", "v3"]
        self.valid_versions = []
        self.request_count = {v: 0 for v in self.versions}
        self.results = {v: set() for v in self.versions}
        self.rate_limit_wait = 0.1  # Initial wait time between requests
        self.max_retries = 3
        
    def test_versions(self):
        """Check which API versions are available"""
        for version in self.versions:
            try:
                response = requests.get(f"{self.base_url}/{version}/autocomplete?query=a")
                if response.status_code == 200:
                    self.valid_versions.append(version)
                    print(f"✓ Version {version} is supported")
                else:
                    print(f"✗ Version {version} returned status code {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"✗ Error testing version {version}: {e}")
                
        return self.valid_versions
        
    def make_request(self, version, query):
        """Make a single request to the API with retry logic and rate limiting"""
        url = f"{self.base_url}/{version}/autocomplete?query={query}"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url)
                self.request_count[version] += 1
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Too Many Requests
                    wait_time = self.rate_limit_wait * (2 ** attempt)
                    print(f"Rate limited. Waiting {wait_time:.2f}s before retry.")
                    time.sleep(wait_time)
                    self.rate_limit_wait *= 1.5  # Increase wait time for future requests
                else:
                    print(f"Error: Status code {response.status_code} for query '{query}'")
                    return []
                    
            except requests.exceptions.RequestException as e:
                print(f"Request error for '{query}': {e}")
                time.sleep(self.rate_limit_wait)
                
        print(f"Max retries exceeded for query '{query}'")
        return []
    
    def bfs_approach(self, version, max_depth=5):
        """
        Use Breadth-First Search to explore all possible name combinations
        """
        print(f"\nExtracting names using BFS approach for {version}...")
        queue = deque(string.ascii_lowercase)
        seen = set(string.ascii_lowercase)
        
        depth = 1
        names_found = 0
        
        while queue and depth <= max_depth:
            # Report progress
            print(f"Depth {depth}: Queue size {len(queue)}, Names found so far: {names_found}")
            
            # Process all prefixes at the current depth
            level_size = len(queue)
            for _ in range(level_size):
                prefix = queue.popleft()
                
                # Get autocomplete results for this prefix
                results = self.make_request(version, prefix)
                
                # Handle different response formats
                if isinstance(results, list):
                    # Add new names to the results set
                    new_names = set(results) - self.results[version]
                    self.results[version].update(new_names)
                    names_found += len(new_names)
                    
                    # Check if we need to go deeper with this prefix
                    if len(results) > 0:
                        # If we have results but they're not too many, add next level prefixes
                        if len(results) < 20:  # Arbitrary threshold to avoid too many branches
                            # No need to add more prefixes as we already have all results for this prefix
                            pass
                        else:
                            # Add character extensions to the queue
                            for char in string.ascii_lowercase:
                                new_prefix = prefix + char
                                if new_prefix not in seen:
                                    queue.append(new_prefix)
                                    seen.add(new_prefix)
                
                # Add a small delay to avoid rate limiting
                time.sleep(self.rate_limit_wait)
            
            depth += 1
        
        print(f"BFS approach completed for {version}. Total names found: {len(self.results[version])}")
        return self.results[version]
    
    def optimized_approach(self, version):
        """
        An optimized approach that adapts based on API behavior
        """
        print(f"\nExtracting names using optimized approach for {version}...")
        all_names = set()
        prefixes_to_try = list(string.ascii_lowercase)
        
        # First, try single character prefixes
        for prefix in prefixes_to_try:
            results = self.make_request(version, prefix)
            
            if isinstance(results, list):
                all_names.update(results)
                print(f"Prefix '{prefix}' returned {len(results)} names. Total unique names: {len(all_names)}")
            
            time.sleep(self.rate_limit_wait)
        
        # Check if we got a reasonable number of results
        # If we received too many results with single characters, we may need to go deeper
        if all(len(self.make_request(version, c)) >= 100 for c in 'aeiou'):
            print("Single character queries return too many results. Trying two-character prefixes...")
            
            # Try two-character prefixes
            for first in string.ascii_lowercase:
                for second in string.ascii_lowercase:
                    prefix = first + second
                    results = self.make_request(version, prefix)
                    
                    if isinstance(results, list):
                        new_names = set(results) - all_names
                        all_names.update(new_names)
                        print(f"Prefix '{prefix}' returned {len(results)} names ({len(new_names)} new). Total: {len(all_names)}")
                    
                    time.sleep(self.rate_limit_wait)
        
        self.results[version] = all_names
        print(f"Optimized approach completed for {version}. Total names found: {len(all_names)}")
        return all_names
    
    def parallel_extraction(self, version, prefix_length=2):
        """
        Extract names using parallel requests for better efficiency
        """
        print(f"\nExtracting names using parallel approach for {version} with prefix length {prefix_length}...")
        all_names = set()
        
        # Generate all possible prefixes of the given length
        prefixes = []
        def generate_prefixes(current, depth):
            if depth == 0:
                prefixes.append(current)
                return
            for char in string.ascii_lowercase:
                generate_prefixes(current + char, depth - 1)
        
        generate_prefixes("", prefix_length)
        print(f"Generated {len(prefixes)} prefixes to query")
        
        # Function to process a single prefix
        def process_prefix(prefix):
            local_results = self.make_request(version, prefix)
            time.sleep(self.rate_limit_wait)  # Still respect rate limiting
            return set(local_results) if isinstance(local_results, list) else set()
        
        # Process prefixes in parallel
        batch_size = 10  # Process this many prefixes at a time
        for i in range(0, len(prefixes), batch_size):
            batch = prefixes[i:i+batch_size]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_prefix = {executor.submit(process_prefix, prefix): prefix for prefix in batch}
                
                for future in concurrent.futures.as_completed(future_to_prefix):
                    prefix = future_to_prefix[future]
                    try:
                        result_set = future.result()
                        new_names = result_set - all_names
                        all_names.update(new_names)
                        print(f"Prefix '{prefix}' returned {len(result_set)} names ({len(new_names)} new). Total: {len(all_names)}")
                    except Exception as e:
                        print(f"Error processing prefix '{prefix}': {e}")
            
            print(f"Processed {i+len(batch)}/{len(prefixes)} prefixes. Current total: {len(all_names)} names")
        
        self.results[version] = all_names
        print(f"Parallel approach completed for {version}. Total names found: {len(all_names)}")
        return all_names
    
    def discover_v3_endpoint(self):
        """Try to discover any special endpoints or features in v3"""
        if "v3" not in self.valid_versions:
            print("v3 is not a valid version")
            return None
            
        # Try different endpoints
        potential_endpoints = [
            "/v3/autocomplete/all",
            "/v3/names/all",
            "/v3/autocomplete/dump",
            "/v3/dump",
            "/v3/names"
        ]
        
        for endpoint in potential_endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                print(f"Trying endpoint: {url}")
                response = requests.get(url)
                self.request_count["v3"] += 1
                
                if response.status_code == 200:
                    print(f"✓ Found working endpoint: {endpoint}")
                    try:
                        data = response.json()
                        if isinstance(data, list) and len(data) > 0:
                            self.results["v3"] = set(data)
                            print(f"Retrieved {len(data)} names from {endpoint}")
                            return data
                    except:
                        print("Response is not valid JSON")
            except:
                pass
                
            time.sleep(self.rate_limit_wait)
            
        print("No special endpoints found for v3")
        return None
    
    def run_extraction(self):
        """Run the complete extraction process for all valid versions"""
        # First check which versions are supported
        self.test_versions()
        
        for version in self.valid_versions:
            if version == "v1":
                # Use BFS approach for v1
                self.bfs_approach(version)
            elif version == "v2":
                # Use parallel approach for v2
                self.parallel_extraction(version, prefix_length=2)
            elif version == "v3":
                # Try to discover special endpoints for v3
                v3_data = self.discover_v3_endpoint()
                
                # If no special endpoint, fall back to optimized approach
                if not v3_data:
                    self.optimized_approach(version)
        
        # Print statistics
        self.print_statistics()
        
    def print_statistics(self):
        """Print statistics about the extraction process"""
        print("\n--- EXTRACTION STATISTICS ---")
        for version in self.valid_versions:
            print(f"\n{version.upper()} Statistics:")
            print(f"- Total requests made: {self.request_count[version]}")
            print(f"- Total unique names found: {len(self.results[version])}")
            
            if self.results[version]:
                print(f"- Sample names: {list(self.results[version])[:5]}")
        
        # Write results to files
        for version in self.valid_versions:
            with open(f"{version}_names.json", "w") as f:
                json.dump(list(self.results[version]), f, indent=2)
            print(f"\nSaved {version} results to {version}_names.json")

# Run the extraction
extractor = AutocompleteAPIExtractor()
extractor.run_extraction()