import discord
from discord.ext import commands
from discord.ui import View, Button

# Bot intents
intents = discord.Intents.default()
intents.members = True  # To track member events like join
intents.messages = True  # Ensure the bot can handle messages

# Role data
ROLE_DATA = {
    "Darkness": {"emoji": "<:Darkness:1307418763276324944>", "role_id": 1300093554064097407},
    "GTO": {"emoji": "<:GTO:1307418692992237668>", "role_id": 1300093554080612363},
    "Aversion": {"emoji": "<:aversion:1307418759002198086>", "role_id": 1300093554064097409},
    "Bonnebuche": {"emoji": "<:bonnebuche:1307418760763670651>", "role_id": 1300093554080612365},
    "LMDF": {"emoji": "<:lmdf:1307418765142786179>", "role_id": 1300093554080612364},
    "Notorious": {"emoji": "<:notorious:1307418766266728500>", "role_id": 1300093554064097406},
    "Percophile": {"emoji": "<:percophile:1307418769764651228>", "role_id": 1300093554080612362},
    "Tilisquad": {"emoji": "<:tilisquad:1307418771882905600>", "role_id": 1300093554080612367},
}

SERVER_ID = 1217700740949348443  # Your server's ID


class RoleSelectionView(View):
    def __init__(self, member):
        super().__init__(timeout=None)
        self.member = member

        for role_name, data in ROLE_DATA.items():
            button = Button(label=role_name, emoji=data["emoji"], style=discord.ButtonStyle.primary)
            button.callback = self.create_callback(data["role_id"])
            self.add_item(button)

    def create_callback(self, role_id):
        async def callback(interaction: discord.Interaction):
            guild = interaction.client.get_guild(SERVER_ID)
            role = guild.get_role(role_id)
            if role:
                await self.member.add_roles(role)
                await interaction.response.send_message(
                    f"✅ Rôle `{role.name}` assigné avec succès !", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Impossible d'assigner le rôle. Veuillez contacter l'administrateur.", ephemeral=True
                )

        return callback


class RoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != SERVER_ID:
            return

        try:
            view = RoleSelectionView(member)
            await member.send(
                "👋 Bienvenue sur le serveur !\n\nVeuillez choisir un rôle en cliquant sur un bouton ci-dessous :",
                view=view,
            )
        except discord.Forbidden:
            print(f"Impossible d'envoyer un message à {member}. Le DM est probablement désactivé.")


async def setup(bot):
    await bot.add_cog(RoleCog(bot))

