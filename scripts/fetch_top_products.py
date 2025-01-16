from woocommerce import API
import pandas as pd
import pymysql
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

wcapi = API(
    url=os.getenv('WOOCOMMERCE_URL'),
    consumer_key=os.getenv('WOOCOMMERCE_CONSUMER_KEY'),
    consumer_secret=os.getenv('WOOCOMMERCE_CONSUMER_SECRET'),
    version="wc/v3"
)

# Fetch all products with additional data from WooCommerce API
products = wcapi.get("products", params={"include": ["total_sales", "average_rating", "review_count", "meta_data"]}).json()

# Process and store product data
product_list = []
for product in products:
    clicks = next((item['value'] for item in product['meta_data'] if item['key'] == 'clicks'), 0)
    product_list.append({
        'name': product['name'],
        'price': product['price'],
        'reviews': product['review_count'],
        'rating': float(product['average_rating']),
        'sales': product['total_sales'],
        'clicks': int(clicks),
        'category': product['categories'][0]['name']
    })

# Convert to DataFrame
df = pd.DataFrame(product_list)

# Define weights for composite popularity score
weights = {
    'sales': 0.5,
    'reviews': 0.2,
    'rating': 0.2,
    'clicks': 0.1
}

# Calculate composite popularity score
df['popularity'] = (
    df['sales'] * weights['sales'] +
    df['reviews'] * weights['reviews'] +
    df['rating'] * weights['rating'] +
    df['clicks'] * weights['clicks']
)

# Filter top 5 products by category
top_products = df.groupby('category').apply(lambda x: x.nlargest(5, 'popularity'))

# Database connection
connection = pymysql.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

# Save top products to database
with connection.cursor() as cursor:
    for _, row in top_products.iterrows():
        sql = "INSERT INTO top_products (name, price, reviews, rating, sales, clicks, category, popularity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (row['name'], row['price'], row['reviews'], row['rating'], row['sales'], row['clicks'], row['category'], row['popularity']))
    connection.commit()

connection.close()
