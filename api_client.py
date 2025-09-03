import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ApiClient:
    def __init__(self, base_url, api_key, timeout=30):
        self.base_url = base_url
        self.api_key = api_key  # Store key for services that need it in the request body (e.g., SMM-X)
        self.session = self._create_session()
        self.timeout = timeout
        # For APIs that use header-based auth. This is a common practice.
        self.session.headers['X-API-KEY'] = api_key

    def _create_session(self):
        session = requests.Session()
        # Configure retry logic for robust connections
        retries = Retry(total=5,
                        backoff_factor=0.5,
                        status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"GET request to {url} failed: {e}")
            return None
        except ValueError:  # Catches JSON decoding errors
            logging.error(f"Failed to decode JSON from {url}")
            return None

    def post(self, endpoint, json_data=None):
        """Sends a POST request with JSON data."""
        url = f"{self.base_url}{endpoint}"
        try:
            # Use `json` parameter for automatic JSON encoding and header
            response = self.session.post(url, json=json_data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"POST request to {url} failed: {e}")
            return None
        except ValueError:  # Catches JSON decoding errors
            logging.error(f"Failed to decode JSON from {url}")
            return None
