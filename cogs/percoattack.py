import discord
from discord.ext import commands
from discord.ui import View, Button
from io import BytesIO
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB setup using environment variable
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MongoDB URI not found in environment variables. Check your .env file.")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["discord_bot"]  # Database name
collection = db["perco_messages"]  # Collection name


class PercoAttack(commands.Cog):
    """Cog for handling Perco attack features."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Recreate views for persistent messages on bot startup."""
        logger.info("Bot is ready. Recreating views from database...")
        messages = collection.find({"claimed": {"$exists": True}})
        for message_data in messages:
            channel = self.bot.get_channel(message_data["channel_id"])
            if channel:
                try:
                    logger.info(f"Recreating view for message {message_data['message_id']} in channel {message_data['channel_id']}")
                    message = await channel.fetch_message(message_data["message_id"])
                    view = PercoView(message_data["claimed"])
                    await message.edit(view=view)
                except discord.NotFound:
                    logger.warning(f"Message {message_data['message_id']} not found. Removing from database.")
                    collection.delete_one({"message_id": message_data["message_id"]})

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle messages containing images in a specific channel."""
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

                        # Save the message state in MongoDB
                        collection.insert_one({
                            "message_id": reposted_message.id,
                            "channel_id": reposted_message.channel.id,
                            "claimed": False
                        })
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
    """Custom view for handling Perco attack buttons."""

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

        # Update the state in the MongoDB
        collection.update_one(
            {"message_id": interaction.message.id},
            {"$set": {"claimed": True}}
        )
        logger.info(f"Updated message {interaction.message.id} to claimed in database.")

        await interaction.response.send_message(f"{interaction.user.mention} a réclamé le perco.", ephemeral=False)
        await interaction.message.edit(view=self)


# Set up the cog
async def setup(bot):
    await bot.add_cog(PercoAttack(bot))
