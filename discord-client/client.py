import discord
import os
import random
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from libs.dank_meme_extractor.tenor_client import TenorClient
from libs.llm_integrator.llm_client import LLMClient

class DiscordClient(discord.Client):
    def __init__(self, token, giphy_token, hf_token):
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True

        super().__init__(intents=intents)
        self.token = token
        self.giphy_client = TenorClient(giphy_token)
        self.llm_client = LLMClient(hf_token)

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
    
    async def mention_with_llm_response(self, channel_id, member_list, logger):
        try:
            channel = await self.fetch_channel(channel_id)
            member_id = self.get_random_member(member_list)
            member = await channel.guild.fetch_member(member_id)

            mention = member.mention
            logger.info(f"Mention resolved: {mention}")

            quote = await self.llm_client.generate_quote(logger=logger)
            message = f"{mention} {quote}"

            await channel.send(message)
            logger.info("Message with mention and quote sent.")
        except Exception as e:
            logger.error(f"Error while mentioning member and sending quote: {e}")


    def get_random_member(self, member_list):
        return random.choice(member_list.split('|'))