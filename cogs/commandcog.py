import asyncio
import sys
import traceback
from datetime import datetime, timedelta

import discord
from discord.ext import commands

import TileSQL

class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.db = None
        self.bot = bot
        self.tileChannel = None
        self.maincog = None

    def cog_unload(self):
        self.bot = None

    @commands.command()
    async def pingCommand(self, ctx):
        await ctx.send('pong')

    @commands.command()
    async def fillTile(self, ctx):
        self.maincog.TileList = []
        for x in ("DAA", "DBA", "DCA", "DDA", "DAB", "DEA", "DFA", "DBB", "DCB", "DGA", "EGA", "DDB", "DAC", "DEB", "CFA", "EEA", "DFB", "DBC", "DCC", "CFB", "CDA", "ECA", "EEB", "DDC", "DAD", "DEC", "CDB", "CBA", "EAA", "ECB", "EEC", "DBD", "DCD", "CDC", "CBB", "CAA", "EAB", "ECC", "DDD", "DAE", "CDD", "CBC", "CAB", "EBA", "EAC", "ECD", "DBE", "DCE", "CBD", "CAC", "CCA", "EBB", "EAD", "ECE", "DAF", "CBE", "CAD", "CCB", "EDA", "EBC", "EAE", "DBF", "CBF", "CAE", "CCC", "CEA", "EDB", "EBD", "EAF", "DAG", "CAF", "CCD", "CEB", "EFA", "EDC", "EBE", "EAG", "CAG", "CCE", "CEC", "CGA", "EFB", "EDD", "EBF", "MRX", "BBF", "BDD", "BFB", "FGA", "FEC", "FCE", "FAH", "BAG", "BBE", "BDC", "BFA", "FEB", "FCD", "FAF", "AAG", "DAF", "BBD", "BDB", "FEA", "FCC", "FAE", "FBF", "ABF", "BAE", "BBC", "BDA", "FCB", "FAD", "FBE", "AAF", "BCE", "BAD", "BBB", "FCA", "FAC", "FBD", "ACA", "ABE", "BCD", "BAC", "BBA", "FAB", "FBC", "FDD", "AAE", "ADD", "BCC", "BAB", "FAA", "FBB", "FDC", "ACD", "ABD", "BEC", "BCB", "BAA", "FBA", "FDB", "AEC", "AAD", "ADC", "BEB", "BCA", "FDA", "FFB", "ACC", "ABC", "AFB", "BEA", "FFA", "AEB", "AAC", "ADB", "BGA", "AGA", "ACB", "ABB", "AFA", "AEA", "AAB", "ADA", "ACA", "ABA", "AAA", ):
            self.maincog.TileList.append(TileSQL.TileClass(self.db, x))
        await TileSQL.updateTileList(self.db, self.maincog.TileList)
        await ctx.send('Reseted list')

    @commands.group(invoke_without_command=True)
    async def tt(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid sub command passed...')

    @tt.command()
    async def Empty(self, ctx, tilecode):
        found = False
        for t in self.maincog.TileList:
            if t.id == tilecode:
                found = True
                t.type = TileSQL.TileType.EMPTY
                await TileSQL.createOrUpdateNewTile(self.db, t)
                await ctx.send(f'Setting Type of Tile {t.id} to Empty')
        if not found:
            await ctx.send(f'Couldnt find Tile with ID {tilecode}')

    @tt.command()
    async def Relic(self, ctx, tilecode):
        found = False
        for t in self.maincog.TileList:
            if t.id == tilecode:
                found = True
                t.type = TileSQL.TileType.RELIC
                await TileSQL.createOrUpdateNewTile(self.db, t)
                await ctx.send(f'Setting Type of Tile {t.id} to Relic')
        if not found:
            await ctx.send(f'Couldnt find Tile with ID {tilecode}')

    @tt.command()
    async def Banner(self, ctx, tilecode):
        found = False
        for t in self.maincog.TileList:
            if t.id == tilecode:
                found = True
                t.type = TileSQL.TileType.BANNER
                await TileSQL.createOrUpdateNewTile(self.db, t)
                await ctx.send(f'Setting Type of Tile {t.id} to Banner')
        if not found:
            await ctx.send(f'Couldnt find Tile with ID {tilecode}')

    @tt.command()
    async def Ours(self, ctx, tilecode):
        found = False
        for t in self.maincog.TileList:
            if t.id == tilecode:
                found = True
                await TileSQL.createOrUpdateNewTile(self.db, t)
                await ctx.send(f'Setting Type of Tile {t.id} to Banner')
        if not found:
            await ctx.send(f'Couldnt find Tile with ID {tilecode}')

    @commands.group(invoke_without_command=True)
    async def t(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid sub command passed...')

    @t.command()
    async def rmmsgid(self, ctx, argument):
        tile = await TileSQL.findByTileCode(self.db, argument)
        tile.msg_id = None
        TileSQL.createOrUpdateNewTile(self.db, tile)
        await ctx.send(f'notImplementedException()')

    @t.command()
    async def remove(self, ctx, argument):
        await TileSQL.deleteTile(self.db, argument)
        await ctx.send(f'removed tile {argument}')

    @t.command()
    async def list(self, ctx):
        rt = ""
        for t in self.maincog.TileList:
            rt += f'{t.toString()}\r\n\r\n'
        await ctx.send(rt)

    @t.command()
    async def add(self, ctx, t_id):
        self.maincog.TileList.append(TileSQL.TileClass(self.db, t_id))
        await ctx.send(f'Adding Tile: {t_id}')

    @t.command()
    async def commit(self, ctx):
        await TileSQL.updateTileList(self.db, self.maincog.TileList)
        await ctx.send(f'Committing TileList..')

    @t.command()
    async def update(self, ctx):
        tl = await TileSQL.getAllTiles(self.db, self.tileChannel)
        self.maincog.TileList = tl
        await ctx.send(f'Getting TileList..')

    @t.command()
    async def setSec(self, ctx, argument, argument2):
        found = False
        for t in self.maincog.TileList:
            if t.id == argument:
                found = True
                t.refreshTimer = datetime.now() + timedelta(seconds=argument2)
                await TileSQL.createOrUpdateNewTile(self.db, t)
                await ctx.send(f'Setting Time of Tile {t.id} to {t.refreshTimer}')
        if not found:
            await ctx.send(f'Couldnt find Tile with ID {argument}')

    @t.command()
    async def set(self, ctx, argument, hours: int, minutes: int, seconds: int):
        found = False
        for t in self.maincog.TileList:
            if t.id == argument:
                found = True
                t.refreshTimer = datetime.now() + timedelta(hours=hours, minutes=minutes, seconds=seconds)
                t.lastUpdate = datetime.min
                await TileSQL.createOrUpdateNewTile(self.db, t)
                await ctx.send(f'Setting Time of Tile {t.id} to {t.refreshTimer}')
        if not found:
            await ctx.send(f'Couldnt find Tile with ID {argument}')

    @commands.Cog.listener()
    async def on_ready(self):
        print('waiting...')
        await self.bot.wait_until_ready()
        self.maincog = self.bot.get_cog('MainCog')
        if self.maincog.tileChannel is None:
            print("Searching Channel cmd")
            channel = discord.utils.get(self.bot.get_all_channels(), name='tile-refresh')
            self.tileChannel = channel
            print(f"Found channel {self.tileChannel}")
        else:
            self.tileChannel = self.maincog.tileChannel
            print(f"Got channel {self.tileChannel} from main cog")

        while self.maincog.db is None:
            await asyncio.sleep(delay=1)
        self.db = self.maincog.db

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
                try:
                    await message.remove_reaction(payload.emoji, user)
                    t = await TileSQL.findByMSGID(self.db, msg_id)
                except BaseException as err:
                    print(f"Unexpected {err=}, {type(err)=}")

                if t is None:
                    print("couldn't find Tile")
                else:
                    if t.message is None:
                        try:
                            t.message = await self.tileChannel.fetch_message(t.msg_id)
                        except discord.NotFound:
                            t.message = await self.tileChannel.send(f"Tile: {t.id}")
                            t.msg_id = t.message.id
                            await t.message.add_reaction("♻️")

                    print(f"refreshing tile: {t.id}")
                    t.refreshTimer = datetime.now() + timedelta(hours=28)
                    t.shouldUpdate = False
                    t.lastUpdate = datetime.now()
                    await TileSQL.createOrUpdateNewTile(self.db, t)
                    await t.message.edit(content=await TileSQL.formateMSG(t))
                    await asyncio.sleep(1)
            elif str(emoji) == "a":
                print(str(emoji))
            else:
                print(str(emoji))

async def setup(bot):
    await bot.add_cog(CommandCog(bot))
