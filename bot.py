from dotenv import load_dotenv
load_dotenv()
import os
import discord
from discord.ext import commands
import pangea.exceptions as pe
from pangea.config import PangeaConfig
from pangea.services import Redact

# Pangea Redact service setup
token = os.getenv("PANGEA_REDACT_TOKEN")
domain = os.getenv("PANGEA_DOMAIN")
config = PangeaConfig(domain=domain)
redact = Redact(token, config=config)

# Discord bot setup
discord_token = os.getenv("DISCORD_BOT_TOKEN")
intents = discord.Intents.all()
intents.messages = True 
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    try:
        # Redact API keys using Pangea Redact service
        redact_response = redact.redact(text=message.content)
        if redact_response.result.redacted_text != message.content:
            await message.delete()
            await message.channel.send(f"Message from {message.author} contained sensitive information and was removed.")
            print(f"Removed sensitive information from a message by {message.author} in channel {message.channel}.")  # Log to console
    except pe.PangeaAPIException as e:
        print(f"Pangea Redact Error: {e.response.summary}")
        for err in e.errors:
            print(f"\t{err.detail}")

    await bot.process_commands(message)

bot.run(discord_token)
