import requests
from bs4 import BeautifulSoup
import pandas as pd
import pymysql
from dotenv import load_dotenv
import os
import schedule
import time

# Load environment variables from .env file
load_dotenv()

# Define a function to scrape a single page
def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Example: Scrape data
    data = {
        'url': url,
        'title': soup.title.string,
        'clicks': int(soup.find('span', class_='click-count').text)
    }
    return data

# Define a function to scrape the entire website
def scrape_website():
    # List of URLs to scrape (You can expand this list)
    urls = [
        'https://yourwebsite.com/page1',
        'https://yourwebsite.com/page2',
        # Add more URLs as needed
    ]
    
    data_list = []
    for url in urls:
        data = scrape_page(url)
        data_list.append(data)
    
    # Convert to DataFrame
    df = pd.DataFrame(data_list)
    
    # Database connection
    connection = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    
    # Save data to database
    with connection.cursor() as cursor:
        for _, row in df.iterrows():
            sql = "INSERT INTO scraped_data (url, title, clicks) VALUES (%s, %s, %s)"
            cursor.execute(sql, (row['url'], row['title'], row['clicks']))
        connection.commit()
    
    connection.close()

# Schedule the scraper to run weekly
schedule.every().week.do(scrape_website)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
