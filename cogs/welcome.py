import discord
from discord.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFont
import io
import logging
import os

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)

# Setup intents
intents = discord.Intents.default()
intents.members = True  # Enables member join events
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 1217700740949348443  # Your Guild ID
        self.welcome_channel_id = 1247728759780413480  # Welcome channel ID
        self.default_font_path = "arial.ttf"  # Path to font
        self.known_members = set()  # For polling fallback

        # Start polling for new members as a fallback
        self.poll_new_members.start()

    def cog_unload(self):
        """Ensure tasks are stopped when the cog unloads."""
        self.poll_new_members.cancel()

    async def generate_banner(self, member):
        """Generate a welcome banner with the user's name and avatar."""
        try:
            logging.info(f"Generating banner for {member.name}...")

            # Create a blank banner
            banner = Image.new('RGB', (800, 300), color=(30, 144, 255))  # Blue background
            draw = ImageDraw.Draw(banner)

            # Load fonts
            try:
                font = ImageFont.truetype(self.default_font_path, 40)
                small_font = ImageFont.truetype(self.default_font_path, 30)
            except IOError:
                logging.warning("Font file not found, using default font.")
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()

            # Add welcome text
            text = f"Welcome, {member.name}!"
            draw.text((20, 20), text, font=font, fill="white")
            draw.text((20, 80), "We're happy to have you here!", font=small_font, fill="white")

            # Fetch the member's avatar
            if member.avatar:  # Custom avatar exists
                avatar_data = await member.avatar.read()
            else:
                logging.info("Using default avatar.")
                avatar_data = await self.bot.user.default_avatar.read()

            # Open avatar image
            avatar_image = Image.open(io.BytesIO(avatar_data)).resize((150, 150)).convert("RGBA")

            # Create a circular mask for the avatar
            mask = Image.new("L", avatar_image.size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, avatar_image.size[0], avatar_image.size[1]), fill=255)

            # Paste the avatar onto the banner with the circular mask
            banner.paste(avatar_image, (620, 75), mask)

            # Save the banner to a bytes object
            output = io.BytesIO()
            banner.save(output, format="PNG")
            output.seek(0)

            logging.info(f"Banner generated successfully for {member.name}.")
            return output
        except Exception as e:
            logging.error(f"Error generating banner for {member.name}: {e}")
            return None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handle when a member joins the server."""
        logging.info(f"New member joined: {member.name}")
        if member.guild.id == self.guild_id:
            channel = self.bot.get_channel(self.welcome_channel_id)
            if channel:
                logging.info(f"Sending welcome message in channel ID: {self.welcome_channel_id}")
                # Generate banner
                banner = await self.generate_banner(member)
                if banner:
                    try:
                        await channel.send(
                            f"🎉 Welcome to the server, {member.mention}! We're thrilled to have you join us! 🎉",
                            file=discord.File(banner, filename="welcome_banner.png")
                        )
                    except Exception as e:
                        logging.error(f"Failed to send banner for {member.name}: {e}")
                else:
                    logging.warning("Failed to generate a banner, sending text-only message.")
                    await channel.send(f"🎉 Welcome to the server, {member.mention}! 🎉")
            else:
                logging.error("Welcome channel not found.")

    @tasks.loop(seconds=30)  # Poll every 30 seconds
    async def poll_new_members(self):
        """Fallback: Poll guild members periodically to detect new users."""
        guild = self.bot.get_guild(self.guild_id)
        if guild:
            logging.info("Polling for new members...")
            current_members = {member.id for member in guild.members}
            
            # Detect new members
            new_members = current_members - self.known_members
            self.known_members = current_members  # Update known members
            
            for member_id in new_members:
                member = guild.get_member(member_id)
                if member:
                    await self.send_welcome_message(member)
        else:
            logging.error(f"Guild with ID {self.guild_id} not found.")

    async def send_welcome_message(self, member):
        """Send a fallback welcome message."""
        channel = self.bot.get_channel(self.welcome_channel_id)
        if channel:
            await channel.send(f"Welcome to the server, {member.mention}! 🎉")
        else:
            logging.error("Welcome channel not found.")

    @commands.Cog.listener()
    async def on_ready(self):
        """Initialize the known members list."""
        guild = self.bot.get_guild(self.guild_id)
        if guild:
            logging.info(f"Loading initial member list for guild: {guild.name}")
            self.known_members = {member.id for member in guild.members}

async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(Welcome(bot))

