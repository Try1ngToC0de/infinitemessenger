import os
from dotenv import load_dotenv

load_dotenv()

JB_API = os.getenv('JSONBOX_API_KEY')
JB_URL = os.getenv('JSONBOX_URL')
