import discord
from discord.ext import commands
from .config import GUILD_ID, PING_DEF_CHANNEL_ID, ALERTE_DEF_CHANNEL_ID
from .views import GuildPingView


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
        embed = discord.Embed(
            title="🎯 Panneau d'Alerte DEF",
            description=(
                "Bienvenue sur le **Panneau d'Alerte Défense** ! Utilisez les boutons ci-dessous pour envoyer une alerte "
                "à votre guilde. Cliquez simplement sur le bouton de votre guilde pour notifier ses membres.\n\n"
                "**💡 Instructions :**\n"
                "1️⃣ Cliquez sur le bouton correspondant à votre guilde.\n"
                "2️⃣ Suivez les mises à jour dans le canal d'alerte.\n"
                "3️⃣ Ajoutez des notes si nécessaire.\n\n"
                "⬇️ **Guildes Disponibles** ⬇️"
            ),
            color=discord.Color.blue()
        )

        async for message in channel.history(limit=50):
            if message.pinned:
                await message.edit(embed=embed, view=view)
                print("Panel updated.")
                return

        new_message = await channel.send(embed=embed, view=view)
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
