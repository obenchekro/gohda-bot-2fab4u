import asyncio
from client import DiscordClient
from scheduler import Scheduler
from dotenv import load_dotenv
import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
load_dotenv()

TOKEN = os.getenv('ACCESS_TOKEN')
GIF_CHANNEL_ID = os.getenv('GIF_CHANNEL_ID')
QUOTE_CHANNEL_ID = os.getenv('QUOTE_CHANNEL_ID')
VN_TL_CHANNEL_ID = os.getenv('VN_TL_CHANNEL_ID')
VG_RELEASES_CHANNEL_ID = os.getenv('VG_RELEASES_CHANNEL_ID')

TENOR_API_KEY = os.getenv('TENOR_API_KEY')
HUGGING_FACE_API_KEY = os.getenv('HUGGING_FACE_API_KEY')

REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')

MEMBER_LIST = os.getenv('MEMBERS_LIST')

GIF_DELAY = 10
QUOTE_DELAY = 60 * 60 * 60
VG_VN_MESSAGE_DELAY = 604800

client = DiscordClient(TOKEN, TENOR_API_KEY, HUGGING_FACE_API_KEY, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)
scheduler = Scheduler(client)

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger('discord_bot')

@client.event
async def on_ready():
    logger.info(f'Logged in as {client.user}')

    batches_to_schedule = [
        scheduler.schedule_gif(GIF_CHANNEL_ID, GIF_DELAY, logger),
        scheduler.schedule_mention(QUOTE_CHANNEL_ID, QUOTE_DELAY, MEMBER_LIST, logger),
        scheduler.schedule_dispatch_vn_tl_message(VN_TL_CHANNEL_ID, VG_VN_MESSAGE_DELAY, logger),
        scheduler.schedule_dispatch_vg_releases_message(VG_RELEASES_CHANNEL_ID, VG_VN_MESSAGE_DELAY, logger)
    ]

    asyncio.gather(*[asyncio.create_task(t) for t in batches_to_schedule])

if __name__ == '__main__':
    client.run(TOKEN)
