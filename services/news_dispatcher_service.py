class NewsDispatcherService:
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