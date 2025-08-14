import os
import subprocess
import re
from datetime import date, datetime, timedelta

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Load environment variables from .env file
load_dotenv()


# Selenium Setup
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    return webdriver.Chrome(options=chrome_options)


def get_fact_for_date(target_date):
    slsc_url = f"https://www.slsc.org/astronomy-fact-of-the-day-{target_date}/"

    driver = get_driver()
    driver.get(slsc_url)
    driver.implicitly_wait(10)
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    try:
        elements = soup.find("div", class_="entry").find_all("p")[:-1]
        raw_fact = "\n".join(str(p) for p in elements)
        raw_img_match = re.search(r'src="(.*?)"', raw_fact)
        raw_img = raw_img_match.group(1)
        parsed_fact = re.sub(r'<img[^>]*src="[^"]*"[^>]*>', rf'<img src="{raw_img}" alt=""/>', raw_fact)
        return parsed_fact, slsc_url
    except AttributeError:
        return None, slsc_url


# NASA API endpoint
nasa_url = "https://api.nasa.gov/planetary/apod"
params = {"api_key": os.getenv("NASA_API_KEY")}
response = requests.get(nasa_url, params=params)
if response.status_code != 200:
    exit(f"Error: {response.status_code}")

data = response.json()
title = data.get("title", "Astronomy Picture of the Day")
date_raw = data.get("date", str(date.today()))
credit = data.get("copyright", "NASA")
story = data.get("explanation", "Explanation not provided")
url = data.get("url", "Image URL not provided")
hdurl = data.get("hdurl", "HD Image URL not provided")

# Format date
date_object = datetime.strptime(date_raw, "%Y-%m-%d")
date_str = date_object.strftime("%B %#d, %Y")
slsc_date = date_object.strftime("%B-%#d-%Y").lower()

# Try to get fact for today, if not available try previous days
offset = 0
fact, source = None, None

while not fact:
    previous_date = date_object - timedelta(days=offset)
    slsc_date = previous_date.strftime("%B-%#d-%Y").lower()
    fact, source = get_fact_for_date(slsc_date)
    if fact: break
    else: offset += 1

offset_text = f"({offset} day{'s' if offset > 1 else ''} offset since no new article has been published yet)" if offset > 0 else ""

with open('readmeTemplate.md', 'r', encoding='utf-8') as file:
    markdown_content = file.read()

# Replace placeholders with variable values
markdown_content = markdown_content.replace('{{ title }}', title)
markdown_content = markdown_content.replace('{{ date }}', date_str)
markdown_content = markdown_content.replace('{{ credit }}', credit)
markdown_content = markdown_content.replace('{{ story }}', story)
markdown_content = markdown_content.replace('{{ url }}', url)
markdown_content = markdown_content.replace('{{ hdurl }}', hdurl)
markdown_content = markdown_content.replace('{{ fact }}', fact)
markdown_content = markdown_content.replace('{{ source }}', source)
markdown_content = markdown_content.replace('{{ offset }}', offset_text)

with open('README.md', 'w', encoding='utf-8') as file:
    file.write(markdown_content)

# Push to GitHub
subprocess.run(["git", "add", "README.md"], check=True)
subprocess.run(["git", "commit", "--allow-empty", "-m", "Auto-commit: Astronomy Picture of the Day"], check=True)
subprocess.run(["git", "push"], check=True)
