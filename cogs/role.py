import discord
from discord.ext import commands

# Guild roles configuration
GUILD_DATA = {
    "Darkness": {"emoji": "<:Darkness:1307418763276324944>", "role_id": 1300093554064097407},
    "GTO": {"emoji": "<:GTO:1307418692992237668>", "role_id": 1300093554080612363},
    "Aversion": {"emoji": "<:aversion:1307418759002198086>", "role_id": 1300093554064097409},
    "Bonnebuche": {"emoji": "<:bonnebuche:1307418760763670651>", "role_id": 1300093554080612365},
    "LMDF": {"emoji": "<:lmdf:1307418765142786179>", "role_id": 1300093554080612364},
    "Notorious": {"emoji": "<:notorious:1307418766266728500>", "role_id": 1300093554064097406},
    "Percophile": {"emoji": "<:percophile:1307418769764651228>", "role_id": 1300093554080612362},
    "Tilisquad": {"emoji": "<:tilisquad:1307418771882905600>", "role_id": 1300093554080612367},
}

class RoleSelectionView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)  # No timeout for this view
        self.bot = bot
        for guild_name, guild_info in GUILD_DATA.items():
            self.add_item(RoleButton(bot, guild_name, guild_info["emoji"], guild_info["role_id"]))

class RoleButton(discord.ui.Button):
    def __init__(self, bot, guild_name, emoji, role_id):
        super().__init__(label=guild_name, emoji=emoji, style=discord.ButtonStyle.primary)
        self.bot = bot
        self.guild_name = guild_name
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        """Handles role assignment when a button is clicked."""
        guild = self.bot.guilds[0]  # Since the bot is in only one server
        role = guild.get_role(self.role_id)
        member = guild.get_member(interaction.user.id)

        # Ensure the role and member are valid
        if not role:
            await interaction.response.send_message(
                "The role for this button was not found. Please contact an admin.",
                ephemeral=True
            )
            return
        if not member:
            await interaction.response.send_message(
                "Unable to find your membership in the server. Please contact an admin.",
                ephemeral=True
            )
            return

        # Assign the role
        try:
            await member.add_roles(role)
            await interaction.response.send_message(
                f"You have been assigned to the **{self.guild_name}** role!",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I do not have permission to assign roles. Please contact an admin.",
                ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"An error occurred while assigning the role: {e}",
                ephemeral=True
            )

class RoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Triggered when a member joins the server."""
        await self.send_welcome_message(member)

    async def send_welcome_message(self, member: discord.Member):
        """Sends a welcome message with the role selection buttons."""
        embed = discord.Embed(
            title="Welcome to the Server!",
            description=(
                "Please select your guild by clicking one of the buttons below to be assigned a role."
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Welcome to our community!")
        embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else None)

        try:
            await member.send(
                content="Welcome to the server!",
                embed=embed,
                view=RoleSelectionView(self.bot)
            )
        except discord.Forbidden:
            print(f"Could not send a DM to {member.name}. They may have DMs disabled.")

async def setup(bot):
    await bot.add_cog(RoleCog(bot))
