from dotenv import load_dotenv
load_dotenv()

import os
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
COHERE_TOKEN = os.environ['COHERE_TOKEN']
DEBUG_CHANNEL_ID = int(os.environ['DEBUG_CHANNEL_ID'])

MAX_HISTORY_LENGTH = 50
