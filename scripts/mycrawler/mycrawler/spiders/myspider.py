import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
import pymysql
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class MySpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://yourwebsite.com']

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f'pages/{page}.html'

        # Extract data (example: title and clicks)
        soup = BeautifulSoup(response.body, 'html.parser')
        title = soup.title.string
        clicks = int(soup.find('span', class_='click-count').text)

        # Save to database
        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        with connection.cursor() as cursor:
            sql = "INSERT INTO scraped_data (url, title, clicks) VALUES (%s, %s, %s)"
            cursor.execute(sql, (response.url, title, clicks))
        connection.commit()
        connection.close()

        # Follow links to other pages
        for next_page in response.css('a::attr(href)').getall():
            if next_page is not None:
                yield response.follow(next_page, self.parse)

# Run the spider
process = CrawlerProcess()
process.crawl(MySpider)
process.start()
