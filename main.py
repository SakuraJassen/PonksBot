import asyncio
import os
from MySQLdb import _mysql as mysql

from datetime import datetime, timedelta

import discord
from discord.ext import tasks, commands

import TileSQL

intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

@client.command()
async def ping(ctx):
    await ctx.send('pong!')

@client.command()
async def close(ctx):
    await ctx.send('Exiting...')
    maincog = client.get_cog('MainCog')
    await TileSQL.updateTileList(maincog.db, maincog.TileList)
    await client.close()

async def load_extensions():
    for filename in reversed(os.listdir("./cogs")):  # Changed Absolute path /home/pi/PonksBot/cogs"
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await client.load_extension(f"cogs.{filename[:-3]}")

async def main():
    token = open("./token")
    async with client:
        await load_extensions()
        await client.start(token.read())


asyncio.run(main())
