import asyncio
import random
import sys
import traceback
from datetime import datetime, timedelta

import discord
from discord.ext import tasks, commands

import Tile


class MainCog(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        self.update_time.start()
        self.tileChannel = None

    def cog_unload(self):
        self.update_time.cancel()

    @commands.command()
    async def pingTile(self, ctx):
        await ctx.send('pong pog')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound,)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        # For this error example we check to see where it came from...
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
                await ctx.send('I could not find that member. Please try again.')

        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            await self.client.change_presence(activity=discord.Game(name="deadlole"))

    @tasks.loop(seconds=10)
    async def update_time(self):
        for t in Tile.TileList:
            print(f"looking at tile: {t.id}")
            if t.message == 0:
                t.message = await self.tileChannel.send(f"Tile: {t.id}")
                await t.message.add_reaction("♻️")

            # Only update Tile with a Timer and where the last Update is more than 5 Seconds ago
            totalSinceLastUpdate = (datetime.now() - t.lastUpdate).total_seconds()
            if isinstance(t.refreshTimer, datetime) and totalSinceLastUpdate > 90 + int(random.random() * 10):
                print(f"updating tile: {t.id}")
                t.lastUpdate = datetime.now()
                s = await Tile.formateMSG(t)
                await t.message.edit(content=s)
                await asyncio.sleep(1)
                print(f"... Time since last Update: {totalSinceLastUpdate}")
        await asyncio.sleep(1)
        print("sleeping...")

    @update_time.before_loop
    async def before_update_time(self):
        print('waiting...')
        await self.client.wait_until_ready()
        if self.tileChannel is None:
            print("Searching Channel")
            channel = discord.utils.get(self.client.get_all_channels(), name='tile-refresh')
            self.tileChannel = channel
            print(f"Found channel {self.tileChannel}")

            async for msg in channel.history(limit=200):
                parsed = await Tile.parseMSG(msg.content)
                if parsed is not None:
                    if len(parsed.groups()) == 1:
                        Tile.TileList.append(Tile.TileClass(parsed.group(1), Tile.TileType.EMPTY, timedelta(seconds=0)))
                        Tile.TileList[-1].message = msg
                    elif len(parsed.groups()) == 2:
                        timeToSec = sum(x * int(t) for x, t in zip([3600, 60, 1], parsed.group(2).split(":")))
                        Tile.TileList.append(Tile.TileClass(parsed.group(1), Tile.TileType.EMPTY, datetime.now() + timedelta(seconds=timeToSec)))
                        Tile.TileList[-1].message = msg
                    else:
                        print(f"couldn't ParseTile: {msg.content}")


async def setup(bot):
    await bot.add_cog(MainCog(bot))
