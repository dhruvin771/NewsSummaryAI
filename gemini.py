import google.generativeai as genai
import dotenv
import os
import json
from pymongo import MongoClient
from prompts import system_prompt
from googlenewsdecoder import gnewsdecoder
import schedule
import time
import threading
import discord
import aiohttp

dotenv.load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MONGO_URI = os.getenv("MONGO_DB_SRC")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


DB_NAME = "AI"
COLLECTION_NAME = "news"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        generation_config={"response_mime_type": "application/json"},
        system_instruction=system_prompt
    )

async def send_webhook_message(title, summary, img_url, priority):
    if priority == "high":
        color = 0xFF0000  
    elif priority == "medium":
        color = 0xFFA500  
    else:
        color = 0x00FF00  
        
    embed = discord.Embed(
        title=title if title else "News Summary",
        color=color,
        description=summary if summary else "No summary available."
    )
    if img_url:
        embed.set_image(url=img_url)
    
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(DISCORD_WEBHOOK_URL, session=session)
        await webhook.send(
            embed=embed,
            username="lisu",
            avatar_url="https://www.thestatesman.com/wp-content/uploads/2025/05/blackpink-lisa-k-pop-lisa-documentary-jpg.webp"
        )
    print("Message sent successfully!")

def process_pending_article():
    doc = collection.find_one({"status": "pending"})
    if not doc:
        print("No pending articles found.")
        return

    link = doc.get("link")
    if not link:
        print("No link found in the document.")
        return

    try:
        decoded = gnewsdecoder(link, interval=2)
        if decoded.get("status"):
            url_to_summarize = decoded["decoded_url"]
            print("Decoded URL:", url_to_summarize)
        else:
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"status": "completed", "summary": True, "priority": None}}
            )
            print(f"Decoding failed. Updated document {doc['_id']} as completed with summary=True.")
            return
    except Exception as e:
        print(f"Error decoding link: {e}")
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"status": "completed", "summary": True, "priority": None}}
        )
        print(f"Exception during decoding. Updated document {doc['_id']} as completed with summary=True.")
        return

    response = model.generate_content(url_to_summarize)
    try:
        data = json.loads(response.text)
    except Exception:
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"status": "completed", "summary": True, "priority": None}}
        )
        return
    print(data)

    if data.get("status"):
      update_fields = {
          "status": "completed",
          "send":True,
          "summary": data.get("summary"),
          "priority": data.get("priority")
      }
      collection.update_one({"_id": doc["_id"]}, {"$set": update_fields})
      title = data.get("title") or doc.get("title")
      summary = data.get("summary")
      img_url = doc.get("img")
      priority = data.get("priority")

      import asyncio
      asyncio.run(send_webhook_message(title, summary, img_url, priority))
      print(f"Updated document {doc['_id']} with summary and priority.")
    else:
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"status": "completed", "summary": True, "priority": None}}
        )
        return

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    schedule.every(1).minutes.do(process_pending_article)
    print("Scheduler started. Press Ctrl+C to stop.")
    process_pending_article()
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping the application...")