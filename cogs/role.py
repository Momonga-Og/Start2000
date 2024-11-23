import discord
from discord.ext import commands

# Replace this ID with the ID of the additional role to assign to all users.
ADDITIONAL_ROLE_ID = 1300093554080612361

# Guild data
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
    def __init__(self):
        super().__init__(timeout=None)  # No timeout for this view
        for guild_name, guild_info in GUILD_DATA.items():
            self.add_item(RoleButton(guild_name, guild_info["emoji"], guild_info["role_id"]))

class RoleButton(discord.ui.Button):
    def __init__(self, guild_name, emoji, role_id):
        super().__init__(label=guild_name, emoji=emoji, style=discord.ButtonStyle.primary)
        self.guild_name = guild_name
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        role = guild.get_role(self.role_id)
        additional_role = guild.get_role(ADDITIONAL_ROLE_ID)

        if not role or not additional_role:
            await interaction.response.send_message(
                "There was an error assigning the roles. Please contact an admin.",
                ephemeral=True
            )
            return

        # Assign roles
        await member.add_roles(role, additional_role)
        await interaction.response.send_message(
            f"You have been assigned to **{self.guild_name}** and an additional role!",
            ephemeral=True
        )

class RoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Create the embed
        embed = discord.Embed(
            title="Welcome to the Alliance!",
            description=(
                "Welcome to the server! Please select your guild from the buttons below "
                "to get the appropriate role. You'll also receive an additional role for being part of the alliance."
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Choose wisely!")
        embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else None)

        # Send the embed with the buttons
        channel = member.guild.system_channel
        if channel:
            await channel.send(
                content=f"Welcome {member.mention}!",
                embed=embed,
                view=RoleSelectionView()
            )

async def setup(bot):
    await bot.add_cog(RoleCog(bot))
