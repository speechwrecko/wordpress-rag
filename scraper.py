import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import json
import os
import time
import html

class scraper:
    blog_storage_path = "blog_files"
    log_file = "scraper_log.json"

    def __init__(self, wordpress_blog_url, diffbot_token):
        self.blog_url = wordpress_blog_url
        self.token = diffbot_token

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
                
                post_urls.extend([(post['link'], post['slug']) for post in posts])
                page += 1
            else:
                print(f"Error: Unable to retrieve posts. Status code: {response.status_code}")
                break

        return post_urls   


    def extract_text_from_posts(self, post_urls):
        diffbot_url = 'https://api.diffbot.com/v3/analyze'
        path = scraper.blog_storage_path
        log_object = logger()
        isExist = os.path.exists(path)
        
        if not isExist:
            os.makedirs(path)

        for post_url in post_urls:
            if log_object.is_scraped(post_url[1]):
                continue

            params = {
                'url': post_url[0],
                'token': self.token
            }
            headers = {"accept": "application/json"}

            response = requests.get(diffbot_url, headers=headers, params=params)
            response_json = json.loads(response.text)

            try:
                filename = post_url[1] + ".txt"
                text = "TTILE: " + response_json["objects"][0]["title"] + "\n\n" + "POST: " + response_json["objects"][0]["text"]

                file_path = path + "/" + filename
                if not os.path.isfile(file_path):
                    with open(file_path, "w") as file:
                        file.write(text)

                log_object.log_scrape_event(post_url[0], post_url[1])
            except Exception as e:
                print(e)
                log_object.log_scrape_event(post_url[0], post_url[1], "failed")
                pass

            time.sleep(12)




class logger:
    blog_storage_path = "blog_files"
    log_file = "scraper_log.json"
    log_file_path = blog_storage_path + "/" + log_file

    def __init__(self):
        if os.path.isfile(logger.log_file_path):
            return
        else:
            isExist = os.path.exists(logger.blog_storage_path)
            if not isExist:
                os.makedirs(logger.blog_storage_path)
            f = open(logger.log_file_path, "a")
            empty_dict = {'created_on': time.time()}
            f.seek(0)
            json.dump(empty_dict, f)
            f.close()  

    def log_scrape_event(self, url, slug, result="success"):
        scrape_event = {"url": url, "timestamp": time.time()}
        
        if os.path.isfile(logger.log_file_path):
            with open(logger.log_file_path, "r+") as file:
                log_data = json.load(file)
                if slug in log_data:
                    return
                else:
                    log_data[slug] = scrape_event
                file.seek(0)
                json.dump(log_data, file)

    def update_scrape_event(self, slug, data):
        if os.path.isfile(logger.log_file_path):
            with open(logger.log_file_path, "r+") as file:
                log_data = json.load(file)
                if slug in log_data:
                    for key, value in data.items():
                        log_data[slug][key] = value
                    file.seek(0)
                    json.dump(log_data, file)
                    return
                else:
                    return "scrape event doesn't exist"

        else:
            return "no log file"
        
    def is_scraped(self, slug):
        if os.path.isfile(logger.log_file_path):
            with open(logger.log_file_path, "r") as file:
                log_data = json.load(file)
            if slug in log_data:
                return True
        return False
    
    def is_all_inserted(self):
        if os.path.isfile(logger.log_file_path):
            with open(logger.log_file_path, "r") as file:
                log_data = json.load(file)
            for key in log_data:
                if key != "created_on" and key != "125-2":
                    try:
                        is_inserted = log_data[key].get("db_is_inserted", False)
                        if is_inserted == False:
                            return False
                    except:
                        return False
            return True
        return False

