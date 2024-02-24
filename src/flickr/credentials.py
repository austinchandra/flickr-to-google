import os
from dotenv import load_dotenv

# Load the .env context:
load_dotenv()

api_key = os.getenv('FLICKR_API_KEY')
api_secret = os.getenv('FLICKR_API_SECRET')
