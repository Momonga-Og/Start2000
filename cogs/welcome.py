import discord
from discord.ext import commands
import logging

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 1217700740949348443  # Your guild ID here
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

    @commands.Cog.listener()
    async def on_message(self, message):
        """Respond to messages in a specific channel."""
        if message.author.bot:
            return  # Ignore messages from bots

        # Example response logic: Reply if a user says "hello"
        if "hello" in message.content.lower():
            await message.channel.send(f"Hello, {message.author.mention}! Welcome to the server!")

    @discord.app_commands.command(name='welcome-channel', description='Sets the welcome channel')
    async def welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if interaction.guild.id != self.guild_id:
            await interaction.response.send_message("This command is only available in the specific server.")
            return
        
        if self.welcome_channel_id == channel.id:
            await interaction.response.send_message("This channel is already the welcome channel.")
        else:
            self.set_channel(channel.id)
            await interaction.response.send_message(f"Welcome channel set to {channel.mention}.")

    @discord.app_commands.command(name='welcome-message', description='Sets the welcome message')
    async def welcome_message(self, interaction: discord.Interaction, message: str):
        if interaction.guild.id != self.guild_id:
            await interaction.response.send_message("This command is only available in the specific server.")
            return
        
        if self.welcome_message == message:
            await interaction.response.send_message("This message is already set as the welcome message.")
        else:
            self.set_message(message)
            await interaction.response.send_message("Welcome message set successfully.")

    @discord.app_commands.command(name='welcome-test', description='Sends a test welcome message')
    async def welcome_test(self, interaction: discord.Interaction):
        if interaction.guild.id != self.guild_id:
            await interaction.response.send_message("This command is only available in the specific server.")
            return
        
        channel = self.bot.get_channel(self.welcome_channel_id)
        if channel:
            message = self.welcome_message
            message = message.replace("{user.name}", interaction.user.name)
            message = message.replace("{user.mention}", interaction.user.mention)
            await channel.send(message)
            await interaction.response.send_message("Test welcome message sent.")
        else:
            await interaction.response.send_message("Welcome channel not found.")

async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(Welcome(bot))
