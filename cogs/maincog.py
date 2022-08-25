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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        print(message.content)

    @tasks.loop(seconds=5)
    async def update_time(self):
        for t in Tile.tileList:
            if t.message == 0:
                t.message = await self.tileChannel.send(f"Tile: {t.id}")
                await t.message.add_reaction("♻️")

            cache_msg = await t.message.channel.fetch_message(t.message.id)
            if any(reaction.emoji == "♻️" and reaction.count > 1 for reaction in cache_msg.reactions):
                t.refreshTimer = 28*60*60 + 5
                await cache_msg.clear_reactions()
                await t.message.add_reaction("♻️")

            if t.refreshTimer > 1:
                t.refreshTimer -= 5
                s = t.refreshTimer
                hours, remainder = divmod(s, 3600)
                minutes, seconds = divmod(remainder, 60)
                expIn = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
                await t.message.edit(content=f"Tile: {t.id} | Expires in: {expIn}")
            else :
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
                    print(F"Parsing Error at {msg.content}")
                    await msg.add_reaction("❌")
                else:
                    timeToSec = sum(x * int(t) for x, t in zip([3600, 60, 1], parsed.group(2).split(":")))
                    Tile.tileList.append(Tile.TileClass(parsed.group(1), timeToSec))
                    Tile.tileList[-1].message = msg


async def setup(bot):
    await bot.add_cog(MainCog(bot))
