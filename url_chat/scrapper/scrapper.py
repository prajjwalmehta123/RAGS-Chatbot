import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

class WebCrawler:
    def __init__(self):
        self.visited_urls = set()

    def get_all_links(self, url, base_domain):
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            full_link = urljoin(url, link)
            link_domain = urlparse(full_link).netloc
            if link_domain == base_domain and full_link not in self.visited_urls:
                links.append(full_link)
        return links

    def save_page_content(self, url, folder_path):
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(separator=' ', strip=True)
        parsed_url = urlparse(url)
        file_name = parsed_url.path.strip('/').replace('/', '_') or 'home'
        file_path = os.path.join(folder_path, f"{file_name}.txt")

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(page_text)
            print(f"Saved content from {url} to {file_path}")
        except Exception as e:
            print(f"Failed to save content from {url}: {e}")

    def crawl_website(self, url):
        base_domain = urlparse(url).netloc
        folder_path = os.path.join(os.getcwd(), base_domain)
        os.makedirs(folder_path, exist_ok=True)

        def recursive_crawl(current_url):
            if current_url in self.visited_urls:
                return
            self.visited_urls.add(current_url)
            links = self.get_all_links(current_url, base_domain)
            self.save_page_content(current_url, folder_path)

            for link in links:
                if link not in self.visited_urls:
                    recursive_crawl(link)

        recursive_crawl(url)
        return folder_path