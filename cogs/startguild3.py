# startguild3.py
# This script initializes the bot, sets up the cog, and manages events like on_ready.

import discord
from discord.ext import commands
from startguild1 import GUILD_ID, PING_DEF_CHANNEL_ID
from startguild2 import GuildPingView


class StartGuildCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def ensure_panel(self):
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            print("Guild not found. Check the GUILD_ID.")
            return

        channel = guild.get_channel(PING_DEF_CHANNEL_ID)
        if not channel:
            print("Ping definition channel not found. Check the PING_DEF_CHANNEL_ID.")
            return

        view = GuildPingView(self.bot)
        message_content = "Cliquez sur le logo de votre guilde pour envoyer une alerte DEF !"

        async for message in channel.history(limit=50):
            if message.pinned and message.author == self.bot.user:
                await message.edit(content=message_content, view=view)
                print("Panel updated.")
                return

        new_message = await channel.send(content=message_content, view=view)
        await new_message.pin()
        print("Panel created and pinned.")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} is ready!")
        await self.ensure_panel()


async def setup(bot: commands.Bot):
    await bot.add_cog(StartGuildCog(bot))
