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
TENOR_API_KEY = os.getenv('TENOR_API_KEY')
DELAY = 10

HUGGING_FACE_API_KEY = os.getenv('HUGGING_FACE_API_KEY')
MEMBER_LIST = os.getenv('MEMBERS_LIST')

client = DiscordClient(TOKEN, TENOR_API_KEY, HUGGING_FACE_API_KEY)
scheduler = Scheduler(client)

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger('discord_bot')

@client.event
async def on_ready():
    logger.info(f'Logged in as {client.user}')
    asyncio.create_task(scheduler.schedule_gif(GIF_CHANNEL_ID, DELAY, logger))
    asyncio.create_task(scheduler.schedule_mention(QUOTE_CHANNEL_ID, DELAY, MEMBER_LIST, logger))

if __name__ == '__main__':
    client.run(TOKEN)
