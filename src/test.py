import requests
import time
import string
import json

base_url = "http://35.200.185.69:8000"

def test_api_behavior():
    """
    Test various aspects of the API behavior
    """
    findings = {}
    
    # 1. Test different versions (v1, v2, v3)
    versions = ["v1", "v2", "v3"]
    version_support = {}
    
    for version in versions:
        try:
            response = requests.get(f"{base_url}/{version}/autocomplete?query=a")
            if response.status_code == 200:
                version_support[version] = "Supported"
                version_support[f"{version}_sample"] = response.json()
            else:
                version_support[version] = f"Not supported (Status: {response.status_code})"
        except requests.exceptions.RequestException as e:
            version_support[version] = f"Error: {str(e)}"
    
    findings["version_support"] = version_support
    
    # 2. Test query length requirements (using v1)
    query_length = {}
    for length in range(5):
        query = "a" * length
        response = requests.get(f"{base_url}/v1/autocomplete?query={query}")
        query_length[length] = {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else None
        }
        time.sleep(0.5)  # Avoid potential rate limiting
        
    findings["query_length_requirements"] = query_length
    
    # 3. Test rate limiting
    rate_limit = {}
    for i in range(10):
        start_time = time.time()
        response = requests.get(f"{base_url}/v1/autocomplete?query=a")
        rate_limit[i] = {
            "status_code": response.status_code,
            "time": time.time() - start_time
        }
        
    findings["rate_limit_test"] = rate_limit
    
    # 4. Test different characters
    char_test = {}
    for char in string.ascii_lowercase[:5]:  # Test first 5 letters
        response = requests.get(f"{base_url}/v1/autocomplete?query={char}")
        if response.status_code == 200:
            results = response.json()
            char_test[char] = {
                "count": len(results) if isinstance(results, list) else "Not a list",
                "sample": results[:3] if isinstance(results, list) and results else "Empty"
            }
        time.sleep(0.5)
        
    findings["character_test"] = char_test
    
    # 5. Check if there are any additional parameters
    params_test = {}
    potential_params = ["limit", "offset", "max", "page", "start"]
    
    for param in potential_params:
        response = requests.get(f"{base_url}/v1/autocomplete?query=a&{param}=10")
        params_test[param] = {
            "status_code": response.status_code,
            "different_from_base": response.json() != findings["version_support"]["v1_sample"] if response.status_code == 200 else "N/A"
        }
        time.sleep(0.5)
        
    findings["additional_params"] = params_test
    
    return findings

# Run the behavior analysis
behavior_findings = test_api_behavior()
print(json.dumps(behavior_findings, indent=2))