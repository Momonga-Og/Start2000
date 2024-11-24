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
        """Assigns the role to the user when they click the button."""
        guild = interaction.client.guilds[0]  # Replace with specific guild ID if needed
        member = guild.get_member(interaction.user.id)

        if not member:
            # Fallback to fetching the member directly if they aren't cached
            try:
                member = await guild.fetch_member(interaction.user.id)
            except discord.NotFound:
                await interaction.response.send_message(
                    "You must be a member of the server to use this action.",
                    ephemeral=True
                )
                return

        # Fetch the roles
        role = guild.get_role(self.role_id)
        additional_role = guild.get_role(ADDITIONAL_ROLE_ID)

        if not role or not additional_role:
            await interaction.response.send_message(
                "There was an error assigning the roles. Please contact an admin.",
                ephemeral=True
            )
            return

        # Assign roles
        try:
            await member.add_roles(role, additional_role)
            await interaction.response.send_message(
                f"You have been assigned to **{self.guild_name}** and an additional role!",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I do not have permission to assign roles. Please contact an admin.",
                ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"An error occurred while assigning the roles: {e}",
                ephemeral=True
            )

class RoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Triggered when a member joins the server."""
        await self.send_welcome_message(member)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Fallback: Trigger when a new member sends their first message."""
        if message.author.bot:
            return  # Ignore bot messages

        member = message.author
        guild = message.guild

        if guild is None:
            return  # Ignore DMs

        # Check if the member has no roles (likely new member)
        if len(member.roles) <= 1:  # The default role doesn't count
            print(f"Detected new member via message: {member.name}")
            await self.send_welcome_message(member)

    async def send_welcome_message(self, member: discord.Member):
        """Send a welcome message to a new member via private message."""
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

        try:
            # Send DM to the new member
            await member.send(
                content="Welcome to the server!",
                embed=embed,
                view=RoleSelectionView()
            )
            print(f"Sent welcome message to {member.name} in DM.")
        except discord.Forbidden:
            print(f"Could not send a DM to {member.name}. They may have DMs disabled.")

async def setup(bot):
    await bot.add_cog(RoleCog(bot))
