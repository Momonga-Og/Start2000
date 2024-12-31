import discord
from discord.ext import commands
from pymongo import MongoClient
import os
import re

class StartGuild1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = MongoClient(os.getenv("MONGO_URI"))  # Ensure MONGO_URI is in your environment variables
        self.db = self.client["Spectra"]

    @commands.command()
    async def set_alliance(self, ctx, guild_id: int, role: discord.Role):
        """Assigns an alliance role to a specific guild."""
        # Extracting role ID if it's passed as mention
        role_id_match = re.match(r"<@&(?P<id>\d+)>", str(role))
        role_id = int(role_id_match.group("id")) if role_id_match else role.id

        # Insert or update in the database
        self.db.guilds.update_one(
            {"_id": guild_id},
            {"$set": {"alliance_role": role_id}},
            upsert=True
        )
        await ctx.send(f"Alliance role for guild {guild_id} set to {role.mention}.")

    @commands.command()
    async def upload_logo(self, ctx, guild_id: int):
        """Uploads a logo for a guild."""
        await ctx.send("Please upload the logo image.")

        def check(msg):
            return msg.author == ctx.author and msg.attachments

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60.0)
            attachment = msg.attachments[0]

            if not attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                await ctx.send("Invalid file type. Please upload a PNG or JPG image.")
                return

            # Save the logo in the database (as URL or base64 if necessary)
            logo_url = attachment.url
            self.db.guilds.update_one(
                {"_id": guild_id},
                {"$set": {"logo_url": logo_url}},
                upsert=True
            )

            await ctx.send(f"Logo for guild {guild_id} uploaded successfully.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command()
    async def get_guild_info(self, ctx, guild_id: int):
        """Retrieves the stored information for a guild."""
        guild_info = self.db.guilds.find_one({"_id": guild_id})

        if not guild_info:
            await ctx.send(f"No information found for guild {guild_id}.")
            return

        alliance_role = guild_info.get("alliance_role")
        logo_url = guild_info.get("logo_url")
        
        response = f"**Guild ID**: {guild_id}\n"
        response += f"**Alliance Role**: <@&{alliance_role}>\n" if alliance_role else "Alliance Role: None\n"
        response += f"**Logo URL**: {logo_url}\n" if logo_url else "Logo URL: None\n"

        await ctx.send(response)

# Add cog to bot
def setup(bot):
    bot.add_cog(StartGuild1(bot))
