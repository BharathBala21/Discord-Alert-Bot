import discord
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

USER_TOKEN = os.getenv("USER_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
KEYWORDS = os.getenv("KEYWORDS", "hello,wow").split(",")
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID", 0))

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}. Monitoring Channel ID: {TARGET_CHANNEL_ID}')
        channel = self.get_channel(TARGET_CHANNEL_ID)
        if channel:
            print(f"✅ Success: Monitoring channel '#{channel.name}' in '{channel.guild.name}'")
        else:
            print(f"❌ Error: Channel ID {TARGET_CHANNEL_ID} not found in cache.")
            try:
                channel = await self.fetch_channel(TARGET_CHANNEL_ID)
                print(f"✅ Success: Fetched channel '#{channel.name}' in '{channel.guild.name}'")
            except Exception as e:
                print(f"❌ Critical: Could not find channel. Error: {e}")

    async def on_message(self, message):
        if message.channel.id != TARGET_CHANNEL_ID:
            return

        content_lower = message.content.lower()
        matched_keyword = next((kw for kw in KEYWORDS if kw.strip().lower() in content_lower), None)
        
        if matched_keyword:
            print(f"✅ Match found for keyword '{matched_keyword}'! Message from {message.author}: '{message.content[:50]}'")
            await self.send_to_webhook(message, matched_keyword.strip())

    async def send_to_webhook(self, message, matched_keyword):
        guild_id = message.guild.id if message.guild else "@me"
        payload = {
            "content": (
                f"🔔 **Keyword Matched: `{matched_keyword}`**\n"
                f"**User:** {message.author}\n"
                f"**Link:** https://discord.com/channels/{guild_id}/{message.channel.id}/{message.id}\n"
                f">>> {message.content}"
            )
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(WEBHOOK_URL, json=payload) as response:
                if response.status == 204:
                    print(f"Alert sent successfully!")
                else:
                    print(f"Failed to send webhook: {response.status}")

client = MyClient()
client.run(USER_TOKEN)