import asyncio
import re
import discord
import os
import random
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from libs.dank_meme_extractor.tenor_client import TenorClient
from libs.llm_integrator.llm_client import LLMClient
from libs.reddit_threads.reddit_client import RedditVNTLFetcher

class DiscordClient(discord.Client):
    def __init__(self, token, giphy_token, reddit_client_id, reddit_client_secret, bot_type, logger=None):
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True

        super().__init__(intents=intents)
        self.token = token
        self.bot_type = bot_type
        self.giphy_client = TenorClient(giphy_token)
        self.llm_client = LLMClient()
        self.clash_active = False
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
    
    async def mention_with_llm_response(self, channel_id, member_list, bot_type, logger):
        try:
            channel = await self.fetch_channel(channel_id)
            member_id = self.get_random_member(member_list)
            member = await channel.guild.fetch_member(member_id)

            mention = member.mention
            logger.info(f"Mention resolved: {mention}")

            quote = await self.llm_client.generate_quote(bot_type, logger=logger)
            message = f"{mention} {quote}"

            await channel.send(message)
            logger.info("Message with mention and quote sent.")
        except Exception as e:
            logger.error(f"Error while mentioning member and sending quote: {e}")
    
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
                    await self.post_message(message.channel.id, roast, logger)
                    return

                if not cleaned_msg:
                    await self.post_message(
                        message.channel.id,
                        "You mentionned the jackass of me and can't mimically asking for anything? You pathetic cranking soulja boy.",
                        logger
                    )
                    return
                            
                if cleaned_msg.lower() == "man":
                    manual = (
                        "**📘 Bot Command Manual**\n"
                        "Here are the available commands:\n\n"
                        "🗣️ `@bot [text]` → Responds to your message in shitpost style.\n"
                        "⚔️ `@bot fart` → Starts a roast battle between Gohda and Zaim.\n"
                        "💨 `@bot unfart` → Stops the roast battle.\n"
                        "🎯 `@bot man` → Displays this manual.\n"
                        "📈 `@bot news` → Fetches financial, crypto, and stock market updates (automated).\n"
                        "🎮 `@bot vg` → Fetches big /vg/ announcements (automated).\n"
                        "📰 `@bot vnts` → Sends the latest visual novel translation status (automated).\n"
                        "🔫 `@bot csgo` → Sends the latest trendy csgo trades from reddit (automated).\n"
                    )
                    await self.post_message(message.channel.id, manual, logger)
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

                reply = await self.llm_client.generate_quote_from_user_input(bot_type, cleaned_msg, logger=logger)
                await self.post_message(message.channel.id, reply, logger)

            except Exception as e:
                await self.post_message(
                    message.channel.id,
                    "Something went wrong in the vortex of Riruru-chan's dimension 🌀",
                    logger
                )
                logger.error(f"[on_message error]: {e}")

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

    async def dispatch_news_csgo_trades_skins(self, member_id, target_channel_id, logger):
        try:
            logger.info("Fetching the latest csgo trades skins post from Reddit...")
            latest_csgo_trades = self.reddit_client.fetch_csgo_news_and_tradesites()

            if latest_csgo_trades:
                channel = await self.fetch_channel(target_channel_id)
                member = await channel.guild.fetch_member(member_id)
                await self.post_message(target_channel_id, member.mention, logger)
                for trade in latest_csgo_trades:
                    await self.post_message(target_channel_id, trade['url'], logger)
            else:
                fallback_message = "No latest csgo trades skins post found. Sending fallback message."
                logger.warning(fallback_message)
                await self.post_message(target_channel_id, fallback_message, logger)
        except Exception as e:
            logger.error(f"Error while dispatching the latest csgo trades skins: {e}")
    
    async def dispatch_news_financial_markets(self, member_id, target_channel_id, logger):
        try:
            logger.info("Fetching the latest financial market posts (crypto, ETFs, stocks)...")

            crypto_posts = self.reddit_client.fetch_crypto_news(logger=logger)
            etf_posts = self.reddit_client.fetch_etf_news(logger=logger)
            stock_posts = self.reddit_client.fetch_stock_market_news(logger=logger)

            all_posts = crypto_posts + etf_posts + stock_posts

            if all_posts:
                channel = await self.fetch_channel(target_channel_id)
                member = await channel.guild.fetch_member(member_id)
                await self.post_message(target_channel_id, f"{member.mention}\n📊 Here's your financial market briefing:", logger)

                categories = [("📈 Crypto", crypto_posts), ("💼 ETFs", etf_posts), ("🇺🇸/🇫🇷 Stocks", stock_posts)]
                for title, posts in categories:
                    if posts:
                        await self.post_message(target_channel_id, f"**{title}**", logger)
                        for post in posts:
                            await self.post_message(target_channel_id, post['url'], logger)
            else:
                msg = "No financial news found (crypto, ETFs, or stock markets)."
                logger.warning(msg)
                await self.post_message(target_channel_id, msg, logger)

        except Exception as e:
            logger.error(f"Error while dispatching financial market news: {e}")

    async def dm_blank_message(self, member_list, logger):
        try:
            random_user_id = self.get_random_member(member_list)
            user = await self.fetch_user(random_user_id)
            
            payload = "||" + ("\n" * (self.MAX_MESSAGE_CHUNK_SIZE_LIMIT - 4)) + "||"
            await user.send(payload)
            logger.info(f"Blank DM sent to {user.name}")
        except Exception as e:
            logger.error(f"Error occurred while sending the blank DM: {e}")

    async def clash_between_gohda_and_zaim(self, channel_id, gohda_id, zaim_id, logger):
        self.clash_active = True

        gohda_mention = f"<@{gohda_id}>"
        zaim_mention = f"<@{zaim_id}>"

        logger.info("🔥 Clash between Gohda and Zaim started.")
        gohda_turn = True

        try:
            while self.clash_active:
                if gohda_turn:
                    roast = await self.llm_client.generate_roast("gohda", zaim_mention, logger=logger)
                    if roast:
                        message = f"{zaim_mention} {roast}"
                        await self.post_message(channel_id, message, logger)
                else:
                    roast = await self.llm_client.generate_roast("zaim", gohda_mention, logger=logger)
                    if roast:
                        message = f"{gohda_mention} {roast}"
                        await self.post_message(channel_id, message, logger)

                gohda_turn = not gohda_turn
                await asyncio.sleep(5)

        except asyncio.CancelledError:
            logger.info("Clash coroutine cancelled by unfart.")
        finally:
            await self.post_message(channel_id, "🛑 Gohda and Zaim stopped roasting. The arena is silent.", logger)
            logger.info("Clash ended.")
   
    async def trigger_clash(self, channel_id, gohda_id, zaim_id, logger):
        self.clash_active = True
        await self.post_message(channel_id, "⚔️ Fart detected. Gohda vs Zaim initiated!", logger)
        self.clash_task = asyncio.create_task(self.clash_between_gohda_and_zaim(channel_id, gohda_id, zaim_id, logger))

    async def stop_clash(self, channel_id, logger):
        self.clash_active = False
        if self.clash_task:
            self.clash_task.cancel()
            self.clash_task = None
        await self.post_message(channel_id, "💨 The fart has been unfarted. Peace restored.", logger)

    def get_random_member(self, member_list):
        return random.choice(member_list.split('|'))