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
        self.welcome_channel_id = 1247728759780413480  # Welcome channel ID for announcements
        self.leave_channel_id = 1247728782559809558  # Leave channel ID
        self.default_font_path = "arial.ttf"  # Path to the font file

    async def generate_banner(self, member):
        """Generate a welcome banner with the user's name and avatar."""
        try:
            banner = Image.new('RGB', (800, 300), color=(30, 144, 255))  # Blue background
            draw = ImageDraw.Draw(banner)

            # Load fonts
            try:
                font = ImageFont.truetype(self.default_font_path, 40)
                small_font = ImageFont.truetype(self.default_font_path, 30)
            except IOError:
                logging.error("Font file not found. Ensure 'arial.ttf' is available.")
                raise

            # Add welcome text
            text = f"Welcome, {member.name}!"
            draw.text((20, 20), text, font=font, fill="white")
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
        except Exception as e:
            logging.error(f"Error generating banner for {member.name}: {e}")
            return None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handle when a member joins the server."""
        logging.info(f"{member.name} has joined the server.")
        if member.guild.id == self.guild_id:
            channel = self.bot.get_channel(self.welcome_channel_id)
            if channel:
                # Generate banner
                banner = await self.generate_banner(member)
                if banner:
                    await channel.send(
                        f"🎉 Welcome to the server, {member.mention}! We're thrilled to have you join us! 🎉",
                        file=discord.File(banner, filename="welcome_banner.png")
                    )
                else:
                    await channel.send(f"🎉 Welcome to the server, {member.mention}! We're thrilled to have you join us! 🎉")
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

async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(Welcome(bot))
