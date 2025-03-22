import requests
import time
import json

def test_autocomplete(base_url, version, query):
    url = f"{base_url}/{version}/autocomplete?query={query}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return None

# Base URL
base_url = "http://35.200.185.69:8000"

# Test with a simple query
result = test_autocomplete(base_url, "v1", "a")
print(json.dumps(result, indent=2))