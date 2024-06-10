import requests
from bs4 import BeautifulSoup
import json
# from datetime import datetime
from datetime import datetime, timezone
import math
import os
import csv

def get_html_with_requests(url):
    headers = {
        'User-Agent': 'Your User-Agent String Here',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    response = requests.get(url, headers=headers)
    return response.text if response.status_code == 200 else None

def convert_data_to_json(script_tags_with_keyword):
    for script_tag in script_tags_with_keyword:
        script_tag = script_tag.replace('window.__myx = ', '')
        data = json.loads(script_tag)
    return data

def find_reviews_data(json_data):
    return [json_data['reviewsData']['reviews']]

def find_script_tags_with_keyword(html_data):
    soup = BeautifulSoup(html_data, 'html.parser')
    script_tags = soup.find_all('script')
    return [script_tag.string for script_tag in script_tags if script_tag.string and 'window.__myx = ' in script_tag.string]

def get_html_data(url, page_number):
    url = url + f"?page={page_number}"
    return get_html_with_requests(url)

def get_review_data(json_data):
    reviews_data = find_reviews_data(json_data)
    if reviews_data:
        review_modify_array = [{
            'author': k['userName'],
            'rating': k['userRating'],
            'content': k['review'],
            'images': ';'.join(image['url'] for image in k['images']),
            'videos': '',
            'title': '',
            # 'created_at': datetime.utcfromtimestamp(int(k['updatedAt']) / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            'created_at': datetime.fromtimestamp(int(k['updatedAt']) / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
            'verified_purchase': k['status']
        } for i in reviews_data for k in i]

        file_exists = os.path.exists('myntra.csv')
        
        with open('myntra.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['author', 'rating', 'content', 'images', 'videos', 'title', 'created_at', 'verified_purchase'])
            if not file_exists or os.stat('myntra.csv').st_size == 0:
                writer.writeheader()
            writer.writerows(review_modify_array)

        print("Reviews data saved to myntra.csv")
    else:
        print("No 'reviewsData' object found in script tags.")

def process_page(url, page_number):
    html_data = get_html_data(url, page_number)
    if html_data:
        script_tags_with_keyword = find_script_tags_with_keyword(html_data)
        if script_tags_with_keyword:
            json_data = convert_data_to_json(script_tags_with_keyword)
            get_review_data(json_data)
        else:
            print("No script tags found with keyword 'window.__myx'.")
    else:
        print("Failed to retrieve HTML data.")

url = 'https://www.myntra.com/reviews/25260156'
html_data = get_html_data(url, 1)
if html_data:
    script_tags_with_keyword = find_script_tags_with_keyword(html_data)
    if script_tags_with_keyword:
        json_data = convert_data_to_json(script_tags_with_keyword)
        reviews_count =  json_data['pdpData']['ratings']['reviewInfo']['reviewsCount']
        total_pages = math.ceil(int(reviews_count) / 7)
        for i in range(3):
            process_page(url, i + 1)
    else:
        print("No script tags found with keyword 'window.__myx'.")
else:
    print("Failed to retrieve HTML data.")