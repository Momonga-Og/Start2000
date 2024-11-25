import discord
from discord.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFont
import io
import logging

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.members = True  # Enables on_member_join event
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
        logging.info(f"Event triggered: {member.name} joined the server.")
        if member.guild.id == self.guild_id:
            logging.info(f"Member joined guild with ID: {self.guild_id}.")
            channel = self.bot.get_channel(self.welcome_channel_id)
            if channel:
                logging.info(f"Sending welcome message to channel ID: {self.welcome_channel_id}.")
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
    async def on_message(self, message):
        """Fallback: Detect a new user when they send their first message."""
        if message.author.bot:
            return  # Ignore bots
        
        guild = message.guild
        if guild and guild.id == self.guild_id:
            member = message.author
            if len(member.roles) == 1:  # New users often have only the default role
                channel = self.bot.get_channel(self.welcome_channel_id)
                if channel:
                    await channel.send(f"Welcome to the server, {member.mention}! 🎉")
                    logging.info(f"Detected new member: {member.name}")
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

