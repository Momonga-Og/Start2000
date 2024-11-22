import discord
from discord.ext import commands
import os

# Intents for the bot
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

# Prefix for commands
bot = commands.Bot(command_prefix="!", intents=intents)

# Function to load cogs from the 'cogs' folder
def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"Loaded cog: {filename}")
            except Exception as e:
                print(f"Failed to load cog {filename}: {e}")

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
