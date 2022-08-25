import traceback
from datetime import datetime
import re

import discord
from discord.ext import tasks, commands

import Tile

class MainCog(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        self.update_time.start()
        self.tileChannel = 0

    def cog_unload(self):
        self.updateTime.cancel()

    @commands.command()
    async def pingTile(self, ctx):
        await ctx.send('pong')

    @commands.command()
    async def addTile(self, ctx, argument):
        Tile.tileList.append(Tile.TileClass(argument, 0))
        await ctx.send(f'Adding Tile: {argument}')

    @commands.command()
    async def setTile(self, ctx, argument, argument2):
        found = False
        for t in Tile.tileList:
            if t.id == argument:
                found = True
                t.refreshTimer = int(argument2)
                await ctx.send(f'Setting Time of Tile {t.id} to {t.refreshTimer}')
        if not found:
            await ctx.send(f'Couldnt find Tile with ID {argument}')

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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        print(message.content)

    @tasks.loop(seconds=10)
    async def update_time(self):
        timeDelay = 10
        for t in Tile.tileList:
            if t.message == 0:
                t.message = await self.tileChannel.send(f"Tile: {t.id}")
                await t.message.add_reaction("♻️")

            cache_msg = await t.message.channel.fetch_message(t.message.id)
            for reaction in cache_msg.reactions:
                if reaction.emoji == "♻️" and reaction.count > 1:
                    t.refreshTimer = 28*60*60 + timeDelay
                    await reaction.remove()
                    await t.message.add_reaction("♻️")

            if t.refreshTimer > 1:
                t.refreshTimer -= timeDelay
                s = t.refreshTimer
                hours, remainder = divmod(s, 3600)
                minutes, seconds = divmod(remainder, 60)
                expIn = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
                await t.message.edit(content=f"Tile: {t.id} | Expires in: {expIn}")
            else:
                await t.message.edit(content=f"Tile: {t.id} | Expired")

    @update_time.before_loop
    async def before_update_time(self):
        print('waiting...')
        await self.client.wait_until_ready()
        if self.tileChannel == 0:
            print("Searching Channel")
            channel = discord.utils.get(self.client.get_all_channels(), name='tile-refresh')
            self.tileChannel = channel
            print(f"Fround channel {self.tileChannel}")

            async for msg in channel.history(limit=200):
                parsed = re.search('.*?: (.*?) \| .*: (.*)', msg.content)
                print(parsed)
                if parsed == None or len(parsed.groups()) != 2:
                    parsed = re.search('.*?: (.*?) \| .*', msg.content)
                    if parsed == None or len(parsed.groups()) != 1:
                        print(F"Parsing Error at {msg.content}")
                    else:
                        Tile.tileList.append(Tile.TileClass(parsed.group(1), 0))
                        Tile.tileList[-1].message = msg
                    #await msg.add_reaction("❌")
                else:
                    timeToSec = sum(x * int(t) for x, t in zip([3600, 60, 1], parsed.group(2).split(":")))
                    Tile.tileList.append(Tile.TileClass(parsed.group(1), timeToSec))
                    Tile.tileList[-1].message = msg


async def setup(bot):
    await bot.add_cog(MainCog(bot))
