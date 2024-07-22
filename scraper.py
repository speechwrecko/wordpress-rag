import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import json
import os
import time

class scraper:

    def __init__(self, wordpress_blog_url):
        self.blog_url = wordpress_blog_url

    def get_wordpress_posts(self, per_page=100):
        """
        Retrieve all blog post URLs from a WordPress site using the REST API.
        
        :param base_url: The base URL of the WordPress site (e.g., 'https://example.com')
        :param per_page: Number of posts to retrieve per request (default: 100, max: 100)
        :return: A list of blog post URLs
        """
        api_url = f"{self.blog_url.rstrip('/')}/wp-json/wp/v2/posts"
        post_urls = []
        page = 1

        while True:
            params = {
                'page': page,
                'per_page': per_page,
                'fields': 'link'  # We only need the URL, so we request only the 'link' field
            }

            response = requests.get(api_url, params=params)

            if response.status_code == 200:
                posts = json.loads(response.text)
                
                if not posts:
                    break  # No more posts to retrieve
                
                post_urls.extend([post['link'] for post in posts])
                page += 1
            else:
                print(f"Error: Unable to retrieve posts. Status code: {response.status_code}")
                break

        return post_urls
    
    def extract_text_from_posts(self, post_urls):
        diffbot_url = 'https://api.diffbot.com/v3/analyze'
        path = "blog_files"
        isExist = os.path.exists(path)
        
        if not isExist:
            os.makedirs(path)

        for post_url in post_urls:
            params = {
                'url': post_url,
                'token': 'aa898574824e82c46365a90ef03fe08c'
            }
            headers = {"accept": "application/json"}

            response = requests.get(diffbot_url, headers=headers, params=params)
            response_json = json.loads(response.text)

            try:
                text = "TTILE: " + response_json["objects"][0]["title"] + "\n\n" + "POST: " + response_json["objects"][0]["text"]
                filename = (response_json["objects"][0]["title"]).replace(" ", "_") + ".txt"

                file_path = path + "/" + filename
                if not os.path.isfile(file_path):
                    with open(file_path, "w") as file:
                        file.write(text)
            except:
                pass

            time.sleep(12)

