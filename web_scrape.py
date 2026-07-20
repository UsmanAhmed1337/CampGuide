import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse

base_url = 'https://www.atomcamp.com/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

all_data = []

def get_internal_links(url, domain):
    internal_links = set()
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for a_tag in soup.find_all('a', href=True):
                link = a_tag['href']
                if domain in link or link.startswith('/'):
                    full_link = urljoin(url, link)
                    internal_links.add(full_link)
        else:
            print(f"Failed to retrieve the page {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error occurred while fetching {url}: {e}")
    
    return internal_links

def scrape_page(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else 'No Title'
            text = soup.get_text(separator=' ', strip=True)
            data = {
                "title": title,
                "url": url,
                "text": text
            }
            all_data.append(data)
        else:
            print(f"Failed to retrieve the page {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error occurred while scraping {url}: {e}")

to_crawl = {base_url}
crawled = set()
domain = urlparse(base_url).netloc

while to_crawl:
    current_url = to_crawl.pop()
    
    if current_url not in crawled:
        print(f"Scraping: {current_url}")
        scrape_page(current_url)
        crawled.add(current_url)
        internal_links = get_internal_links(current_url, domain)
        to_crawl.update(internal_links)
        time.sleep(1)

with open('scraped_data.json', 'w', encoding='utf-8') as file:
    json.dump(all_data, file, ensure_ascii=False, indent=4)

print("Data has been successfully saved to 'scraped_data.json'.")
