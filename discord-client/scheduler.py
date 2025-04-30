import asyncio
from client import DiscordClient

class Scheduler:
    def __init__(self, client: DiscordClient):
        self.client = client

    async def schedule_message(self, channel_id, message, delay, logger):
        while True:
            await self.client.post_message(channel_id, message, logger)
            await asyncio.sleep(delay)

    async def schedule_gif(self, channel_id, delay, logger):
        while True:
            await self.client.send_gif(channel_id, logger)
            await asyncio.sleep(delay)
            
    async def schedule_mention(self, channel_id, delay, member_list, logger):
        while True:
            await self.client.mention_with_llm_response(channel_id, member_list, logger)
            await asyncio.sleep(delay)