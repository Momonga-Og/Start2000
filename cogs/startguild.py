import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import random

# Configuration
GUILD_ID = 1217700740949348443  # Replace with your guild ID
PING_DEF_CHANNEL_ID = 1247706162317758597  # Replace with your ping channel ID
ALERTE_DEF_CHANNEL_ID = 1247728738326679583  # Replace with your alert channel ID

GUILD_EMOJIS_ROLES = {
    "Darkness": {"emoji": "🌑", "role_id": 1244077334668116050},
    "GTO": {"emoji": "🔥", "role_id": 1244077334668116050},
    "Aversion": {"emoji": "💀", "role_id": 1244077334668116050},
    "Bonnebuche": {"emoji": "🍞", "role_id": 1244077334668116050},
    "LMDF": {"emoji": "💪", "role_id": 1244077334668116050},
    "Notorious": {"emoji": "⚡", "role_id": 1244077334668116050},
    "Percophile": {"emoji": "🎶", "role_id": 1244077334668116050},
    "Tilisquad": {"emoji": "👑", "role_id": 1244077334668116050},
}

ALERT_MESSAGES = [
    "🚨 {role} Alerte DEF ! Connectez-vous maintenant !",
    "⚔️ {role}, il est temps de défendre !",
    "🛡️ {role} Défendez votre guilde !",
    "💥 {role} est attaquée ! Rejoignez la défense !",
    "⚠️ {role}, mobilisez votre équipe pour défendre !",
]


class AlertResponseView(View):
    def __init__(self, alert_message: discord.Message):
        super().__init__(timeout=None)
        self.alert_message = alert_message

    @discord.ui.button(label="Ajouter une Note", style=discord.ButtonStyle.primary)
    async def add_note(self, button: Button, interaction: discord.Interaction):
        class NoteModal(Modal):
            def __init__(self):
                super().__init__(title="Ajouter une Note")
                self.note = TextInput(
                    label="Note",
                    placeholder="Ajoutez une note ici...",
                    style=discord.TextStyle.paragraph,
                )
                self.add_item(self.note)

            async def on_submit(self, modal_interaction: discord.Interaction):
                await self.alert_message.reply(
                    f"📘 **Note ajoutée par {modal_interaction.user.mention}**:\n{self.note.value}",
                    mention_author=False,
                )
                await modal_interaction.response.send_message("Note ajoutée avec succès!", ephemeral=True)

        await interaction.response.send_modal(NoteModal())

    @discord.ui.button(label="Win", style=discord.ButtonStyle.success)
    async def mark_win(self, button: Button, interaction: discord.Interaction):
        await self.alert_message.reply(
            f"✅ **Alerte marquée comme GAGNÉE par {interaction.user.mention}**.",
            mention_author=False,
        )
        await interaction.response.send_message("Alerte marquée comme gagnée!", ephemeral=True)

    @discord.ui.button(label="Lost", style=discord.ButtonStyle.danger)
    async def mark_lost(self, button: Button, interaction: discord.Interaction):
        await self.alert_message.reply(
            f"❌ **Alerte marquée comme PERDUE par {interaction.user.mention}**.",
            mention_author=False,
        )
        await interaction.response.send_message("Alerte marquée comme perdue!", ephemeral=True)



class GuildPingView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

        for guild_name, data in GUILD_EMOJIS_ROLES.items():
            button = Button(
                label=f"  {guild_name.upper()}  ",
                emoji=data["emoji"],
                style=discord.ButtonStyle.primary,
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

            alert_message = random.choice(ALERT_MESSAGES).format(role=role.mention)
            sent_message = await alert_channel.send(alert_message)

            # Add responsive buttons under the alert
            view = AlertResponseView(sent_message)
            await sent_message.edit(view=view)

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
            if message.pinned and message.author == self.bot.user:
                await message.edit(content=message_content, view=view)
                print("Panel updated.")
                return

        new_message = await channel.send(content=message_content, view=view)
        await new_message.pin()
        print("Panel created and pinned.")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} is ready!")
        await self.ensure_panel()


async def setup(bot: commands.Bot):
    await bot.add_cog(StartGuildCog(bot))
