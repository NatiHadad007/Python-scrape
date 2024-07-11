import cloudscraper
from bs4 import BeautifulSoup
import time
import random
import json
from urllib.parse import urlparse
import requests

proxy_api = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'


user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
    # Add more user agents here
]

def get_proxies():
    try:
        response = requests.get(proxy_api)
        if response.status_code == 200:
            proxies = response.text.splitlines()
            return proxies
        else:
            print("Failed to fetch proxies")
            return []
    except Exception as e:
        print(f"An error occurred while fetching proxies. Error: {str(e)}")
        return []

def fetch_html_content(url, proxies):
    for proxy in proxies:
        user_agent = random.choice(user_agents)
        scraper = cloudscraper.create_scraper(
            interpreter="nodejs",
            browser={
                "browser": "chrome",
                "platform": "ios",
                "desktop": False,
            },
            captcha={
                "provider": "2captcha",
                "api_key": "b391465958df1b64dbc88cb2d68ecefd",
            }
        )

        headers = {
            "User-Agent": user_agent
        }

        try:
            response = scraper.get(url, proxies={"https": proxy}, headers=headers)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            # time.sleep(random.randint(5, 10))
            print(f"Failed to scrape using: {proxy}")
    return None

def extract_domain_prices(html_content):
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        plan_name = soup.find_all('a', class_="sb link sb star-rating-root link")
        hrefs = [
            f"https://www.capterra.com{a.get('href').replace('reviews', 'pricing')}"
            for a in plan_name if a.get('href')
        ]
        return hrefs
    except Exception as e:
        print(f"An error occurred while extracting hrefs. Error: {str(e)}")
        return []

def extract_brand_name(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')
    if len(path_parts) > 3:
        return path_parts[3]  # Extracting the brand name part from the URL
    return None

def fetching_plans_and_pricing(urls):
    proxies = get_proxies()
    all_data = []
    for url in urls:
        html_content = fetch_html_content(url, proxies)
        if html_content:
            try:
                soup = BeautifulSoup(html_content, "html.parser")
                brand = extract_brand_name(url)
                plans = soup.find_all('h3', class_="leading-lg")
                prices = soup.find_all('div', class_="leading-2xl mb-xs text-2xl font-semibold")
                for plan, price in zip(plans, prices):
                    data = {
                        "brand": brand,
                        "plan": plan.text,
                        "price": price.text
                    }
                    print(data)
                    all_data.append(data)
                    save_data_to_json(all_data)
            except Exception as e:
                print(f"An error occurred while processing URL: {url}. Error: {str(e)}")
            time.sleep(random.randint(5, 10))

def save_data_to_json(data, filename="data.json"):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        print(f"Data saved: {data}")
    except Exception as e:
        print(f"An error occurred while saving data to JSON. Error: {str(e)}")

if __name__ == "__main__":
    url = "https://www.capterra.com/ecommerce-software/"
    proxies = get_proxies()
    html_content = fetch_html_content(url, proxies)

    if html_content:
        print("HTML content fetched successfully")
        hrefs = extract_domain_prices(html_content)
        if hrefs:
            print("Extracted domain prices URLs successfully")
            fetching_plans_and_pricing(hrefs)
        else:
            print("No domain prices URLs found")
    else:
        print("Failed to retrieve HTML content. Please check your internet connection or try again later.")
