import os
import discord
from dotenv import load_dotenv

load_dotenv()

DC_TOKEN = os.getenv('DC_TOKEN')
DC_GUILD = discord.Object(id=os.getenv('DC_GUILD'))
ORS_KEY = os.getenv('ORS_KEY')
