import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import os

class Alerts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_channel_id = 1247728738326679583  # Replace with your specific channel ID

    @app_commands.command(name="alert", description="Generate a report of notifications sent in this channel for the last 7 days.")
    async def alert(self, interaction: discord.Interaction):
        # Ensure the command is only used in the designated channel
        if interaction.channel_id != self.allowed_channel_id:
            await interaction.response.send_message("This command can only be used in the designated channel.", ephemeral=True)
            return

        # Get the message history for the last 7 days
        channel = interaction.channel
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)

        # Collect relevant messages asynchronously
        messages = []
        async for message in channel.history(after=seven_days_ago):
            if message.author.bot and (message.mention_everyone or message.role_mentions):
                messages.append(message)

        # Collect notification data
        notification_data = {}
        for message in messages:
            author = message.author
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            roles_tagged = [role.name for role in message.role_mentions]

            # Initialize data for the author if not already done
            if author.id not in notification_data:
                notification_data[author.id] = {
                    "username": author.name,
                    "roles_tagged": {},
                    "timestamps": []
                }

            # Add the timestamp of the message
            notification_data[author.id]["timestamps"].append(timestamp)

            # Count the roles tagged
            for role in roles_tagged:
                if role not in notification_data[author.id]["roles_tagged"]:
                    notification_data[author.id]["roles_tagged"][role] = 0
                notification_data[author.id]["roles_tagged"][role] += 1

        # Generate the report
        report_filename = f"notification_report_{now.strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, "w") as report_file:
            if not notification_data:
                report_file.write("No notifications were sent in the last 7 days.\n")
            else:
                for user_id, data in notification_data.items():
                    report_file.write(f"User: {data['username']}\n")
                    report_file.write(f"Notifications sent: {len(data['timestamps'])}\n")
                    report_file.write("Roles tagged:\n")
                    for role, count in data["roles_tagged"].items():
                        report_file.write(f"  {role}: {count} times\n")
                    report_file.write("Timestamps:\n")
                    for timestamp in data["timestamps"]:
                        report_file.write(f"  {timestamp}\n")
                    report_file.write("\n")

        # Notify the user and attach the file
        await interaction.response.send_message("Report generated:", file=discord.File(report_filename), ephemeral=True)

        # Clean up the file after sending
        os.remove(report_filename)

async def setup(bot):
    await bot.add_cog(Alerts(bot))
