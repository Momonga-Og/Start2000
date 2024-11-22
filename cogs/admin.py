import discord
from discord.ext import commands
from discord import app_commands
import logging

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blocked_users = {}

    @app_commands.command(name="block_user", description="Block the bot from greeting a user")
    async def block_user(self, interaction: discord.Interaction, user: discord.Member):
        try:
            guild_id = interaction.guild.id
            if guild_id not in self.blocked_users:
                self.blocked_users[guild_id] = set()
            self.blocked_users[guild_id].add(user.id)
            await interaction.response.send_message(f"{user.name} will no longer be greeted by the bot.")
        except Exception as e:
            logging.exception("Error in block_user command")
            await interaction.response.send_message("An error occurred while processing your command.")

    @app_commands.command(name="unblock_user", description="Unblock the bot from greeting a user")
    async def unblock_user(self, interaction: discord.Interaction, user: discord.Member):
        try:
            guild_id = interaction.guild.id
            if guild_id in self.blocked_users and user.id in self.blocked_users[guild_id]:
                self.blocked_users[guild_id].remove(user.id)
                await interaction.response.send_message(f"{user.name} will now be greeted by the bot.")
            else:
                await interaction.response.send_message(f"{user.name} was not blocked.")
        except Exception as e:
            logging.exception("Error in unblock_user command")
            await interaction.response.send_message("An error occurred while processing your command.")

    @app_commands.command(name="addme", description="Add the bot to a server")
    async def addme(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message('Use this link to add me to your server: <invite_link>')
        except Exception as e:
            logging.exception("Error in addme command")
            await interaction.response.send_message("An error occurred while processing your command.")

async def setup(bot):
    cog = Admin(bot)
    await bot.add_cog(cog)
    if not bot.tree.get_command('block_user'):
        bot.tree.add_command(cog.block_user)
    if not bot.tree.get_command('unblock_user'):
        bot.tree.add_command(cog.unblock_user)
    if not bot.tree.get_command('addme'):
        bot.tree.add_command(cog.addme)
