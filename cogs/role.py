import discord
from discord.ext import commands

# Role data
ROLE_DATA = {
    "Darkness": {"emoji": "🖤", "role_name": "Darkness", "role_id": 1300093554064097407},
    "GTO": {"emoji": "🔵", "role_name": "GTO", "role_id": 1300093554080612363},
    "Aversion": {"emoji": "🔴", "role_name": "Aversion", "role_id": 1300093554064097409},
    "Bonnebuche": {"emoji": "🟢", "role_name": "Bonnebuche", "role_id": 1300093554080612365},
    "LMDF": {"emoji": "🟠", "role_name": "LMDF", "role_id": 1300093554080612364},
    "Notorious": {"emoji": "💛", "role_name": "Notorious", "role_id": 1300093554064097406},
    "Percophile": {"emoji": "💜", "role_name": "Percophile", "role_id": 1300093554080612362},
    "Tilisquad": {"emoji": "🤍", "role_name": "Tilisquad", "role_id": 1300093554080612367},
}

class InGameNameModal(discord.ui.Modal):
    def __init__(self, bot, role_name):
        super().__init__(title="Nom en Jeu")
        self.bot = bot
        self.role_name = role_name

        self.ign = discord.ui.TextInput(
            label="Entrez votre nom en jeu",
            placeholder="Exemple: Momonga-beta",
            required=True,
            max_length=32,
        )
        self.add_item(self.ign)

    async def on_submit(self, interaction: discord.Interaction):
        member = interaction.user
        try:
            await member.edit(nick=self.ign.value)
            await interaction.response.send_message(
                f"Votre nom a été mis à jour : **{self.ign.value}** et vous avez le rôle **{self.role_name}** !",
                ephemeral=True,
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "Impossible de mettre à jour votre pseudo. Vérifiez mes permissions !",
                ephemeral=True,
            )


class RoleButton(discord.ui.Button):
    def __init__(self, bot, role_name, emoji, role_display_name, role_id):
        super().__init__(label=role_name, emoji=emoji, style=discord.ButtonStyle.primary)
        self.bot = bot
        self.role_display_name = role_display_name
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        # Get or create the role
        role = guild.get_role(self.role_id)
        if not role:
            role = await guild.create_role(
                name=self.role_display_name,
                reason="Création automatique du rôle.",
            )

        # Assign role
        await user.add_roles(role, reason="Role Selection")
        await interaction.response.send_message(
            f"Vous avez choisi le rôle **{self.role_display_name}** ! Un moment ...",
            ephemeral=True,
        )

        # Prompt for in-game name
        modal = InGameNameModal(self.bot, self.role_display_name)
        await interaction.response.send_modal(modal)


class RoleSelectionView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        for role_name, role_info in ROLE_DATA.items():
            self.add_item(RoleButton(bot, role_name, role_info["emoji"], role_info["role_name"], role_info["role_id"]))


class RoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roles")
    async def roles(self, ctx):
        embed = discord.Embed(
            title="Choisissez votre rôle",
            description="Cliquez sur un bouton pour choisir un rôle !",
            color=discord.Color.blue(),
        )
        await ctx.send(embed=embed, view=RoleSelectionView(self.bot))


async def setup(bot):
    await bot.add_cog(RoleCog(bot))
