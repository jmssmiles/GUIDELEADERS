import os
import discord
from dotenv import load_dotenv
from discord import app_commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1473696832352944288

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)

    # Copy global commands to this guild (optional, but helpful)
    tree.copy_global_to(guild=guild)

    synced = await tree.sync(guild=guild)   # <-- guild sync (instant)
    print(f"Logged in as {client.user} | Synced {len(synced)} commands to guild {GUILD_ID}")

@tree.command(name="hello", description="Say hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello from STARTGuide 🚀")

client.run(TOKEN)