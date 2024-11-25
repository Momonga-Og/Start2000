import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
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

    async def generate_banner(self, member):
        """Generate a welcome banner with the user's name and avatar."""
        # Load or create a base image for the banner
        banner = Image.new('RGB', (800, 300), color=(30, 144, 255))  # Blue background
        draw = ImageDraw.Draw(banner)

        # Load a font (you can replace 'arial.ttf' with a path to your preferred font)
        font = ImageFont.truetype("arial.ttf", 40)  # Adjust size as needed
        small_font = ImageFont.truetype("arial.ttf", 30)

        # Add welcome text
        text = f"Welcome, {member.name}!"
        draw.text((20, 20), text, font=font, fill="white")

        # Add server info
        draw.text((20, 80), f"We're happy to have you here!", font=small_font, fill="white")

        # Download the member's avatar
        avatar_data = await member.avatar.read()
        avatar_image = Image.open(io.BytesIO(avatar_data)).resize((150, 150))

        # Paste the avatar onto the banner
        banner.paste(avatar_image, (620, 75))

        # Save banner to a bytes object
        output = io.BytesIO()
        banner.save(output, format="PNG")
        output.seek(0)
        return output

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handle when a member joins the server."""
        logging.info(f"{member.name} has joined the server.")
        if member.guild.id == self.guild_id:
            channel = self.bot.get_channel(self.welcome_channel_id)
            if channel:
                banner = await self.generate_banner(member)
                await channel.send(file=discord.File(banner, filename="welcome_banner.png"))
            else:
                logging.error("Welcome channel not found.")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Handle when a member leaves the server."""
        logging.info(f"{member.name} has left the server.")
        if member.guild.id == self.guild_id:
            channel = self.bot.get_channel(self.leave_channel_id)
            if channel:
                await channel.send(f"{member.name} has left the server. Goodbye!")
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

async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(Welcome(bot))
