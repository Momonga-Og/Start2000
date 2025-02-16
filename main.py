import discord
from discord.ext import commands
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

OWNER_ID = 486652069831376943  # Replace with your Discord user ID
TOKEN = os.getenv('DISCORD_TOKEN')

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    await sync_commands()

async def sync_commands():
    if not hasattr(bot, 'synced'):
        try:
            synced = await bot.tree.sync()
            logger.info(f"Synced {len(synced)} commands")
            bot.synced = True
        except Exception as e:
            logger.exception("Failed to sync commands")

@bot.command(name='memory')
async def memory_command(ctx):
    await ctx.send("Memory management has been removed from this bot.")

@bot.event
async def on_message(message: discord.Message):
    if message.author != bot.user:
        logger.info(f"Message from {message.author}: {message.content}")

    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        await forward_dm(message)
    await bot.process_commands(message)

async def forward_dm(message: discord.Message):
    owner = await bot.fetch_user(OWNER_ID)
    if owner:
        await owner.send(f"Message from {message.author}: {message.content}")

@bot.event
async def on_disconnect():
    logger.info("Bot disconnected")

@bot.event
async def on_error(event: str, *args, **kwargs):
    logger.exception(f"An error occurred in event {event}")

@bot.event
async def on_close():
    logger.info("Bot is closing")
    await close_sessions()

async def close_sessions():
    logger.info("Performing cleanup before closing...")

EXTENSIONS = [
    'cogs.admin',
    'cogs.relocate', 'cogs.watermark', 'cogs.talk', 'cogs.role',
    'cogs.watermark_user', 'cogs.metiers',
    'cogs.image_converter', 'cogs.startguild',
    'cogs.alerts', 'cogs.welcomesparta',
    'cogs.super', 'cogs.translator', 'cogs.voice',
]

async def load_extensions():
    for extension in EXTENSIONS:
        try:
            await bot.load_extension(extension)
            logger.info(f"Loaded extension: {extension}")
        except Exception as e:
            logger.exception(f"Failed to load extension {extension}")

async def main():
    async with bot:
        await load_extensions()
        if not TOKEN:
            logger.error("Bot token not found")
            return
        try:
            await bot.start(TOKEN)
        except discord.LoginFailure:
            logger.error("Invalid token")
        except Exception as e:
            logger.exception("Failed to start the bot")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception("Bot encountered an error and stopped")
