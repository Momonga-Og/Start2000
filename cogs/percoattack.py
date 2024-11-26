import discord
from discord.ext import commands
from discord.ui import View, Button
from io import BytesIO
import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DB_PATH = "conversation_history.db"

def setup_database():
    """Create the necessary table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS perco_messages (
        message_id INTEGER PRIMARY KEY,
        channel_id INTEGER NOT NULL,
        claimed INTEGER NOT NULL DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

setup_database()

class PercoAttack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Recreate views for persistent messages on bot startup."""
        logger.info("Bot is ready. Recreating views from database...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT message_id, channel_id, claimed FROM perco_messages")
        rows = cursor.fetchall()
        conn.close()

        for message_id, channel_id, claimed in rows:
            channel = self.bot.get_channel(channel_id)
            if channel:
                try:
                    logger.info(f"Recreating view for message {message_id} in channel {channel_id}")
                    message = await channel.fetch_message(message_id)
                    view = PercoView(bool(claimed))
                    await message.edit(view=view)
                except discord.NotFound:
                    logger.warning(f"Message {message_id} not found. Removing from database.")
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM perco_messages WHERE message_id = ?", (message_id,))
                    conn.commit()
                    conn.close()

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots or messages without attachments
        if message.author.bot or not message.attachments:
            return

        # Check if the message is sent in the specific channel
        if message.channel.id == 1247728782559809558:  # Replace with your channel ID
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith("image/"):
                    try:
                        # Attempt to download the image
                        image_data = await attachment.read()
                        image_file = BytesIO(image_data)
                        image_file.seek(0)

                        # Create a button for this specific image
                        view = PercoView()
                        file = discord.File(fp=image_file, filename=attachment.filename)
                        reposted_message = await message.channel.send(
                            file=file,
                            content=f"{message.author.mention} a posté une image :",
                            view=view
                        )

                        # Save the message state in the database
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO perco_messages (message_id, channel_id, claimed) VALUES (?, ?, ?)",
                            (reposted_message.id, reposted_message.channel.id, 0)
                        )
                        conn.commit()
                        conn.close()
                        logger.info(f"Saved message {reposted_message.id} in channel {reposted_message.channel.id} to database.")

                    except discord.errors.NotFound:
                        logger.error(f"Failed to download attachment {attachment.filename}.")
                        await message.channel.send(
                            f"Erreur : Impossible de télécharger l'image `{attachment.filename}`. Lien non valide ou expiré.",
                            delete_after=10
                        )
            # Delete the user's original message
            await message.delete()

class PercoView(View):
    def __init__(self, claimed=False):
        super().__init__()
        self.claimed = claimed
        self.button = Button(label="Réclamé", style=discord.ButtonStyle.green)
        self.add_item(self.button)

        # Attach callback dynamically based on the claimed state
        if claimed:
            self.button.label = "Réclamé ✔"
            self.button.disabled = True
        else:
            self.button.callback = self.claimed_button  # Set the callback for unclaimed button

    async def claimed_button(self, interaction: discord.Interaction):
        """Callback for the claimed button."""
        self.claimed = True
        self.button.label = "Réclamé ✔"
        self.button.disabled = True

        # Update the state in the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE perco_messages SET claimed = 1 WHERE message_id = ?",
            (interaction.message.id,)
        )
        conn.commit()
        conn.close()
        logger.info(f"Updated message {interaction.message.id} to claimed in database.")

        await interaction.response.send_message(f"{interaction.user.mention} a réclamé le perco.", ephemeral=False)
        await interaction.message.edit(view=self)

# Set up the cog
async def setup(bot):
    await bot.add_cog(PercoAttack(bot))
