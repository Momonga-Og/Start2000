import discord
from discord.ext import commands
from discord.ui import View, Button
from io import BytesIO
import sqlite3

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
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT message_id, channel_id, claimed FROM perco_messages")
        rows = cursor.fetchall()
        conn.close()

        for message_id, channel_id, claimed in rows:
            channel = self.bot.get_channel(channel_id)
            if channel:
                try:
                    message = await channel.fetch_message(message_id)
                    view = PercoView(bool(claimed))
                    await message.edit(view=view)
                except discord.NotFound:
                    # If the message no longer exists, remove it from the database
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

                    except discord.errors.NotFound:
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
        if self.claimed:
            # If already claimed, disable the button
            self.add_item(Button(label="Réclamé ✔", style=discord.ButtonStyle.green, disabled=True))
        else:
            # If not claimed, add the interactive button
            self.add_item(self.create_claim_button())

    def create_claim_button(self):
        """Create the claim button."""
        return Button(label="Réclamé", style=discord.ButtonStyle.green, callback=self.claimed_button)

    async def claimed_button(self, interaction: discord.Interaction):
        self.claimed = True
        button = self.children[0]  # Access the button
        button.label = "Réclamé ✔"
        button.disabled = True

        # Update the state in the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE perco_messages SET claimed = 1 WHERE message_id = ?",
            (interaction.message.id,)
        )
        conn.commit()
        conn.close()

        await interaction.response.send_message(f"{interaction.user.mention} a réclamé le perco.", ephemeral=False)
        await interaction.message.edit(view=self)

# Set up the cog
async def setup(bot):
    await bot.add_cog(PercoAttack(bot))
