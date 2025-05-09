import discord
import os
import random
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from libs.dank_meme_extractor.tenor_client import TenorClient
from libs.llm_integrator.llm_client import LLMClient
from libs.reddit_threads.reddit_client import RedditVNTLFetcher

class DiscordClient(discord.Client):
    def __init__(self, token, giphy_token, hf_token, reddit_client_id, reddit_client_secret, logger=None):
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True

        super().__init__(intents=intents)
        self.token = token
        self.giphy_client = TenorClient(giphy_token)
        self.llm_client = LLMClient(hf_token)
        self.MAX_MESSAGE_CHUNK_SIZE_LIMIT = 2000

        self.reddit_client = RedditVNTLFetcher(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret
        )

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
        
    async def send_message_in_chunks(self, channel_id, message, logger):
        if len(message) > self.MAX_MESSAGE_CHUNK_SIZE_LIMIT:
            logger.warning("Message too long, splitting into chunks.")
            chunks = [message[idx: idx + self.MAX_MESSAGE_CHUNK_SIZE_LIMIT] for idx in range(0, len(message), self.MAX_MESSAGE_CHUNK_SIZE_LIMIT)]
            for chunk_idx, chunk in enumerate(chunks):
                await self.post_message(channel_id, chunk, logger)
                logger.info(f"Sent chunk no°{chunk_idx} according to the strategy of chunking sizes.")
        else:
            await self.post_message(channel_id, message, logger)
            logger.info("Successfully sended the whole message.")

    async def dispatch_vn_tl_updates_daily(self, target_channel_id, logger):
        try:
            logger.info("Fetching the latest VNTS post from Reddit...")
            latest_vn_tl_updates_post = self.reddit_client.fetch_latest_vnts_post()

            if latest_vn_tl_updates_post:
                latest_vn_tl_updates_message = self.reddit_client.fetch_post_content(latest_vn_tl_updates_post)
                
                if latest_vn_tl_updates_message:
                    latest_vn_tl_updates_message_with_ping = f"@everyone @here\n{latest_vn_tl_updates_message}"
                    await self.send_message_in_chunks(target_channel_id, latest_vn_tl_updates_message_with_ping, logger)
                else:
                    fallback_message = "No content found for the latest VNTS post."
                    logger.warning(fallback_message)
                    await self.post_message(target_channel_id, fallback_message, logger)
            else:
                fallback_message = "No latest VNTS post found. Sending fallback message."
                logger.warning(fallback_message)
                await self.post_message(target_channel_id, fallback_message, logger)
        except Exception as e:
            logger.error(f"Error while dispatching VNTS update: {e}")
            
    async def dispatch_new_vg_annoucements(self, target_channel_id, logger):
        try:
            logger.info("Fetching the latest vg big annoucements post from Reddit...")
            latest_game_releases = self.reddit_client.fetch_latest_game_releases()

            if latest_game_releases:
                await self.post_message(target_channel_id, "@everyone @here", logger)
                for game_release in latest_game_releases:
                    await self.post_message(target_channel_id, game_release['url'], logger)
            else:
                fallback_message = "No latest vg big annoucements post found. Sending fallback message."
                logger.warning(fallback_message)
                await self.post_message(target_channel_id, fallback_message, logger)
        except Exception as e:
            logger.error(f"Error while dispatching the latest vg big annoucements post: {e}")

    def get_random_member(self, member_list):
        return random.choice(member_list.split('|'))