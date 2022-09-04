import asyncio
import os
from datetime import datetime, timedelta

import discord
from discord.ext import tasks, commands

import Tile

intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

Tile.init()

@client.command()
async def ping(ctx):
    await ctx.send('pong!')

@client.command()
async def close(ctx):
    await ctx.send('Exiting...')
    await client.close()

async def load_extensions():
    for filename in os.listdir("/home/pi/PonksBot/cogs"): # Changed Absolute path /home/pi/PonksBot/cogs"
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await client.load_extension(f"cogs.{filename[:-3]}")

async def main():
    token = open("/home/pi/PonksBot/token")
    async with client:
        await load_extensions()
        await client.start(token.read())


asyncio.run(main())
