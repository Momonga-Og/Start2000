import discord
from discord.ext import commands
from discord.ui import View, Button
import random

# Configuration
GUILD_ID = 1217700740949348443  # Replace with your guild ID
PING_DEF_CHANNEL_ID = 1247706162317758597  # Replace with your ping channel ID
ALERTE_DEF_CHANNEL_ID = 1247728738326679583  # Replace with your alert channel ID

# Guild emojis with IDs and corresponding role IDs
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

# French alert messages
ALERT_MESSAGES = [
    "🚨 {role} Alerte DEF ! Connectez-vous maintenant !",
    "⚔️ {role}, il est temps de défendre !",
    "🛡️ {role} Défendez votre guilde !",
    "💥 {role} est attaquée ! Rejoignez la défense !",
    "⚠️ {role}, mobilisez votre équipe pour défendre !",
]


class GuildPingView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

        # Add alert buttons for guilds
        for guild_name, data in GUILD_EMOJIS_ROLES.items():
            button = Button(
                label=f"  {guild_name.upper()}  ",
                emoji=data["emoji"],
                style=discord.ButtonStyle.primary,
            )
            button.callback = self.create_ping_callback(guild_name, data["role_id"])
            self.add_item(button)

        # Add additional buttons
        self.add_item(
            Button(
                label="Ajouter une Note",
                style=discord.ButtonStyle.success,
                custom_id="add_note",
            )
        )
        self.add_item(
            Button(
                label="Win",
                style=discord.ButtonStyle.green,
                custom_id="win",
            )
        )
        self.add_item(
            Button(
                label="Lost",
                style=discord.ButtonStyle.red,
                custom_id="lost",
            )
        )

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
            embed = discord.Embed(
                title="🔔 Alerte envoyée !",
                description=f"**{interaction.user.mention}** a déclenché une alerte pour **{guild_name}**.",
                color=discord.Color.red(),
            )
            embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)

            await alert_channel.send(f"{alert_message}", embed=embed)

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
        message_content = (
            "Cliquez sur le logo de votre guilde pour envoyer une alerte DEF !\n"
            "Utilisez les boutons ci-dessous pour des actions supplémentaires."
        )

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
