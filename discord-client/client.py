import discord
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from dank_meme_extractor.tenor_client import TenorClient

class DiscordClient(discord.Client):
    def __init__(self, token, giphy_token):
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True

        super().__init__(intents=intents)
        self.token = token
        self.giphy_client = TenorClient(giphy_token)

    async def post_message(self, channel_id, message, logger):
        channel = await self.fetch_channel(channel_id)
        await channel.send(message)
        logger.info(f'message \'{message}\' has been successfully rendered...')
    
    async def send_gif(self, channel_id, logger):
        gif_url = await self.giphy_client.get_gif_url()
        channel = await self.fetch_channel(channel_id)
        if gif_url:
            logger.info(f'Media GIF {gif_url} has been successfully rendered...')
            await channel.send(gif_url)
        else:
            logger.error("Failed to get GIF URL...")
            await channel.send(":ggohda:")

    def run_bot(self, logger):
        logger.info("Starting to bootstrap the bot in the discord client...")
        self.run(self.token)
