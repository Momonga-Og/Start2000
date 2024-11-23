import discord
from discord.ext import commands
import random

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channel_id = 1247728759780413480  # Welcome channel ID
        self.leave_channel_id = 1247728782559809558   # Leaving channel ID
        self.welcome_messages = [
            "Bienvenue sur le serveur, {name} ! Nous sommes ravis de t'accueillir parmi nous.",
            "Salut {name}, bienvenue ! Amuse-toi bien ici !",
            "Bienvenue dans notre belle communauté, {name} !",
        ]
        self.leave_messages = [
            "Au revoir, {name}. Nous espérons te revoir bientôt !",
            "C'est triste de te voir partir, {name}. À la prochaine !",
            "Adieu, {name}. Bonne continuation !"
        ]

    async def create_welcome_embed(self, member):
        """Create the embed for a user joining."""
        embed = discord.Embed(
            title="Bienvenue sur le serveur !",
            description=f"{random.choice(self.welcome_messages).format(name=member.name)}",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Nous sommes maintenant {len(member.guild.members)} membres !")
        return embed

    async def create_leave_embed(self, member):
        """Create the embed for a user leaving."""
        embed = discord.Embed(
            title="Un membre nous quitte...",
            description=f"{random.choice(self.leave_messages).format(name=member.name)}",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Il nous reste {len(member.guild.members)} membres.")
        return embed

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """When a member joins the server."""
        channel = self.bot.get_channel(self.welcome_channel_id)
        if channel:
            embed = await self.create_welcome_embed(member)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """When a member leaves the server."""
        channel = self.bot.get_channel(self.leave_channel_id)
        if channel:
            embed = await self.create_leave_embed(member)
            await channel.send(embed=embed)

    async def cog_unload(self):
        """Ensure bot disconnects properly."""
        pass

async def setup(bot):
    await bot.add_cog(Welcome(bot))
