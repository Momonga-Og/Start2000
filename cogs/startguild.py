import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import random

# Configuration
GUILD_ID = 1217700740949348443  # Replace with your guild ID
PING_DEF_CHANNEL_ID = 1247706162317758597  # Replace with your ping channel ID
ALERTE_DEF_CHANNEL_ID = 1247728738326679583  # Replace with your alert channel ID

# Guild emojis with IDs and corresponding role IDs
GUILD_EMOJIS_ROLES = {
    "Darkness": {
        "emoji": "🌑",
        "role_id": 1244077334668116050,
    },
    "GTO": {
        "emoji": "🔥",
        "role_id": 1244077334668116050,
    },
    "Aversion": {
        "emoji": "💀",
        "role_id": 1244077334668116050,
    },
    "Bonnebuche": {
        "emoji": "🍞",
        "role_id": 1244077334668116050,
    },
    "LMDF": {
        "emoji": "💪",
        "role_id": 1244077334668116050,
    },
    "Notorious": {
        "emoji": "⚡",
        "role_id": 1244077334668116050,
    },
    "Percophile": {
        "emoji": "🎶",
        "role_id": 1244077334668116050,
    },
    "Tilisquad": {
        "emoji": "👑",
        "role_id": 1244077334668116050,
    },
}

# French alert messages
ALERT_MESSAGES = [
    "🚨 {role} Alerte DEF ! Connectez-vous maintenant !",
    "⚔️ {role}, il est temps de défendre !",
    "🛡️ {role} Défendez votre guilde !",
    "💥 {role} est attaquée ! Rejoignez la défense !",
    "⚠️ {role}, mobilisez votre équipe pour défendre !",
]


class NoteModal(Modal):
    def __init__(self, message: discord.Message):
        super().__init__(title="Ajouter une note")
        self.message = message

        self.note_input = TextInput(
            label="Votre note",
            placeholder="Ajoutez des détails sur l'alerte (nom de la guilde attaquante, heure, etc.)",
            max_length=100,
            style=discord.TextStyle.paragraph,
        )
        self.add_item(self.note_input)

    async def on_submit(self, interaction: discord.Interaction):
        # Retrieve the original embed and append the note
        embed = self.message.embeds[0]
        existing_notes = embed.fields[0].value if embed.fields else "Aucune note."
        updated_notes = (
            f"{existing_notes}\n- **{interaction.user.display_name}**: {self.note_input.value.strip()}"
        )

        # Update the embed with the new note
        embed.clear_fields()
        embed.add_field(name="📝 Notes", value=updated_notes, inline=False)

        await self.message.edit(embed=embed)
        await interaction.response.send_message("Votre note a été ajoutée avec succès !", ephemeral=True)


