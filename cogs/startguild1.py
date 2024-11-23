# startguild1.py
from discord.ext import commands
from discord import app_commands, Interaction, Embed, ButtonStyle
from discord.ui import View, Button

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
class GuildAlertView(View):
    def __init__(self):
        super().__init__()
        self.add_item(AddNoteButton())
        self.add_item(WonButton())
        self.add_item(LostButton())

class AddNoteButton(Button):
    def __init__(self):
        super().__init__(label="Ajouter une note", style=ButtonStyle.blurple)

    async def callback(self, interaction: Interaction):
        await interaction.response.send_message(
            "La fonctionnalité 'Ajouter une note' est en cours de développement !", ephemeral=True
        )

class WonButton(Button):
    def __init__(self):
        super().__init__(label="Gagné", style=ButtonStyle.green)

    async def callback(self, interaction: Interaction):
        await interaction.response.send_message(
            "🎉 Les défenseurs ont **gagné** la bataille contre les attaquants ! Bien joué !",
            ephemeral=False,
        )

class LostButton(Button):
    def __init__(self):
        super().__init__(label="Perdu", style=ButtonStyle.red)

    async def callback(self, interaction: Interaction):
        await interaction.response.send_message(
            "❌ Les défenseurs ont **perdu** la bataille. Bonne chance la prochaine fois !",
            ephemeral=False,
        )

class StartGuildCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="alerte")
    async def alerte(self, ctx):
        """Send an alert message to the designated channel with interactive buttons."""
        channel = self.bot.get_channel(ALERTE_DEF_CHANNEL_ID)
        if not channel:
            await ctx.send("Impossible de trouver le canal d'alerte.")
            return

        embed = Embed(
            title="Alerte percepteur",
            description="Un percepteur est attaqué ! Veuillez défendre immédiatement !",
            color=0xFF0000,
        )
        embed.add_field(name="Instructions", value="Cliquez sur les boutons ci-dessous pour indiquer le résultat.")
        await channel.send(embed=embed, view=GuildAlertView())

async def setup(bot: commands.Bot):
    await bot.add_cog(StartGuildCog(bot))
