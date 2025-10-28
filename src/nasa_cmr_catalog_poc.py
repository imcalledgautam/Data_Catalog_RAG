import requests
import json
from pprint import pprint

def fetch_nasa_cmr_catalog():
    """
    Fetches a list of collections (data catalog entries) from the NASA CMR Search API.
    
    This simulates the programmatic retrieval of metadata from a data catalog.
    """
    # 1. Configuration: NASA CMR Search Endpoint for Collections (Datasets)
    CMR_URL = 'https://cmr.earthdata.nasa.gov/search/collections'
    PAGE_LIMIT = 5 # Fetch first 5 collections for demonstration

    # 2. Define Search Parameters
    params = {
        'page_size': PAGE_LIMIT,
        'pretty': 'true'
    }

    # 3. Define Headers (Request JSON output)
    headers = {
        'Accept': 'application/json' 
    }

    print(f"Fetching {PAGE_LIMIT} collections from NASA CMR...")

    # 4. Execute the GET Request
    try:
        response = requests.get(CMR_URL, params=params, headers=headers)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
        return

    # 5. Process the JSON Response
    data = response.json()
    
    # The actual catalog entries are found within the nested 'feed' and 'entry' keys
    collection_entries = data.get('feed', {}).get('entry', [])
    
    # Report stats from the response headers
    print(f"Total collections found in the database (CMR-Hits): {response.headers.get('CMR-Hits', 'N/A')}")
    print(f"Displaying {len(collection_entries)} sample catalog entries:")
    print("-" * 50)
    
    # 6. Extract and present the key metadata fields
    catalog_data = []
    for entry in collection_entries:
        catalog_data.append({
            'Catalog_Entry_Name': entry.get('dataset_id', 'N/A'),
            'Concept_ID': entry.get('id', 'N/A'),
            'Short_Name': entry.get('short_name', 'N/A'),
            'Metadata_Source_URL': entry.get('location', 'N/A'),
            'Summary_Snippet': entry.get('summary', 'No summary provided')[:100] + '...'
        })

    pprint(catalog_data)
    # Return the extracted catalog data so callers (other modules) can ingest it programmatically.
    return catalog_data

if __name__ == "__main__":
    fetch_nasa_cmr_catalog()