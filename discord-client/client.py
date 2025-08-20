import asyncio
import re
import discord
from discord import app_commands
import os
import random
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from libs.bot_games.tic_tac_toe import TicTacToeGame
from libs.dank_meme_extractor.tenor_client import TenorClient
from libs.llm_integrator.llm_client import LLMClient
from libs.reddit_threads.reddit_client import RedditVNTLFetcher

class DiscordClient(discord.Client):
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

    async def post_message(self, channel_id, message, logger):
        channel = await self.fetch_channel(channel_id)
        await channel.send(message)
        logger.info(f'message \'{message}\' has been successfully rendered...')
    
    async def send_gif(self, channel_id, logger):
        gif_url = await self.giphy_client.get_gif_url()
        
        if gif_url:
            logger.info(f'Media GIF {gif_url} has been successfully rendered...')
            await self.post_message(channel_id, gif_url, logger)
        else:
            logger.error("Failed to get GIF URL...")
            await self.post_message(channel_id, ":ggohda:", logger)
    
    async def mention_with_llm_response(self, channel_id, member_list, bot_type, logger):
        try:
            channel = await self.fetch_channel(channel_id)
            member_id = self.get_random_member(member_list)
            member = await channel.guild.fetch_member(member_id)

            mention = member.mention
            logger.info(f"Mention resolved: {mention}")

            quote = await self.llm_client.generate_quote(bot_type, logger=logger)
            message = f"{mention} {quote}"

            await self.post_message(channel_id, message, logger)
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
    
    async def dispatch_ln_wn_news(self, member_id, target_channel_id, logger):
        try:
            logger.info("Fetching the latest light novel/web novel posts from Reddit...")
            latest_ln_wn_posts = self.reddit_client.fetch_latest_ln_wn_news()

            if latest_ln_wn_posts:
                channel = await self.fetch_channel(target_channel_id)
                member = await channel.guild.fetch_member(member_id)
                await self.post_message(target_channel_id, member.mention, logger)
                for trade in latest_ln_wn_posts:
                    await self.post_message(target_channel_id, trade['url'], logger)
            else:
                fallback_message = "No latest light novel/web novel post found. Sending fallback message."
                logger.warning(fallback_message)
                await self.post_message(target_channel_id, fallback_message, logger)
        except Exception as e:
            logger.error(f"Error while dispatching the latest light novel/web novel posts: {e}")
    
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
    
    async def man(self, channel, logger):
        try:
            manual = (
                        "**📘 Bot Command Manual**\n"
                        "Here are the available commands:\n\n"
                        "🗣️ `@bot [text]` → Responds to your message in shitpost style.\n"
                        "🖼️ `@bot [gif]` → Post a gif related to a dank meme of a specific VG/VN.\n"
                        "⚔️ `@bot fart` → Starts a roast battle between Gohda and Zaim.\n"
                        "💨 `@bot unfart` → Stops the roast battle.\n"
                        "🎯 `@bot man` → Displays this manual.\n"
                        "📈 `@bot news` → Fetches financial, crypto, and stock market updates (automated).\n"
                        "🎮 `@bot vg` → Fetches big /vg/ announcements (automated).\n"
                        "📰 `@bot vnts` → Sends the latest visual novel translation status (automated).\n"
                        "🔫 `@bot csgo` → Sends the latest trendy csgo trades from reddit (automated).\n"
                        "📚 `@bot ln` → Sends the latest light novel/web novel news from reddit (automated).\n"
                        "🎲 `@bot ttt [N]` → Start a Tic-Tac-Toe game (default 3x3, choose size with N). For rules, type `@bot ttt rules`.\n"
                        "💣 `@bot punish @user` → Plays Russian Roulette by sending a blank DM to the target.\n"
                    )
            await self.post_message(channel, manual, logger)
            logger.info("Bot manual displayed.")
        except Exception as e:
            logger.error(f"Error occurred while trying to display the commands manual: {e}")
    
    async def punish_user(self, message, channel, logger):
        try:
            member_id_matched = re.search(r"<@!?(\d+)>", message)
            if member_id_matched:
                target_id = member_id_matched.group(1)
                await self.post_message(
                    channel,
                    f"<@{target_id}> will get his ass washed out for {self.MAX_MESSAGE_CHUNK_SIZE_LIMIT} times!",
                    logger
                )
                for _ in range(self.MAX_MESSAGE_CHUNK_SIZE_LIMIT):
                    await self.dm_blank_message(target_id, logger)
                    await asyncio.sleep(5)
            else:
                await self.post_message(
                    channel,
                    "❌ No target mentioned for punishment. Use `@bot punish @user`.",
                    logger
                )
        except Exception as e:
            logger.error(f"Error while trying to punish the user {target_id}: {e}")

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
                        await self.send_message_in_chunks(channel_id, message, logger)
                else:
                    roast = await self.llm_client.generate_roast("zaim", gohda_mention, logger=logger)
                    if roast:
                        message = f"{gohda_mention} {roast}"
                        await self.send_message_in_chunks(channel_id, message, logger)

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

    async def handle_ttt(self, message, cleaned_msg, logger):
        if not hasattr(self, "ttt_sessions"):
            self.ttt_sessions = {}

        key = (message.channel.id, message.author.id)
        MIN_SIZE = 3
        MAX_SIZE = 10

        if cleaned_msg.lower() in ("ttt rules", "tic tac toe rules", "tictactoe rules"):
            await self.post_message(
                message.channel.id,
                "**📘 Tic-Tac-Toe Rules**\n"
                "- The game is played on an N×N board (default 3×3).\n"
                "- You play with ❌, the bot plays with ⭕.\n"
                "- Players take turns placing their symbol.\n"
                "- First to align N symbols in a row, column, or diagonal wins.\n"
                "- If the board fills with no winner, it’s a draw.\n"
                "- To play: type `A1`, `2 3`, or `5` (for 3×3).\n"
                "- Type `stop` to quit anytime.",
                logger
            )
            return True

        if key in self.ttt_sessions and self.ttt_sessions[key].active:
            game = self.ttt_sessions[key]
            reply = game.handle_message(cleaned_msg)
            if reply is None:
                await self.post_message(
                    message.channel.id,
                    "❓ Not a move. Examples: `A1`, `2 3`, `5` (3×3 numpad), or `stop`.",
                    logger
                )
                return True
            await self.post_message(message.channel.id, reply, logger)
            if not game.active:
                self.ttt_sessions.pop(key, None)
            return True

        m = re.match(r"^(?:ttt|ttt\s+start|tic\s*tac\s*toe|tictactoe)(?:\s+(.*))?$", cleaned_msg.strip(), flags=re.IGNORECASE)
        if m:
            args = (m.group(1) or "").strip()
            size = None
            hint = ""

            if not args:
                size = 3
                hint = f"(defaulting to {size}x{size}; you can start with `ttt 5` or `ttt 4x4`)"
            else:
                m2 = re.match(r"^(\d{1,2})(?:\s*[xX]\s*(\d{1,2}))?$", args)
                if not m2:
                    await self.post_message(
                        message.channel.id,
                        f"❌ Invalid board size. Use `ttt N` or `ttt NxN` (min {MIN_SIZE}, max {MAX_SIZE}).",
                        logger
                    )
                    return True
                n1 = int(m2.group(1))
                n2 = int(m2.group(2)) if m2.group(2) else n1
                if n1 != n2:
                    await self.post_message(message.channel.id, "❌ Only square boards are supported (e.g., `ttt 5` or `ttt 5x5`).", logger)
                    return True
                if not (MIN_SIZE <= n1 <= MAX_SIZE):
                    await self.post_message(message.channel.id, f"❌ Size out of range. Allowed: {MIN_SIZE}–{MAX_SIZE}.", logger)
                    return True
                size = n1

            game = TicTacToeGame(message.channel.id, message.author.id, size=size)
            self.ttt_sessions[key] = game
            await self.post_message(
                message.channel.id,
                f"🎮 Tic-Tac-Toe {size}x{size} started! {hint}\n{game.format_board()}\nYour turn! (Examples: `A1`, `5 2`, or `stop`)",
                logger
            )
            return True

        if cleaned_msg.lower() in ("ttt stop", "stop ttt", "tictactoe stop"):
            game = self.ttt_sessions.get(key)
            if game and game.active:
                msg = game.stop()
                self.ttt_sessions.pop(key, None)
                await self.post_message(message.channel.id, msg, logger)
            else:
                await self.post_message(message.channel.id, "No active game found.", logger)
            return True

        return False


    def get_random_member(self, member_list):
        return random.choice(member_list.split('|'))