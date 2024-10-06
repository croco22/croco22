import os
import subprocess
from datetime import datetime

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv("NASA_API_KEY")

# API endpoint
api_url = "https://api.nasa.gov/planetary/apod"
params = {"api_key": api_key}
response = requests.get(api_url, params=params)

if response.status_code == 200:
    data = response.json()
    title = data.get("title", "Title not found")
    date_raw = data.get("date", "Date not found")
    authors = data.get("copyright", "Copyright not found")
    text = data.get("explanation", "Explanation not found")
    url = data.get("url", "Image URL not found")
    hdurl = data.get("hdurl", "HD Image URL not found")

    # Format date
    date_object = datetime.strptime(date_raw, "%Y-%m-%d")
    date = date_object.strftime("%d %B %Y")

    with open('readmeTemplate.md', 'r', encoding='utf-8') as file:
        markdown_content = file.read()

    # Replace placeholders with variable values
    markdown_content = markdown_content.replace('{{ title }}', title)
    markdown_content = markdown_content.replace('{{ date }}', date)
    markdown_content = markdown_content.replace('{{ authors }}', authors)
    markdown_content = markdown_content.replace('{{ text }}', text)
    markdown_content = markdown_content.replace('{{ url }}', url)
    markdown_content = markdown_content.replace('{{ hdurl }}', hdurl)

    with open('README.md', 'w', encoding='utf-8') as file:
        file.write(markdown_content)
else:
    exit(f"Error: {response.status_code}")

# Push to GitHub
subprocess.run(["git", "add", "README.md"], check=True)
subprocess.run(["git", "commit", "-m", "Auto-commit: Astronomy Picture of the Day"], check=True)
subprocess.run(["git", "push"], check=True)
