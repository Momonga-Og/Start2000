import discord
from discord.ext import commands
import logging

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 123456789012345678  # Your guild ID here
        self.welcome_channel_id = 1247728759780413480  # Default channel for welcome messages
        self.leave_channel_id = 1247728782559809558  # Default channel for leaving messages
        self.welcome_message = "Welcome, {user.name}! We're glad to have you here!"  # Default welcome message

    def set_channel(self, channel_id):
        """Store the welcome channel ID."""
        self.welcome_channel_id = channel_id

    def set_message(self, message):
        """Store the welcome message."""
        self.welcome_message = message

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
        if member.guild.id == self.guild_id:
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
        if member.guild.id == self.guild_id:
            channel = self.bot.get_channel(self.leave_channel_id)
            if channel:
                embed = await self.create_leave_embed(member)
                await channel.send(embed=embed)
            else:
                logging.error("Leave channel not found.")

    # Slash command to set the welcome channel
    @commands.slash_command(name='welcome-channel', description='Sets the welcome channel')
    async def welcome_channel(self, ctx, channel: discord.TextChannel):
        if ctx.guild.id != self.guild_id:
            await ctx.respond(f"This command is only available in the specific server.")
            return
        
        if self.welcome_channel_id == channel.id:
            await ctx.respond(f"This channel is already the welcome channel.")
        else:
            self.set_channel(channel.id)
            await ctx.respond(f"Welcome channel set to {channel.mention}.")

    # Slash command to set the welcome message
    @commands.slash_command(name='welcome-message', description='Sets the welcome message')
    async def welcome_message(self, ctx, message: str):
        if ctx.guild.id != self.guild_id:
            await ctx.respond(f"This command is only available in the specific server.")
            return
        
        if self.welcome_message == message:
            await ctx.respond(f"This message is already set as the welcome message.")
        else:
            self.set_message(message)
            await ctx.respond("Welcome message set successfully.")

    # Slash command to test the welcome message
    @commands.slash_command(name='welcome-test', description='Sends a test welcome message')
    async def welcome_test(self, ctx):
        if ctx.guild.id != self.guild_id:
            await ctx.respond(f"This command is only available in the specific server.")
            return
        
        channel = self.bot.get_channel(self.welcome_channel_id)
        if channel:
            # Replace placeholders in the welcome message
            message = self.welcome_message
            message = message.replace("{user.name}", ctx.author.name)
            message = message.replace("{user.mention}", ctx.author.mention)
            await channel.send(message)
            await ctx.respond("Test welcome message sent.")
        else:
            await ctx.respond("Welcome channel not found.")

async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(Welcome(bot))