class AddNoteView(View):
    def __init__(self, bot: commands.Bot, alert_message: discord.Message):
        super().__init__()
        self.bot = bot
        self.alert_message = alert_message
        self.won_button_clicked = False
        self.lost_button_clicked = False

        self.add_note_button = Button(
            label="Ajouter une note",
            style=discord.ButtonStyle.secondary,
            emoji="📝"
        )
        self.add_note_button.callback = self.add_note_callback
        self.add_item(self.add_note_button)

        self.won_button = Button(
            label="Gagné",
            style=discord.ButtonStyle.success,
            emoji="✅"
        )
        self.won_button.callback = self.won_callback
        self.add_item(self.won_button)

        self.lost_button = Button(
            label="Perdu",
            style=discord.ButtonStyle.danger,
            emoji="❌"
        )
        self.lost_button.callback = self.lost_callback
        self.add_item(self.lost_button)

    async def add_note_callback(self, interaction: discord.Interaction):
        # Check if the user can interact with this
        if interaction.channel_id != ALERTE_DEF_CHANNEL_ID:
            await interaction.response.send_message("Vous ne pouvez pas ajouter de note ici.", ephemeral=True)
            return

        modal = NoteModal(self.alert_message)
        await interaction.response.send_modal(modal)

    async def won_callback(self, interaction: discord.Interaction):
        if self.won_button_clicked:
            await interaction.response.send_message("Ce bouton a déjà été cliqué.", ephemeral=True)
            return

        # Mark the alert as won
        embed = self.alert_message.embeds[0]
        embed.color = discord.Color.green()
        embed.set_footer(text="Victoire !")
        await self.alert_message.edit(embed=embed)

        # Disable the buttons after clicking
        self.won_button.disabled = True
        self.lost_button.disabled = True
        await self.alert_message.edit(view=self)

        self.won_button_clicked = True
        await interaction.response.send_message("L'alerte est marquée comme gagnée.", ephemeral=True)

    async def lost_callback(self, interaction: discord.Interaction):
        if self.lost_button_clicked:
            await interaction.response.send_message("Ce bouton a déjà été cliqué.", ephemeral=True)
            return

        # Mark the alert as lost
        embed = self.alert_message.embeds[0]
        embed.color = discord.Color.red()
        embed.set_footer(text="Défaite !")
        await self.alert_message.edit(embed=embed)

        # Disable the buttons after clicking
        self.won_button.disabled = True
        self.lost_button.disabled = True
        await self.alert_message.edit(view=self)

        self.lost_button_clicked = True
        await interaction.response.send_message("L'alerte est marquée comme perdue.", ephemeral=True)


class GuildPingView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        for guild_name, data in GUILD_EMOJIS_ROLES.items():
            button = Button(
                label=f"  {guild_name.upper()}  ",
                emoji=data["emoji"],
                style=discord.ButtonStyle.primary
            )
            button.callback = self.create_ping_callback(guild_name, data["role_id"])
            self.add_item(button)

    def create_ping_callback(self, guild_name, role_id):
        async def callback(interaction: discord.Interaction):
            if interaction.guild_id != GUILD_ID:
                await interaction.response.send_message(
                    "Cette fonction n'est pas disponible sur ce serveur.", ephemeral=True
                )
                return

            alert_channel = interaction.guild.get_channel(ALERTE_DEF_CHANNEL_ID)
            if not alert_channel:
                await interaction.response.send_message("Canal d'alerte introuvable !", ephemeral=True)
                return

            role = interaction.guild.get_role(role_id)
            if not role:
                await interaction.response.send_message(f"Rôle pour {guild_name} introuvable !", ephemeral=True)
                return

            # Send alert to the alert channel
            alert_message = random.choice(ALERT_MESSAGES).format(role=role.mention)
            embed = discord.Embed(
                title="🔔 Alerte envoyée !",
                description=f"**{interaction.user.mention}** a déclenché une alerte pour **{guild_name}**.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            embed.add_field(name="📝 Notes", value="Aucune note.", inline=False)

            sent_message = await alert_channel.send(f"{alert_message}", embed=embed, view=AddNoteView(self.bot, sent_message))

            # Acknowledge the interaction
            await interaction.response.send_message(
                f"Alerte envoyée à {guild_name} dans le canal d'alerte!", ephemeral=True
            )

        return callback


class StartGuildCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def ensure_panel(self):
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            print("Guild not found. Check the GUILD_ID.")
            return

        channel = guild.get_channel(PING_DEF_CHANNEL_ID)
        if not channel:
            print("Ping definition channel not found. Check the PING_DEF_CHANNEL_ID.")
            return

        view = GuildPingView(self.bot)
        message_content = "Cliquez sur le logo de votre guilde pour envoyer une alerte DEF !"

        async for message in channel.history(limit=50):
            if message.pinned and message.author == self.bot.user:  # Check if the bot is the author of the pinned message
                await message.edit(content=message_content, view=view)
                print("Panel updated.")
                return

        new_message = await channel.send(content=message_content, view=view)
        print("Panel created.")


async def setup(bot: commands.Bot):
    await bot.add_cog(StartGuildCog(bot))  # Make sure to await this properly
