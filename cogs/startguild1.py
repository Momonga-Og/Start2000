import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Modal, TextInput
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import random

# Configuration
GUILD_ID = 1217700740949348443  # Replace with your guild ID
PING_DEF_CHANNEL_ID = 1247706162317758597  # Replace with your ping channel ID
ALERTE_DEF_CHANNEL_ID = 1247728738326679583  # Replace with your alert channel ID

# MongoDB connection
uri = "mongodb+srv://srijafam:cobra123@cluster0.jbldi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["alert_panel"]
alliances_collection = db["alliances"]

ALERT_MESSAGES = [
    "\ud83d\udea8 {role} Alerte DEF ! Connectez-vous maintenant !",
    "\u2694\ufe0f {role}, il est temps de d\u00e9fendre !",
    "\ud83d\udee1\ufe0f {role} D\u00e9fendez votre guilde !",
    "\ud83d\udca5 {role} est attaqu\u00e9e ! Rejoignez la d\u00e9fense !",
    "\u26a0\ufe0f {role}, mobilisez votre \u00e9quipe pour d\u00e9fendre !",
]

class AlertActionView(View):
    def __init__(self, bot: commands.Bot, message: discord.Message):
        super().__init__(timeout=None)
        self.bot = bot
        self.message = message
        self.is_locked = False

        self.add_note_button = Button(
            label="Ajouter une note",
            style=discord.ButtonStyle.secondary,
            emoji="\ud83d\udd8d"
        )
        self.add_note_button.callback = self.add_note_callback
        self.add_item(self.add_note_button)

        self.won_button = Button(
            label="Won",
            style=discord.ButtonStyle.success,
        )
        self.won_button.callback = self.mark_as_won
        self.add_item(self.won_button)

        self.lost_button = Button(
            label="Lost",
            style=discord.ButtonStyle.danger,
        )
        self.lost_button.callback = self.mark_as_lost
        self.add_item(self.lost_button)

    async def add_note_callback(self, interaction: discord.Interaction):
        if interaction.channel_id != ALERTE_DEF_CHANNEL_ID:
            await interaction.response.send_message("Vous ne pouvez pas ajouter de note ici.", ephemeral=True)
            return

        modal = NoteModal(self.message)
        await interaction.response.send_modal(modal)

    async def mark_as_won(self, interaction: discord.Interaction):
        await self.mark_alert(interaction, "Gagnée", discord.Color.green())

    async def mark_as_lost(self, interaction: discord.Interaction):
        await self.mark_alert(interaction, "Perdue", discord.Color.red())

    async def mark_alert(self, interaction: discord.Interaction, status: str, color: discord.Color):
        if self.is_locked:
            await interaction.response.send_message("Cette alerte a déjà été marquée.", ephemeral=True)
            return

        self.is_locked = True
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

        embed = self.message.embeds[0]
        embed.color = color
        embed.add_field(name="Statut", value=f"L'alerte a été marquée comme **{status}** par {interaction.user.mention}.", inline=False)

        await self.message.edit(embed=embed)
        await interaction.response.send_message(f"Alerte marquée comme **{status}** avec succès.", ephemeral=True)

class GuildPingView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

        alliances = alliances_collection.find()
        for alliance in alliances:
            button = Button(
                label=f"  {alliance['name'].upper()}  ",
                emoji=alliance['logo'],
                style=discord.ButtonStyle.primary
            )
            button.callback = self.create_ping_callback(alliance)
            self.add_item(button)

    def create_ping_callback(self, alliance):
        async def callback(interaction: discord.Interaction):
            try:
                if interaction.guild_id != GUILD_ID:
                    await interaction.response.send_message(
                        "Cette fonction n'est pas disponible sur ce serveur.", ephemeral=True
                    )
                    return

                alert_channel = interaction.guild.get_channel(ALERTE_DEF_CHANNEL_ID)
                if not alert_channel:
                    await interaction.response.send_message("Canal d'alerte introuvable !", ephemeral=True)
                    return

                role = interaction.guild.get_role(alliance['role_id'])
                if not role:
                    await interaction.response.send_message(f"Rôle pour {alliance['name']} introuvable !", ephemeral=True)
                    return

                alert_message = random.choice(ALERT_MESSAGES).format(role=role.mention)
                embed = discord.Embed(
                    title="\ud83d\udd14 Alerte envoyée !",
                    description=f"**{interaction.user.mention}** a déclenché une alerte pour **{alliance['name']}**.",
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
                embed.add_field(name="\ud83d\udd8d Notes", value="Aucune note.", inline=False)

                sent_message = await alert_channel.send(content=alert_message, embed=embed)
                view = AlertActionView(self.bot, sent_message)
                await sent_message.edit(view=view)

                await interaction.response.send_message(
                    f"Alerte envoyée à {alliance['name']} dans le canal d'alerte !", ephemeral=True
                )

            except Exception as e:
                print(f"Error in ping callback for {alliance['name']}: {e}")
                await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

        return callback

class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="set_alliance", description="Configure a new alliance")
    async def set_alliance(self, interaction: discord.Interaction, logo: str, name: str, role: str):
        alliances_collection.insert_one({
            "logo": logo,
            "name": name,
            "role_id": int(role)
        })
        await interaction.response.send_message(
            f"Alliance `{name}` with logo `{logo}` and role `{role}` has been set.", ephemeral=True
        )

    @commands.Cog.listener()
    async def on_ready(self):
        print("AdminCommands ready.")

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
            "**🎯 Panneau d'Alerte DEF**\n\n"
            "Cliquez sur le bouton de votre guilde pour envoyer une alerte."
        )

        async for message in channel.history(limit=50):
            if message.pinned:
                await message.edit(content=message_content, view=view)
                print("Panel updated.")
                return

        new_message = await channel.send(content=message_content, view=view)
        await new_message.pin()
        print("Panel created and pinned successfully.")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.ensure_panel()

        guild = self.bot.get_guild(GUILD_ID)
        alert_channel = guild.get_channel(ALERTE_DEF_CHANNEL_ID)
        if alert_channel:
            await alert_channel.set_permissions(
                guild.default_role, send_messages=False, add_reactions=False
            )
            print("Alert channel permissions updated.")

        print("Bot is ready.")

async def setup(bot: commands.Bot):
    await bot.add_cog(StartGuildCog(bot))
    await bot.add_cog(AdminCommands(bot))
