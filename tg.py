import discord
import asyncio
import aiohttp
import dotenv
import os

dotenv.load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

async def send_webhook_message():
    embed = discord.Embed(
        title="Discord Bot Message",
        color=0x00ff00,
        description="Simple Discord bot for sending messages."
    )
    
    embed.add_field(name="Features", value="• Send formatted messages\n• Use webhooks for posting", inline=False)
    embed.add_field(name="Status", value="> Bot is now active and ready to use!", inline=False)
    
    embed.set_image(url="https://www.thestatesman.com/wp-content/uploads/2025/05/blackpink-lisa-k-pop-lisa-documentary-jpg.webp")
    
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(DISCORD_WEBHOOK_URL, session=session)
        await webhook.send(
            embed=embed,
            username="lisu",
            avatar_url="https://www.thestatesman.com/wp-content/uploads/2025/05/blackpink-lisa-k-pop-lisa-documentary-jpg.webp"
        )
    
    print("Message sent successfully!")

async def send_multiple_messages():
    count = 5  # Change this number for how many messages you want
    for i in range(count):
        await send_webhook_message()
        await asyncio.sleep(1)  # Wait 1 second between messages
        print(f"Sent message {i+1}")

asyncio.run(send_multiple_messages())