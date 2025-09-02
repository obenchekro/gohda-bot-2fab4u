import asyncio
import re

class MessagingService:
    TYPING_MAX_DELAY = 3
    TYPING_CHARS_PER_SECOND = 20

    async def post_message(self, channel_id, message, logger):
        channel = await self.fetch_channel(channel_id)
        async with channel.typing():  
            await asyncio.sleep(min(self.TYPING_MAX_DELAY, len(message) / self.TYPING_CHARS_PER_SECOND))
            await channel.send(message)
        logger.info(f"message '{message}' has been successfully rendered...")
    
    async def send_gif(self, channel_id, logger):
        gif_url = await self.giphy_client.get_gif_url()
        
        if gif_url:
            logger.info(f"Media GIF {gif_url} has been successfully rendered...")
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
                        "🪢 `@bot hm` → Start a Hangman game. For rules, type `@bot hm rules`.\n"
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