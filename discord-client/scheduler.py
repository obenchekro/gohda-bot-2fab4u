import asyncio
from client import DiscordClient

class Scheduler:
    def __init__(self, client: DiscordClient):
        self.client = client

    async def __loop_task(self, delay, logger, task_name, coro, *args):
        while True:
            try:
                await coro(*args)
                logger.info(f"Task '{task_name}' executed successfully.")
            except Exception as e:
                logger.error(f"Error in task '{task_name}': {e}")
            await asyncio.sleep(delay)

    async def schedule_message(self, channel_id, message, delay, logger):
        await self.__loop_task(
            delay,
            logger,
            "schedule_message",
            self.client.post_message,
            channel_id,
            message,
            logger
        )

    async def schedule_gif(self, channel_id, delay, logger):
        await self.__loop_task(
            delay,
            logger,
            "schedule_gif",
            self.client.send_gif,
            channel_id,
            logger
        )

    async def schedule_mention(self, channel_id, delay, member_list, logger):
        await self.__loop_task(
            delay,
            logger,
            "schedule_mention",
            self.client.mention_with_llm_response,
            channel_id,
            member_list,
            logger
        )

    async def schedule_dispatch_vn_tl_message(self, channel_id, delay, logger):
        await self.__loop_task(
            delay,
            logger,
            "schedule_dispatch_vn_tl_message",
            self.client.dispatch_vn_tl_updates_daily,
            channel_id,
            logger
        )

    async def schedule_dispatch_vg_releases_message(self, channel_id, delay, logger):
        await self.__loop_task(
            delay,
            logger,
            "schedule_dispatch_vg_releases_message",
            self.client.dispatch_new_vg_annoucements,
            channel_id,
            logger
        )

    async def schedule_dm_blank_message(self, member_list, delay, logger):
        await self.__loop_task(
            delay,
            logger,
            "schedule_dm_blank_message",
            self.client.dm_blank_message,
            member_list,
            logger
        )

    async def schedule_dispatch_csgo_trades_skins(self, member_id, channel_id, delay, logger):
        await self.__loop_task(
            delay,
            logger,
            "schedule_dispatch_csgo_trades_skins",
            self.client.dispatch_news_csgo_trades_skins,
            member_id,
            channel_id,
            logger
        )
    
    async def schedule_dispatch_financial_markets_news(self, member_id, channel_id, delay, logger):
        await self.__loop_task(
            delay,
            logger,
            "schedule_dispatch_financial_markets_news",
            self.client.dispatch_news_financial_markets,
            member_id,
            channel_id,
            logger
        )

