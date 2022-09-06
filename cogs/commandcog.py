import asyncio
import sys
import traceback
from datetime import datetime, timedelta

import discord
from discord.ext import tasks, commands

import Tile


class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_time.start()
        self.tileChannel = None

    def cog_unload(self):
        self.update_time.cancel()

    @commands.group(invoke_without_command=True)
    async def tile(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid sub command passed...')

    @commands.command()
    async def pingCommand(self, ctx):
        await ctx.send('pong')

    @tile.command()
    async def remove(self, ctx, argument):
        ##TileList.remove(Tile(argument))
        await ctx.send(f'notImplementedException()')

    @tile.command()
    async def list(self, ctx):
        for t in Tile.TileList:
            await ctx.send(f'Tile: {t.id}')

    @tile.command()
    async def add(self, ctx, argument):
        Tile.TileList.append(Tile.TileClass(argument, Tile.TileType.EMPTY, timedelta(seconds=0)))
        await ctx.send(f'Adding Tile: {argument}')

    @tile.command()
    async def setSec(self, ctx, argument, argument2):
        found = False
        for t in Tile.TileList:
            if t.id == argument:
                found = True
                t.refreshTimer = datetime.now() + timedelta(seconds=argument2)
                await ctx.send(f'Setting Time of Tile {t.id} to {t.refreshTimer}')
        if not found:
            await ctx.send(f'Couldnt find Tile with ID {argument}')

    @tile.command()
    async def set(self, ctx, argument, hours: int, minutes: int, seconds: int):
        found = False
        for t in Tile.TileList:
            if t.id == argument:
                found = True
                t.refreshTimer = datetime.now() + timedelta(hours=hours, minutes=minutes, seconds=seconds)
                t.lastUpdate = datetime.min
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
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id != self.bot.user.id and self.tileChannel.id == payload.channel_id:
            msg_id = payload.message_id
            emoji = payload.emoji
            channel = self.tileChannel
            message = await channel.fetch_message(payload.message_id)

            user = self.bot.get_user(payload.user_id)
            if not user:
                user = await self.bot.fetch_user(payload.user_id)
            # instead of reaction we should use payload.emoji
            # for example:
            if str(emoji) == "♻️":
                t = await Tile.findByMSGID(msg_id)
                print(f"refreshing tile: {t.id}")
                t.refreshTimer = datetime.now() + timedelta(hours=28)
                t.lastUpdate = datetime.now()
                await t.message.edit(content=await Tile.formateMSG(t))
                await message.remove_reaction(payload.emoji, user)
                await asyncio.sleep(2)
            elif str(emoji) == "a":
                print(str(emoji))
            else:
                print(str(emoji))

    @tasks.loop(seconds=999999)
    async def update_time(self):
        self.update_time.stop()

    @update_time.before_loop
    async def before_update_time(self):
        print('waiting...')
        await self.bot.wait_until_ready()
        maincog = self.bot.get_cog('MainCog')
        if maincog.tileChannel is None:
            print("Searching Channel cmd")
            channel = discord.utils.get(self.bot.get_all_channels(), name='tile-refresh')
            self.tileChannel = channel
            print(f"Found channel {self.tileChannel}")
        else:
            self.tileChannel = maincog.tileChannel
            print(f"Got channel {self.tileChannel} from main cog")

async def setup(bot):
    await bot.add_cog(CommandCog(bot))
