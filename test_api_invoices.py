import requests
import json
import urllib.parse

# Replace with your actual API base URL and endpoint
API_BASE_URL = "https://axonaut.com"
API_ENDPOINT = "/api/v2/invoices"

# Replace with your actual API key
API_KEY = "c3db28c18964b774aaaf1a18f72cb409"

# Set up headers (including authorization)
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "userApiKey": API_KEY  # Add the userApiKey header
}

# First, try a simple request without date parameters
try:
    # Construct the API URL
    url = f"{API_BASE_URL}{API_ENDPOINT}"

    print(f"Making request to: {url}")
    print(f"Headers: {headers}")

    # Make the API request without parameters
    response = requests.get(url, headers=headers)

    print(f"Status code: {response.status_code}")
    print(f"Response headers: {response.headers}")

    # Check if successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        print("Request successful! Response data:")
        print(json.dumps(data, indent=4))
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(f"Response text: {response.text}")

    # Now try with date parameters
    print("\n--- Now trying with date parameters ---\n")

    # Date format as specified in the documentation
    date_after = "28/02/2025"
    date_before = "01/03/2025"

    # Try without URL encoding first
    params = {
        "date_after": date_after,
        "date_before": date_before
    }

    print(f"Making request to: {url}")
    print(f"Headers: {headers}")
    print(f"Parameters: {params}")

    response = requests.get(url, headers=headers, params=params)

    print(f"Status code: {response.status_code}")
    print(f"Response headers: {response.headers}")

    if response.status_code == 200:
        data = response.json()
        print("Request successful! Response data:")
        print(json.dumps(data, indent=4))

        # Save the JSON data to a file
        with open("axonaut_invoices.json", "w") as f:
            json.dump(data, f, indent=4)  # Save with pretty formatting

        print("JSON data saved to axonaut_invoices.json")
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(f"Response text: {response.text}")

except Exception as e:
    print(f"An error occurred: {e}")
