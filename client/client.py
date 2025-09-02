import re
import discord
from discord import app_commands
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from libs.dank_meme_extractor.tenor_client import TenorClient
from libs.llm_integrator.llm_client import LLMClient
from libs.reddit_threads.reddit_client import RedditVNTLFetcher

from services import MessagingService, ClashService, TTTService, NewsDispatcherService, UtilsService, HangmanService

class DiscordClient(MessagingService, ClashService, TTTService, HangmanService, NewsDispatcherService, UtilsService, discord.Client):
    def __init__(self, token, giphy_token, reddit_client_id, reddit_client_secret, bot_type, logger=None):
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True

        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)
        self.token = token
        self.bot_type = bot_type
        self.giphy_client = TenorClient(giphy_token)
        self.llm_client = LLMClient()
        self.clash_active = False
        self.gohda_id = None
        self.zaim_id = None
        self.ttt_sessions = {}
        self.MAX_MESSAGE_CHUNK_SIZE_LIMIT = 2000

        self.reddit_client = RedditVNTLFetcher(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret
        )

    async def handle_mention_message(self, message, bot_type, gohda_id, zaim_id, logger):
        if message.author == self.user:
            return
             
        if "fart" in message.content.lower() and not self.clash_active:
            await self.trigger_clash(message.channel.id, gohda_id, zaim_id, logger)
            return

        if "unfart" in message.content.lower() and self.clash_active:
            await self.stop_clash(message.channel.id, logger)
            return

        if self.user.mentioned_in(message):
            try:
                cleaned_msg = re.sub(rf"<@!?{self.user.id}>", "", message.content).strip()
                
                if message.author.bot:
                    target_mention = f"<@{message.author.id}>"
                    roast = await self.llm_client.generate_roast(bot_type, target_mention, logger=logger)
                    await self.send_message_in_chunks(message.channel.id, roast, logger)
                    return

                if not cleaned_msg:
                    await self.post_message(
                        message.channel.id,
                        "You mentionned the jackass of me and can't mimically asking for anything? You pathetic cranking soulja boy.",
                        logger
                    )
                    return

                if await self.handle_ttt(message, cleaned_msg, logger):
                    return

                if await self.handle_hangman(message, cleaned_msg, logger):
                    return
                            
                if cleaned_msg.lower() == "man":
                    await self.man(message.channel.id, logger)
                    return
                
                if cleaned_msg.lower() == "gif":
                    await self.send_gif(message.channel.id, logger)
                    return

                if cleaned_msg.lower() == "news":
                    await self.dispatch_news_financial_markets(message.author.id, message.channel.id, logger)
                    return
                
                if cleaned_msg.lower() == "vg":
                    await self.dispatch_new_vg_annoucements(message.channel.id, logger)
                    return
                
                if cleaned_msg.lower() == "vnts":
                    await self.dispatch_vn_tl_updates_daily(message.channel.id, logger)
                    return
                
                if cleaned_msg.lower() == "csgo":
                    await self.dispatch_news_csgo_trades_skins(message.author.id, message.channel.id, logger)
                    return
                
                if cleaned_msg.lower() == "ln":
                    await self.dispatch_ln_wn_news(message.author.id, message.channel.id, logger)
                    return
            
                if cleaned_msg.lower().startswith("punish"):
                    await self.punish_user(cleaned_msg, message.channel.id, logger)
                    return

                reply = await self.llm_client.generate_quote_from_user_input(bot_type, cleaned_msg, logger=logger)
                await self.send_message_in_chunks(message.channel.id, reply, logger)

            except Exception as e:
                await self.post_message(
                    message.channel.id,
                    "Something went wrong in the vortex of Riruru-chan's dimension 🌀",
                    logger
                )
                logger.error(f"[on_message error]: {e}")
