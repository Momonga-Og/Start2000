import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class WelcomeSparta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Check if the member joined the specific server
        if member.guild.id == 1300093554064097400:  # Sparta server ID
            try:
                # Send public welcome message
                public_channel = member.guild.get_channel(1300093554399645707)  # Public channel ID
                if public_channel:
                    welcome_message = (
                        f"🎉 Bienvenue {member.mention} à Alliance Start ! 🎉\n"
                        "Nous sommes ravis de t'avoir parmi nous ! N'oublie pas de consulter nos canaux et profite de ton séjour. 🎊"
                    )
                    image_url = "https://github.com/Momonga-Og/Start2000/blob/main/Alliance%20Start2000.png?raw=true"  
                    embed = discord.Embed(description=welcome_message, color=discord.Color.blue())
                    embed.set_image(url=image_url)
                    await public_channel.send(embed=embed)
                    print("Public welcome message sent successfully.")
                else:
                    print("Public channel not found or inaccessible.")

                # Send private welcome message with buttons
                dm_message = (
                    "Bonjour, je suis Start2000, le bot autonome créé pour l'alliance Start sur Dofus Touch."
                   "Bienvenue dans notre guilde ! Explorez nos salons ainsi que mes fonctionnalités et commandes."
                    "J'espère que vous passerez une excellente expérience sur notre serveur Discord."
                )
                
                view = WelcomeView(self.bot, member.guild.roles, member.guild)
                await member.send(dm_message, view=view)
                print("DM sent with WelcomeView successfully.")
            except Exception as e:
                print(f"Error in on_member_join: {e}")

class WelcomeView(discord.ui.View):
    def __init__(self, bot, roles, guild):
        super().__init__()
        self.bot = bot
        self.roles = roles
        self.guild = guild

    @discord.ui.button(label="Change your Discord server name", style=discord.ButtonStyle.primary)
    async def change_name_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Please enter your new server name:", ephemeral=True)
        print("Prompted user to enter a new server name.")
        
        def check(m):
            return m.author == interaction.user and isinstance(m.channel, discord.DMChannel)

        try:
            message = await self.bot.wait_for('message', check=check, timeout=60)
            member = self.guild.get_member(interaction.user.id)
            if member:
                await member.edit(nick=message.content)
                await interaction.followup.send(f"Your server name has been changed to {message.content}", ephemeral=True)
                print(f"Nickname changed to {message.content} for {interaction.user}.")
            else:
                await interaction.followup.send("Failed to find your member data. Please contact an admin.", ephemeral=True)
                print("Member data not found in guild.")
        except asyncio.TimeoutError:
            await interaction.followup.send("You took too long to respond. Please try again.", ephemeral=True)
            print("User timed out while entering new server name.")
        except Exception as e:
            print(f"Error in change_name_button: {e}")

    @discord.ui.button(label="Choose Member or Guest", style=discord.ButtonStyle.secondary)
    async def choose_role_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        options = [
            discord.SelectOption(label="🌀-𝕸𝖊𝖒𝖇𝖊𝖗-🌀", description="Join as a Member"),
            discord.SelectOption(label="Guest", description="Join as a Guest"),
        ]
        select = discord.ui.Select(placeholder="Choose your role", options=options)
        select.callback = self.select_callback
        self.add_item(select)
        await interaction.response.send_message("Please choose your role:", view=self, ephemeral=True)
        print("Prompted user to choose a role.")

    async def select_callback(self, interaction: discord.Interaction):
        role_name = interaction.data['values'][0]
        role = discord.utils.get(self.roles, name=role_name)
        member = self.guild.get_member(interaction.user.id)
        if role and member:
            try:
                await member.add_roles(role)
                await interaction.followup.send(f"You have been assigned the {role_name} role.", ephemeral=True)
                print(f"Role '{role_name}' assigned to {interaction.user}.")
            except Exception as e:
                await interaction.followup.send(f"Failed to assign the role {role_name}. Please contact an admin.", ephemeral=True)
                print(f"Error assigning role '{role_name}': {e}")
        else:
            await interaction.followup.send(f"Role '{role_name}' not found or failed to find your member data. Please contact an admin.", ephemeral=True)
            print("Role or member data not found.")

async def setup(bot):
    await bot.add_cog(WelcomeSparta(bot))
    print("WelcomeSparta cog loaded successfully.")
