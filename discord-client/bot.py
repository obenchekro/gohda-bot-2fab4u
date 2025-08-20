import argparse
import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
load_dotenv()

import environments
from client import DiscordClient
from scheduler import Scheduler
from commands import Commands

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger('discord_bot')

def parse_args():
    parser = argparse.ArgumentParser(description="Run a Discord bot (gohda or zaim)")
    parser.add_argument('--bot', choices=['gohda', 'zaim'], required=True, help="Type of bot to run (gohda or zaim)")
    return parser.parse_args()

async def run_bot(bot_type):
    if bot_type == "gohda":
        token = environments.TOKEN_GOHDA
    elif bot_type == "zaim":
        token = environments.TOKEN_ZAIM
    else:
        raise ValueError("Bot type not recognized. Use --bot gohda or --bot zaim.")

    client = DiscordClient(
        token=token,
        giphy_token=environments.TENOR_API_KEY,
        reddit_client_id=environments.REDDIT_CLIENT_ID,
        reddit_client_secret=environments.REDDIT_CLIENT_SECRET,
        bot_type=bot_type
    )

    scheduler = Scheduler(client)
    commands = Commands(client, logger, gohda_id=environments.GOHDA_ID, zaim_id=environments.ZAIM_ID)


    @client.event
    async def on_ready():
        logger.info(f"[{bot_type.upper()}] Logged in as {client.user}")
        client.llm_client.bot_id = client.user.id
        client.gohda_id = environments.GOHDA_ID
        client.zaim_id = environments.ZAIM_ID

        await commands.setup()
        await schedule_tasks_for_bot(scheduler, logger, bot_type)

    @client.event
    async def on_message(message):
        await client.handle_mention_message(message, bot_type, environments.GOHDA_ID, environments.ZAIM_ID, logger)

    await client.start(token)

async def schedule_tasks_for_bot(scheduler, logger, bot_type):
    tasks = []
    if bot_type == "gohda":
        tasks.extend([
            scheduler.schedule_dm_blank_message(environments.MEMBER_LIST, environments.QUOTE_DELAY, logger),
            scheduler.schedule_gif(environments.GIF_CHANNEL_ID, environments.GIF_DELAY, logger),
            scheduler.schedule_mention(environments.QUOTE_CHANNEL_ID, environments.QUOTE_DELAY, environments.MEMBER_LIST, bot_type, logger),
            scheduler.schedule_dispatch_vn_tl_message(environments.VN_TL_CHANNEL_ID, environments.VG_VN_MESSAGE_DELAY, logger),
            scheduler.schedule_dispatch_vg_releases_message(environments.VG_RELEASES_CHANNEL_ID, environments.VG_VN_MESSAGE_DELAY, logger),
            scheduler.schedule_dispatch_csgo_trades_skins(environments.ZBIYEB_ID, environments.CSGO_SKINS_NEWS_CHANNEL_ID, environments.VG_VN_MESSAGE_DELAY, logger),
            scheduler.schedule_dispatch_ln_wn_news(environments.ZBIYEB_ID, environments.LN_WN_NEWS_CHANNEL_ID, environments.VG_VN_MESSAGE_DELAY, logger),
            scheduler.schedule_dispatch_financial_markets_news(environments.OWNER_ID, environments.CRYPTO_ETF_NEW_CHANNEL_ID, environments.VG_VN_MESSAGE_DELAY, logger)
        ])
    elif bot_type == "zaim":
        tasks.extend([
            scheduler.schedule_mention(environments.QUOTE_CHANNEL_ID, environments.QUOTE_DELAY, environments.MEMBER_LIST, bot_type, logger)
        ])

    await asyncio.gather(*[asyncio.create_task(t) for t in tasks])

if __name__ == '__main__':
    try:
        args = parse_args()
        asyncio.run(run_bot(args.bot))
    except Exception as e:
        logger.error(f"Failed to launch bot: {e}")
        sys.exit(1)
