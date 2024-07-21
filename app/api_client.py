import requests
from config import Config

class ApiClient:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def _get_headers(self):
        return {
            'x-api-key': f'{self.api_key}'
        }
    
    def get(self, url, **kwargs):
        kwargs.setdefault('headers', self._get_headers())
        response = requests.get(url, **kwargs)
        self._handle_error(response)
        return response
    
    def post(self, url, **kwargs):
        kwargs.setdefault('headers', self._get_headers())
        response = requests.post(url, **kwargs)
        self._handle_error(response)
        return response
    
    def put(self, url, **kwargs):
        kwargs.setdefault('headers', self._get_headers())
        response = requests.put(url, **kwargs)
        self._handle_error(response)
        return response
    
    def delete(self, url, **kwargs):
        kwargs.setdefault('headers', self._get_headers())
        response = requests.delete(url, **kwargs)
        self._handle_error(response)
        return response

    def _handle_error(self, response):
        if response.status_code not in (200, 201, 204):
            print(f"Error: {response.status_code} - {response.text}")


api_client = ApiClient(Config.API_KEY_BACKEND)
