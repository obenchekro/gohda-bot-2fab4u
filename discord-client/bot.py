import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
load_dotenv()

import secrets
from client import DiscordClient
from scheduler import Scheduler

client = DiscordClient(
    secrets.TOKEN, 
    secrets.TENOR_API_KEY, 
    secrets.HUGGING_FACE_API_KEY, 
    secrets.REDDIT_CLIENT_ID, 
    secrets.REDDIT_CLIENT_SECRET
)
scheduler = Scheduler(client)

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger('discord_bot')

@client.event
async def on_ready():
    logger.info(f'Logged in as {client.user}')

    batches_to_schedule = [
        #scheduler.schedule_dm_blank_message(secrets.MEMBER_LIST, secrets.QUOTE_DELAY, logger),
        #scheduler.schedule_gif(secrets.GIF_CHANNEL_ID, secrets.GIF_DELAY, logger),
        #scheduler.schedule_mention(secrets.QUOTE_CHANNEL_ID, secrets.QUOTE_DELAY, secrets.MEMBER_LIST, logger),
        #scheduler.schedule_dispatch_vn_tl_message(secrets.VN_TL_CHANNEL_ID, secrets.VG_VN_MESSAGE_DELAY, logger),
        #scheduler.schedule_dispatch_vg_releases_message(secrets.VG_RELEASES_CHANNEL_ID, secrets.VG_VN_MESSAGE_DELAY, logger),
        #scheduler.schedule_dispatch_csgo_trades_skins(secrets.ZBIYEB_ID, secrets.CSGO_SKINS_NEWS_CHANNEL_ID, secrets.VG_VN_MESSAGE_DELAY, logger),
        scheduler.schedule_dispatch_financial_markets_news(secrets.OWNER_ID, secrets.CRYPTO_ETF_NEW_CHANNEL_ID, secrets.VG_VN_MESSAGE_DELAY, logger)
    ]

    asyncio.gather(*[asyncio.create_task(t) for t in batches_to_schedule])

if __name__ == '__main__':
    client.run(secrets.TOKEN)
