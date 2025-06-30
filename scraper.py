from GoogleNews import GoogleNews
from datetime import datetime, timedelta
import time
import os
import re
from pymongo import MongoClient
from dotenv import load_dotenv
import schedule
import threading

load_dotenv()

MONGO_URI = os.getenv("MONGO_DB_SRC")
DB_NAME = "AI"
COLLECTION_NAME = "news"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

list_of_topics = [{
    "topic": "Artificial Intelligence",
    "topic_id": "CAAqJAgKIh5DQkFTRUFvSEwyMHZNRzFyZWhJRlpXNHRSMElvQUFQAQ"
}]

def convert_to_epoch_and_time_ago(timestamp):
    try:
        if isinstance(timestamp, datetime):
            dt = timestamp
        else:
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
        
        epoch_time = dt.timestamp()
        
        return round(epoch_time), True
    except Exception as e:
        return None, False

def is_duplicate_article(title, link):
    title_pattern = re.compile(re.escape(title), re.IGNORECASE)
    
    existing_article = collection.find_one({
        "$or": [
            {"title": title_pattern},
            {"link": link}
        ]
    })
    
    return existing_article is not None

def save_to_mongodb(article_data, topic_name):
    title = article_data.get('title', '')
    link = article_data.get('link', '')
    
    if not title or not link:
        return False
    
    if is_duplicate_article(title, link):
        return False
    
    epoch_time, status = convert_to_epoch_and_time_ago(article_data.get('datetime'))
    if not status:
        print(f"Error converting time for article: {title}")
        return False

    document = {
        "title": title,
        "link": link,
        "summary": None,
        "img": article_data.get('img', None),
        "epoch": epoch_time,
        "topic": topic_name,
        "created_at": datetime.utcnow(),
        "priority":"low",
        "status":"pending",
        "send":False
    }
    
    try:
        result = collection.insert_one(document)
        print(f"Saved article: {title}")
        return True
    except Exception as e:
        print(f"Error saving article {title}: {str(e)}")
        return False

def process_news_data(data, topic_name, method_type):
    saved_count = 0
    for i, item in enumerate(data, 1):
        time_info, status = convert_to_epoch_and_time_ago(item.get('datetime'))
        if status:
            if save_to_mongodb(item, topic_name):
                saved_count += 1
            
    print(f"Total articles saved: {saved_count}")

def scrape_news():
    print(f"\n{'='*80}")
    print(f"Starting news scraping at {datetime.now()}")
    print(f"{'='*80}")
    
    googlenews = GoogleNews(lang='en', region='US', period='1h')
    
    for topic_info in list_of_topics:
        topic_name = topic_info["topic"]
        topic_id = topic_info["topic_id"]
        
        try:
            print(f"Processing {topic_name}...")
            googlenews.clear()
            googlenews.set_topic(topic_id)
            googlenews.get_news()
            topic_data = googlenews.results(sort=True)
            process_news_data(topic_data, topic_name, "set_topic")
            
            time.sleep(2)
            
        except Exception as e:
            print(f"Error processing topic {topic_name}: {str(e)}")
    
    print(f"News scraping completed at {datetime.now()}")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    print("Starting News Summary AI with MongoDB integration...")
    
    schedule.every(5).minutes.do(scrape_news)
    
    print("Running initial scrape...")
    scrape_news()
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    print("Scheduler started. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping the application...")
        client.close()

if __name__ == "__main__":
    main()
 