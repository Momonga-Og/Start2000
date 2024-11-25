import discord
from discord.ext import commands
from discord.ui import View, Button

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
                    image = await attachment.read()
                    # Repost the image with buttons
                    file = discord.File(fp=image, filename=attachment.filename)
                    view = PercoView()
                    await message.channel.send(file=file, content=f"{message.author.mention} a posté une image :", view=view)

class PercoView(View):
    def __init__(self):
        super().__init__()
        self.claimed = False  # Tracks whether one of the buttons was clicked

    @discord.ui.button(label="Réclamé", style=discord.ButtonStyle.green)
    async def claimed_button(self, button: Button, interaction: discord.Interaction):
        if self.claimed:
            await interaction.response.send_message("Cette action a déjà été effectuée !", ephemeral=True)
        else:
            self.claimed = True
            await interaction.response.send_message(f"{interaction.user.mention} a réclamé le perco.", ephemeral=False)
            self.disable_buttons()
            await interaction.message.edit(view=self)

    @discord.ui.button(label="Pas encore réclamé", style=discord.ButtonStyle.red)
    async def not_claimed_button(self, button: Button, interaction: discord.Interaction):
        if self.claimed:
            await interaction.response.send_message("Cette action a déjà été effectuée !", ephemeral=True)
        else:
            self.claimed = True
            await interaction.response.send_message(f"{interaction.user.mention} n'a pas réclamé le perco.", ephemeral=False)
            self.disable_buttons()
            await interaction.message.edit(view=self)

    def disable_buttons(self):
        """Disable all buttons after one is clicked."""
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True

# Set up the cog
def setup(bot):
    bot.add_cog(PercoAttack(bot))
