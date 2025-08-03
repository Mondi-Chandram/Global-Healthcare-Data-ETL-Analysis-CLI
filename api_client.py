import requests
import logging

class APIClient:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.api_key = api_key

    def fetch_data(self, params=None, endpoint=""):
        headers = {'X-Api-Key': self.api_key} if self.api_key else {}

        url = f"{self.base_url}"
        if endpoint:
            url += f"/{endpoint}"

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            return []
        