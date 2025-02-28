import os
import subprocess
import re
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# Load environment variables from .env file
load_dotenv()

# Selenium Setup
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

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
date = date_object.strftime("%B %d, %Y")

# Selenium-powered Fact Scraper
slsc_date = date_object.strftime("%B-%d-%Y").lower()
slsc_url = f"https://www.slsc.org/astronomy-fact-of-the-day-{slsc_date}/"
driver.get(slsc_url)
driver.implicitly_wait(10)
html = driver.page_source
driver.quit()
soup = BeautifulSoup(html, "html.parser")
elements = soup.find("div", class_="entry").find_all("p")[:-1]
raw_fact = "\n".join(str(p) for p in elements)
raw_img = re.search(r'src="(.*?)"', raw_fact).group(1)
fact = re.sub(r'<img[^>]*src="[^"]*"[^>]*>', rf'<img src="{raw_img}" alt=""/>', raw_fact)

with open('readmeTemplate.md', 'r', encoding='utf-8') as file:
    markdown_content = file.read()

# Replace placeholders with variable values
markdown_content = markdown_content.replace('{{ title }}', title)
markdown_content = markdown_content.replace('{{ date }}', date)
markdown_content = markdown_content.replace('{{ credit }}', credit)
markdown_content = markdown_content.replace('{{ story }}', story)
markdown_content = markdown_content.replace('{{ url }}', url)
markdown_content = markdown_content.replace('{{ hdurl }}', hdurl)
markdown_content = markdown_content.replace('{{ fact }}', fact)
markdown_content = markdown_content.replace('{{ source }}', slsc_url)

with open('README.md', 'w', encoding='utf-8') as file:
    file.write(markdown_content)

# Push to GitHub
subprocess.run(["git", "add", "README.md"], check=True)
subprocess.run(["git", "commit", "-m", "Auto-commit: Astronomy Picture of the Day"], check=True)
subprocess.run(["git", "push"], check=True)
