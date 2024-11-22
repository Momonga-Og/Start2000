import discord
from discord.ext import commands
import os

# Intents for the bot
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True  # Make sure the intent is set correctly

# Prefix for commands
bot = commands.Bot(command_prefix="!", intents=intents)

# Function to load cogs from the 'cogs' folder
def load_cogs():
    # Ensure the 'cogs' folder exists
    cog_folder = './cogs'
    if os.path.exists(cog_folder):
        for filename in os.listdir(cog_folder):
            if filename.endswith('.py') and filename != '__init__.py':  # Skip '__init__.py'
                try:
                    # Dynamically load each cog in the cogs folder
                    bot.load_extension(f'cogs.{filename[:-3]}')  # Removing .py from filename
                    print(f"Loaded cog: {filename}")
                except Exception as e:
                    print(f"Failed to load cog {filename}: {e}")
    else:
        print("Error: 'cogs' folder does not exist.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('Bot is ready!')

# Load all cogs
load_cogs()

# Run the bot with the token from the environment variable
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("Error: DISCORD_TOKEN environment variable not set.")
