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
CHANNEL_ID = os.getenv('CHANNEL_ID')
TENOR_API_KEY = os.getenv('TENOR_API_KEY')
DELAY = 60 * 60

client = DiscordClient(TOKEN, TENOR_API_KEY)
scheduler = Scheduler(client)

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger('discord_bot')

@client.event
async def on_ready():
    logger.info(f'Logged in as {client.user}')
    asyncio.create_task(scheduler.schedule_gif(CHANNEL_ID, DELAY, logger))

if __name__ == '__main__':
    client.run(TOKEN)
