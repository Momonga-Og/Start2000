import discord
from discord.ext import commands
import logging

# Enable logging to help with debugging
logging.basicConfig(level=logging.INFO)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channel_id = 1247728759780413480  # Channel for welcoming users
        self.leave_channel_id = 1247728782559809558  # Channel for user departures

    async def create_welcome_embed(self, member):
        """Create an embed message to welcome a new user."""
        embed = discord.Embed(
            title="Welcome to the Server!",
            description=f"Bienvenue {member.mention} dans le serveur!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="Username", value=member.name, inline=True)
        embed.add_field(name="User ID", value=member.id, inline=True)
        embed.set_footer(text="Nous espérons que vous passerez un bon moment ici !")
        return embed

    async def create_leave_embed(self, member):
        """Create an embed message to announce when a user leaves."""
        embed = discord.Embed(
            title="A user has left the server",
            description=f"Au revoir {member.mention}, tu vas nous manquer !",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="Username", value=member.name, inline=True)
        embed.add_field(name="User ID", value=member.id, inline=True)
        embed.set_footer(text="On espère te revoir bientôt !")
        return embed

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handle when a member joins the server."""
        logging.info(f"{member.name} has joined the server.")
        
        # Get the welcome channel by ID
        channel = self.bot.get_channel(self.welcome_channel_id)
        if channel:
            embed = await self.create_welcome_embed(member)
            await channel.send(embed=embed)
        else:
            logging.error("Welcome channel not found.")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Handle when a member leaves the server."""
        logging.info(f"{member.name} has left the server.")
        
        # Get the leave channel by ID
        channel = self.bot.get_channel(self.leave_channel_id)
        if channel:
            embed = await self.create_leave_embed(member)
            await channel.send(embed=embed)
        else:
            logging.error("Leave channel not found.")

async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(Welcome(bot))
