import discord
from discord.ext import commands
from discord.ui import View, Button
from io import BytesIO

class PercoAttack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots or messages without attachments
        if message.author.bot or not message.attachments:
            return

        # Check if the message is sent in the specific channel
        if message.channel.id == 1247728782559809558:
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith("image/"):
                    # Download the image
                    image_data = await attachment.read()
                    image_file = BytesIO(image_data)
                    image_file.seek(0)

                    # Repost the image with buttons
                    file = discord.File(fp=image_file, filename=attachment.filename)
                    view = PercoView()
                    reposted_message = await message.channel.send(
                        file=file,
                        content=f"{message.author.mention} a posté une image :",
                        view=view
                    )

                    # Delete the user's original message
                    await message.delete()
                    view.message = reposted_message  # Store the reposted message for later updates

class PercoView(View):
    def __init__(self):
        super().__init__()
        self.claimed = False  # Tracks whether one of the buttons was clicked
        self.message = None  # To store the message this view is attached to

    @discord.ui.button(label="Réclamé", style=discord.ButtonStyle.green)
    async def claimed_button(self, interaction: discord.Interaction, button: Button):
        if self.claimed:
            await interaction.response.send_message("Cette action a déjà été effectuée !", ephemeral=True)
        else:
            self.claimed = True
            self.update_buttons("Réclamé ✔", discord.ButtonStyle.green)
            await interaction.response.send_message(f"{interaction.user.mention} a réclamé le perco.", ephemeral=False)
            await interaction.message.edit(view=self)  # Update the message

    @discord.ui.button(label="Pas encore réclamé", style=discord.ButtonStyle.red)
    async def not_claimed_button(self, interaction: discord.Interaction, button: Button):
        if self.claimed:
            await interaction.response.send_message("Cette action a déjà été effectuée !", ephemeral=True)
        else:
            self.claimed = True
            self.update_buttons("Pas encore réclamé ❌", discord.ButtonStyle.red)
            await interaction.response.send_message(f"{interaction.user.mention} n'a pas réclamé le perco.", ephemeral=False)
            await interaction.message.edit(view=self)  # Update the message

    def update_buttons(self, new_label, new_style):
        """Replaces the buttons with updated ones."""
        self.clear_items()  # Remove all existing buttons
        self.add_item(Button(label=new_label, style=new_style, disabled=True))  # Add the updated button

# Set up the cog
async def setup(bot):
    await bot.add_cog(PercoAttack(bot))
