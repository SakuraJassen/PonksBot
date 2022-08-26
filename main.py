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
    await ctx.send('pong')

@client.command()
async def close(ctx):
    await ctx.send('Exiting...')
    await client.close()

@client.command()
async def removeTile(ctx, argument):
    ##tileList.remove(Tile(argument))
    await ctx.send(f'notImplementedException()')

@client.command()
async def printTile(ctx):
    for t in Tile.tileList:
        await ctx.send(f'Current Tile: {t.id}')

@client.command()
async def addTile(ctx, argument):
    Tile.tileList.append(Tile.TileClass(argument, datetime()))
    await ctx.send(f'Adding Tile: {argument}')

@client.command()
async def setTileSeconds(ctx, argument, argument2):
    found = False
    for t in Tile.tileList:
        if t.id == argument:
            found = True
            t.refreshTimer = datetime.now() + timedelta(seconds=argument2)
            await ctx.send(f'Setting Time of Tile {t.id} to {t.refreshTimer}')
    if not found:
        await ctx.send(f'Couldnt find Tile with ID {argument}')

@client.command()
async def setTile(ctx, argument, hours: int, minutes: int, seconds: int):
    found = False
    for t in Tile.tileList:
        if t.id == argument:
            found = True
            t.refreshTimer = datetime.now() + timedelta(hours=hours, minutes=minutes, seconds=seconds)
            await ctx.send(f'Setting Time of Tile {t.id} to {t.refreshTimer}')
    if not found:
        await ctx.send(f'Couldnt find Tile with ID {argument}')

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await client.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with client:
        await load_extensions()
        await client.start('')


asyncio.run(main())
