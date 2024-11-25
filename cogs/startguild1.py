import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Modal, TextInput
import json
import random

# Configuration
GUILD_ID = 1217700740949348443  # Replace with your guild ID
PING_DEF_CHANNEL_ID = 1247706162317758597  # Replace with your ping channel ID
ALERTE_DEF_CHANNEL_ID = 1247728738326679583  # Replace with your alert channel ID
EMOJIS_ROLES_FILE = "guild_emojis_roles.json"  # File to store emoji-role data

# Function to load the emoji-role data
def load_emojis_roles():
    try:
        with open(EMOJIS_ROLES_FILE, "r") as f:
            data = f.read().strip()
            if not data:
                return {}  # If file is empty, return an empty dictionary
            return json.loads(data)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding {EMOJIS_ROLES_FILE}. Returning empty dictionary.")
        return {}

# Function to save the emoji-role data
def save_emojis_roles(data):
    try:
        with open(EMOJIS_ROLES_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving {EMOJIS_ROLES_FILE}: {e}")

# Slash command to add a new guild emoji, role, and logo
class NewGuildModal(Modal):
    def __init__(self):
        super().__init__(title="Ajouter un nouvel emoji et un rôle")
        
        self.emoji_name_input = TextInput(
            label="Nom de l'emoji",
            placeholder="Exemple : Darkness",
            required=True
        )
        self.add_item(self.emoji_name_input)

        self.emoji_input = TextInput(
            label="Emoji",
            placeholder="Exemple : 🌑",
            required=True
        )
        self.add_item(self.emoji_input)

        self.role_input = TextInput(
            label="ID du rôle",
            placeholder="Exemple : 123456789012345678",
            required=True
        )
        self.add_item(self.role_input)

        self.logo_input = TextInput(
            label="URL du logo",
            placeholder="Exemple : https://example.com/logo.png",
            required=False
        )
        self.add_item(self.logo_input)

    async def on_submit(self, interaction: discord.Interaction):
        emoji_name = self.emoji_name_input.value.strip()
        emoji = self.emoji_input.value.strip()
        role_id = self.role_input.value.strip()
        logo_url = self.logo_input.value.strip()

        emojis_roles = load_emojis_roles()
        
        # Add the new emoji and role
        emojis_roles[emoji_name] = {
            "emoji": emoji,
            "role_id": role_id,
            "logo_url": logo_url
        }

        save_emojis_roles(emojis_roles)
        
        await interaction.response.send_message(f"Emoji et rôle pour **{emoji_name}** ajoutés avec succès.", ephemeral=True)
        
        # Update the button panel
        await update_button_panel(self.bot)

class StartGuild1Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="newguild", description="Ajoutez un nouvel emoji, rôle et logo.")
    async def newguild(self, interaction: discord.Interaction):
        # Logic for adding emojis, roles, and logos here
        await interaction.response.send_message("New guild command received!")

    async def ensure_panel(self):
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            print("Guild not found. Check the GUILD_ID.")
            return
        
        @commands.Cog.listener()
        async def on_ready(self):
            await self.bot.tree.sync()  # Sync the commands when the bot is ready
            channel = guild.get_channel(PING_DEF_CHANNEL_ID)
            if not channel:
                print("Ping definition channel not found. Check the PING_DEF_CHANNEL_ID.")
                return

            await update_button_panel(self.bot)

    async def on_ready(self):
        await self.ensure_panel()

    async def setup(self, bot: commands.Bot):
        await bot.add_cog(StartGuild1Cog(bot))

async def update_button_panel(bot: commands.Bot):
    # Load the emojis and roles from file
    emojis_roles = load_emojis_roles()

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found.")
        return

    channel = guild.get_channel(PING_DEF_CHANNEL_ID)
    if not channel:
        print("Channel not found.")
        return

    # Create the buttons dynamically based on stored data
    view = View(timeout=None)
    for guild_name, data in emojis_roles.items():
        button = Button(
            label=f"  {guild_name.upper()}  ",
            emoji=data["emoji"],
            style=discord.ButtonStyle.primary
        )
        button.callback = await create_ping_callback(guild_name, data)
        view.add_item(button)

    message_content = (
        "**🎯 Panneau d'Alerte DEF**\n\n"
        "Bienvenue sur le Panneau d'Alerte Défense ! Cliquez sur le bouton de votre guilde ci-dessous pour envoyer une alerte à votre équipe.\n\n"
        "⬇️ **Guildes Disponibles** ⬇️"
    )
    await channel.send(content=message_content, view=view)

async def create_ping_callback(guild_name, data):
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

            role = interaction.guild.get_role(int(data["role_id"]))
            if not role:
                await interaction.response.send_message(f"Rôle pour {guild_name} introuvable !", ephemeral=True)
                return

            alert_message = random.choice(ALERT_MESSAGES).format(role=role.mention)
            embed = discord.Embed(
                title="🔔 Alerte envoyée !",
                description=f"**{interaction.user.mention}** a déclenché une alerte pour **{guild_name}**.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=data["logo_url"] if data["logo_url"] else interaction.user.avatar.url)
            embed.add_field(name="📝 Notes", value="Aucune note.", inline=False)

            sent_message = await alert_channel.send(content=alert_message, embed=embed)
            view = AlertActionView(bot, sent_message)
            await sent_message.edit(view=view)

            await interaction.response.send_message(
                f"Alerte envoyée à {guild_name} dans le canal d'alerte !", ephemeral=True
            )

        except Exception as e:
            print(f"Error in ping callback for {guild_name}: {e}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    return callback

# Setup function for adding the cog
async def setup(bot: commands.Bot):
    await bot.add_cog(StartGuild1Cog(bot))
