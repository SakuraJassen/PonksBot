import asyncio
import random
import sys
import traceback
from datetime import datetime, timedelta

import discord
from discord.ext import tasks, commands
import MySQLdb
import TileSQL

class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None
        try:
            self.db = MySQLdb.connect(user='botuser', password='SlFs2020', host='192.168.0.69', database='bot')
        except MySQLdb.Error as err:
            print(err)

        self.update_time.start()
        self.tileChannel = None
        self.TileList = []

    def cog_unload(self):
        self.update_time.cancel()

    @commands.command()
    async def pingTile(self, ctx):
        await ctx.send('pong pog11')

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        if self.tileChannel is None:
            print("Searching Channel")
            channel = discord.utils.get(self.bot.get_all_channels(), name='tile-refresh')
            self.tileChannel = channel
            print(f"Found channel {self.tileChannel}")

        self.TileList = TileSQL.getAllTiles(self.db, self.tileChannel)

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
            await self.bot.change_presence(activity=discord.Game(name="deadlole"))

    @tasks.loop(seconds=30)
    async def update_time(self):
        while self.db is None:
            print("couldn't connect to database retrying...")
            self.db = MySQLdb.connect(user='botuser', password='SlFs2020', host='192.168.0.69', database='bot')

            await asyncio.sleep(1)

        tl = await TileSQL.getAllTiles(self.db, self.tileChannel)
        self.TileList = tl
        for t in self.TileList:
            print(f"looking at tile: {t.id}")
            if t.msg_id == 0 or t.msg_id is None:
                t.message = await self.tileChannel.send(f"Tile: {t.id}")
                t.msg_id = t.message.id
                await t.message.add_reaction("♻️")

            if t.message is None:
                try:
                    t.message = await self.tileChannel.fetch_message(t.msg_id)
                except discord.NotFound:
                    t.message = await self.tileChannel.send(f"Tile: {t.id}")
                    t.msg_id = t.message.id
                    await t.message.add_reaction("♻️")

            # Only update Tile with a Timer and where the last Update is more than 5 Seconds ago
            totalSinceLastUpdate = (datetime.now() - t.lastUpdate).total_seconds()
            print(f"... Time since last Update: {totalSinceLastUpdate}")
            if t.shouldUpdate or (isinstance(t.refreshTimer, datetime) and totalSinceLastUpdate > 90 + int(random.random() * 10)):
                t.shouldUpdate = False
                print(f"updating tile: {t.id}")
                t.lastUpdate = datetime.now() + timedelta(seconds=int(random.random() * 120))
                s = await TileSQL.formateMSG(t)
                await t.message.edit(content=s)
                #await asyncio.sleep(1)

        await asyncio.sleep(1)
        await TileSQL.updateTileList(self.db, self.TileList)
        print("sleeping...")

    @update_time.before_loop
    async def before_update_time(self):
        print('waiting...')
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(MainCog(bot))
