from GoogleNews import GoogleNews
from datetime import datetime
import time

list_of_topics = [{
    "topic": "Artificial Intelligence",
    "topic_id": "CAAqKggKIiRDQkFTRlFvSUwyMHZNRGRqTVhZU0JXVnVMVWRDR2dKSlRpZ0FQAQ"
},
{
    "topic": "Computing",
    "topic_id": "CAAqJQgKIh9DQkFTRVFvSUwyMHZNREZzY0hNU0JXVnVMVWRDS0FBUAE"
},
{
    "topic": "OpenAI",
    "topic_id": "CAAqLAgKIiZDQkFTRmdvTkwyY3ZNVEZpZUdNMk5UWjJOaElGWlc0dFIwSW9BQVAB"
},
{
    "topic": "Physics",
    "topic_id": "CAAqJQgKIh9DQkFTRVFvSUwyMHZNRFZ4YW5RU0JXVnVMVWRDS0FBUAE"
},
{
    "topic": "Machine Learning",
    "topic_id": "CAAqJggKIiBDQkFTRWdvSkwyMHZNREZvZVdoZkVnVmxiaTFIUWlnQVAB"
},
{
    "topic": "Deep Learning",
    "topic_id": "CAAqKAgKIiJDQkFTRXdvS0wyMHZNR2d4Wm00NGFCSUZaVzR0UjBJb0FBUAE"
},
{
    "topic": "Science",
    "topic_id": "CAAqKggKIiRDQkFTRlFvSUwyMHZNRFp0Y1RjU0JXVnVMVWRDR2dKSlRpZ0FQAQ"
},
{
    "topic": "World",
    "topic_id": "CAAqKggKIiRDQkFTRlFvSUwyMHZNRGx1YlY4U0JXVnVMVWRDR2dKSlRpZ0FQAQ"
},
{
    "topic": "Internet",
    "topic_id": "CAAqKggKIiRDQkFTRlFvSUwyMHZNRGRqTVhZU0JXVnVMVWRDR2dKSlRpZ0FQAQ"
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

def process_news_data(data, topic_name, method_type):
    print(f"\n{'='*60}")
    print(f"TOPIC: {topic_name} ({method_type})")
    print(f"{'='*60}")
    
    for i, item in enumerate(data, 1):
        print(f"Article {i}:")
        print(f"Title: {item.get('title', 'N/A')}")
        print(f"Media: {item.get('media', 'N/A')}")
        print(f"Link: {item.get('link', 'N/A')}")
        print(f"Image: {item.get('img', 'N/A')}")
        
        time_info, status = convert_to_epoch_and_time_ago(item.get('datetime'))
        if status:
            print(f"Time info: {time_info}")
        else:
            print(f"Error: {item.get('datetime', 'N/A')}")
        
        print("-" * 50)

# Initialize GoogleNews
googlenews = GoogleNews(lang='en', region='US', period='1d')

for topic_info in list_of_topics:
    topic_name = topic_info["topic"]
    topic_id = topic_info["topic_id"]
    
    # Method 1: Using set_topic
    print(f"Processing {topic_name} with set_topic...")
    googlenews.clear()
    googlenews.set_topic(topic_id)
    topic_data = googlenews.results(sort=True)
    process_news_data(topic_data, topic_name, "set_topic")
    
    # Wait 2 seconds
    time.sleep(2)
    
    # Method 2: Using get_news
    print(f"Processing {topic_name} with get_news...")
    googlenews.clear()
    googlenews.get_news(topic_name)
    news_data = googlenews.results(sort=True)
    process_news_data(news_data, topic_name, "get_news")
    
    # Wait 2 seconds before next topic
    time.sleep(2)