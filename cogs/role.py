import discord
from discord.ext import commands

# Replace with your bot's token
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Guild role configuration
ROLE_DATA = {
    "Darkness": {"emoji": "🌑", "role_id": 1300093554064097407},
    "GTO": {"emoji": "🚗", "role_id": 1300093554080612363},
    "Aversion": {"emoji": "⚔️", "role_id": 1300093554064097409},
    "Bonnebuche": {"emoji": "🍂", "role_id": 1300093554080612365},
    "LMDF": {"emoji": "🌲", "role_id": 1300093554080612364},
    "Notorious": {"emoji": "💀", "role_id": 1300093554064097406},
    "Percophile": {"emoji": "🎵", "role_id": 1300093554080612362},
    "Tilisquad": {"emoji": "🔥", "role_id": 1300093554080612367},
}

# Additional role to assign to all users
ADDITIONAL_ROLE_ID = 1258492552605335645

# The ID of the channel where the bot will post the role selection message
ROLE_CHANNEL_ID = 123456789012345678  # Replace with your channel ID

# Create a bot instance with the necessary intents
intents = discord.Intents.default()
intents.members = True  # Needed to fetch members and assign roles
bot = commands.Bot(command_prefix="!", intents=intents)


class RoleSelectionView(discord.ui.View):
    """Interactive view for role selection."""

    def __init__(self):
        super().__init__(timeout=None)  # No timeout for persistent buttons
        for role_name, role_info in ROLE_DATA.items():
            self.add_item(RoleButton(role_name, role_info["emoji"], role_info["role_id"]))


class RoleButton(discord.ui.Button):
    """A button for assigning a specific role."""

    def __init__(self, role_name, emoji, role_id):
        super().__init__(label=role_name, emoji=emoji, style=discord.ButtonStyle.primary)
        self.role_name = role_name
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user

        if not guild or not member:
            await interaction.response.send_message(
                "This interaction can only be used in a server.",
                ephemeral=True
            )
            return

        role = guild.get_role(self.role_id)
        additional_role = guild.get_role(ADDITIONAL_ROLE_ID)

        if not role or not additional_role:
            await interaction.response.send_message(
                "Roles are not correctly configured. Please contact an admin.",
                ephemeral=True
            )
            return

        try:
            await member.add_roles(role, additional_role, reason="Role assigned via button interaction.")
            await interaction.response.send_message(
                f"You have been assigned to **{self.role_name}** and an additional role!",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to assign roles. Please contact an admin.",
                ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"An error occurred while assigning roles: {e}",
                ephemeral=True
            )


@bot.event
async def on_ready():
    """Triggered when the bot is ready."""
    print(f"Logged in as {bot.user} ({bot.user.id})")

    # Get the role selection channel
    guild = bot.guilds[0]  # Assuming the bot is in only one server
    channel = guild.get_channel(ROLE_CHANNEL_ID)

    if not channel:
        print(f"Channel with ID {ROLE_CHANNEL_ID} not found.")
        return

    # Check if the message already exists
    async for message in channel.history(limit=10):  # Check recent messages for redundancy
        if message.author == bot.user and message.content.startswith("**Role Selection**"):
            print("Role selection message already exists.")
            return

    # Send the role selection message
    embed = discord.Embed(
        title="Role Selection",
        description=(
            "Welcome to the server! Click the buttons below to select your guild role.\n\n"
            "You will also be assigned an alliance role automatically."
        ),
        color=discord.Color.blue()
    )
    await channel.send("**Role Selection**", embed=embed, view=RoleSelectionView())


@bot.event
async def on_member_join(member: discord.Member):
    """DM the member with a welcome message on joining."""
    embed = discord.Embed(
        title="Welcome to the Alliance!",
        description=(
            "Welcome to the server! Please visit the role selection channel to choose your guild role.\n"
            "You'll receive an additional role automatically upon selection."
        ),
        color=discord.Color.green()
    )

    try:
        await member.send(embed=embed)
    except discord.Forbidden:
        print(f"Could not DM {member.name}. They may have DMs disabled.")


bot.run(BOT_TOKEN)
