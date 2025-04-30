import requests
import random
from libs.dank_meme_extractor.word_list import SEARCH_TERM_LIST

class TenorClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://tenor.googleapis.com/v2/search"

    @staticmethod
    def get_random_keyword():
        return random.choice(SEARCH_TERM_LIST)
    
    async def get_gif_url(self):
        endpoint = self.base_url
        params = {
            "q": self.get_random_keyword(),
            "key": self.api_key,
            "limit": 50,
            "contentfilter": "high",
            "media_filter": "minimal",
            "locale": "en_US"
        }
        response = requests.get(endpoint, params=params)
        data = response.json() if response.status_code == 200 else None
        gif_list = data['results'] if 'results' in data else None
        if gif_list:
            gif_choice = random.choice(gif_list)
            gif_url = gif_choice['media_formats']['gif']['url'] if 'media_formats' in gif_choice and 'gif' in gif_choice['media_formats'] else None
            return gif_url
        return None
