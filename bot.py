import os
import discord
from dotenv import load_dotenv
from discord import app_commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1473696832352944288
ONBOARDING_LOG_CHANNEL_NAME = "onboarding-log"
LEARNER_ROLE_NAME = "Learner"
import asyncio
intents = discord.Intents.default()
intents.members = True  # IMPORTANT for member join + role assignment

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# ---------- Helpers ----------
async def find_text_channel(guild: discord.Guild, name: str):
    for ch in guild.text_channels:
        if ch.name == name:
            return ch
    return None

def find_role(guild: discord.Guild, name: str):
    for r in guild.roles:
        if r.name == name:
            return r
    return None


# ---------- UI Components ----------
class StartOnboardingView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60 * 10)  # 10 minutes

    @discord.ui.button(label="Start onboarding", style=discord.ButtonStyle.primary)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(OnboardingModal())

    @discord.ui.button(label="Browse resources", style=discord.ButtonStyle.secondary)
    async def resources(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = (
            "Here are good places to start:\n"
            "• #announcements\n"
            "• #start-here (if you have it)\n"
            "• #general for introductions\n\n"
            "If you tell me your cohort, I can point you to the right channels."
        )
        await interaction.response.send_message(msg, ephemeral=True)

    @discord.ui.button(label="Get help", style=discord.ButtonStyle.success)
    async def help(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Reply here with what you need, or tag an admin in #general. 👋",
            ephemeral=True
        )


class OnboardingModal(discord.ui.Modal, title="Guideleaders Onboarding"):
    preferred_name = discord.ui.TextInput(
        label="Preferred name",
        placeholder="e.g., Mike",
        max_length=50
    )
    cohort = discord.ui.TextInput(
        label="Which cohort are you in?",
        placeholder="e.g., MIT Applied Agentic AI – Spring 2026",
        max_length=100
    )
    goal = discord.ui.TextInput(
        label="What do you want to get out of this course?",
        placeholder="One sentence is perfect.",
        style=discord.TextStyle.paragraph,
        max_length=400
    )
    timezone = discord.ui.TextInput(
        label="Your timezone",
        placeholder="e.g., ET / CT / PT / GMT+1",
        max_length=30
    )
    availability = discord.ui.TextInput(
        label="Best meeting windows (roughly)",
        placeholder="e.g., Tue/Thu 7–9pm ET, Sat mornings",
        style=discord.TextStyle.paragraph,
        max_length=200
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Confirm to user
        await interaction.response.send_message(
            "✅ Got it — welcome aboard! I’ve logged your onboarding details.",
            ephemeral=True
        )

        guild = interaction.guild
        user = interaction.user

        # Assign learner role (if exists)
        role = find_role(guild, LEARNER_ROLE_NAME) if guild else None
        if role and isinstance(user, discord.Member):
            try:
                await user.add_roles(role, reason="Guideleaders onboarding completed")
            except discord.Forbidden:
                pass  # missing permissions

        # Log to onboarding channel
        if guild:
            log_ch = await find_text_channel(guild, ONBOARDING_LOG_CHANNEL_NAME)
            if log_ch:
                embed = discord.Embed(
                    title="New Learner Onboarding",
                    description=f"{user.mention} completed onboarding.",
                )
                embed.add_field(name="Preferred name", value=str(self.preferred_name), inline=False)
                embed.add_field(name="Cohort", value=str(self.cohort), inline=False)
                embed.add_field(name="Goal", value=str(self.goal), inline=False)
                embed.add_field(name="Timezone", value=str(self.timezone), inline=True)
                embed.add_field(name="Availability", value=str(self.availability), inline=False)
                await log_ch.send(embed=embed)


# ---------- Events ----------
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    guild = discord.Object(id=GUILD_ID)
    await tree.sync(guild=guild)
    print("Guild commands synced.")
    client.loop.create_task(heartbeat())

@client.event
async def on_member_join(member: discord.Member):
    try:
        await member.send(
            f"Welcome to **Guideleaders**, {member.mention}! 🎉\n\n"
            "I can help you get set up in under 2 minutes.\n"
            "Click below to begin:",
            view=StartOnboardingView()
        )
    except discord.Forbidden:
        # If DMs are closed, optionally post in a public channel
        pass


# ---------- Slash command (manual trigger) ----------
@tree.command(name="onboard", description="Start the onboarding flow")
async def onboard(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Click below to start onboarding:",
        view=StartOnboardingView(),
        ephemeral=True
    )

    @tree.command(name="hello", description="Test command")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello from STARTGuide 🚀", ephemeral=True)

async def heartbeat():
    while True:
         print("Heartbeat: bot process alive")
         await asyncio.sleep(30)

client.run(TOKEN)
