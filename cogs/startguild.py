import discord
from discord.ext import commands
from discord.ui import Button, View
from .config import GUILD_ID, PING_DEF_CHANNEL_ID, ALERTE_DEF_CHANNEL_ID


class GuildPingView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)  # Timeout is None for persistent views
        self.bot = bot
        self.cooldowns = {}  # A dictionary to store cooldowns for buttons

        # Adding GTO button
        self.add_item(Button(label="GTO", style=discord.ButtonStyle.red, custom_id="gto"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Check if interaction is valid (e.g., not on cooldown).
        """
        if "cooldown" in self.cooldowns:
            remaining_time = self.cooldowns["cooldown"] - discord.utils.utcnow().timestamp()
            if remaining_time > 0:
                await interaction.response.send_message(
                    f"⏳ Cooldown active! Please wait {int(remaining_time)} seconds before trying again.",
                    ephemeral=True
                )
                return False
        return True

    @discord.ui.button(label="GTO", style=discord.ButtonStyle.danger, custom_id="gto")
    async def gto_button(self, button: Button, interaction: discord.Interaction):
        """
        Handle GTO button click.
        """
        now = discord.utils.utcnow().timestamp()
        self.cooldowns["cooldown"] = now + 120  # Set cooldown for 2 minutes

        # Example action: Send a message
        await interaction.response.send_message("🚨 GTO alert sent!", ephemeral=False)


class StartGuildCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def ensure_panel(self):
        """
        Ensures that the panel for the alert system is updated or created.
        """
        # Fetch the guild
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            print("⚠️ Guild not found. Check the GUILD_ID in your configuration.")
            return

        # Fetch the designated channel for ping definitions
        channel = guild.get_channel(PING_DEF_CHANNEL_ID)
        if not channel:
            print("⚠️ Ping definition channel not found. Check the PING_DEF_CHANNEL_ID in your configuration.")
            return

        # Create the interactive view and the embed
        view = GuildPingView(self.bot)
        embed = discord.Embed(
            title="🎯 Panneau d'Alerte DEF",
            description=(
                "Bienvenue sur le **Panneau d'Alerte Défense** !\n\n"
                "Utilisez les boutons ci-dessous pour envoyer une alerte à votre guilde. "
                "Cliquez simplement sur le bouton correspondant pour notifier ses membres.\n\n"
                "**📋 Instructions :**\n"
                "1️⃣ Cliquez sur le bouton correspondant à votre guilde.\n"
                "2️⃣ Suivez les mises à jour dans le canal d'alerte.\n"
                "3️⃣ Ajoutez des notes si nécessaire.\n\n"
                "⬇️ **Guildes Disponibles** ⬇️"
            ),
            color=discord.Color.blurple()  # Using blurple for a modern, Discord-friendly color.
        )
        embed.set_footer(text="Alliance START | Alert System", icon_url="https://example.com/icon.png")

        # Check for an existing pinned message to update it
        async for message in channel.history(limit=50):
            if message.pinned:
                await message.edit(embed=embed, view=view)
                print("✅ Panel updated successfully.")
                return

        # Create and pin a new message if none exist
        new_message = await channel.send(embed=embed, view=view)
        await new_message.pin()
        print("✅ Panel created and pinned successfully.")

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Event listener triggered when the bot is ready. Ensures the alert panel and updates permissions.
        """
        await self.ensure_panel()

        # Fetch the guild and alert channel
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            print("⚠️ Guild not found. Check the GUILD_ID in your configuration.")
            return

        alert_channel = guild.get_channel(ALERTE_DEF_CHANNEL_ID)
        if alert_channel:
            # Update alert channel permissions to restrict sending and reactions
            await alert_channel.set_permissions(
                guild.default_role, send_messages=False, add_reactions=False
            )
            print("✅ Alert channel permissions updated.")

        print("🚀 Bot is ready and operational.")


# Async function to add the cog to the bot
async def setup(bot: commands.Bot):
    """
    Setup function to add the StartGuildCog to the bot.
    """
    await bot.add_cog(StartGuildCog(bot))
