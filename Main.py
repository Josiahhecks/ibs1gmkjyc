import discord
from discord.ext import commands
import json
import asyncio

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Load configuration
try:
    with open("config.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def setup(ctx):
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    # Ask for Main Server ID
    await ctx.send("Please provide the **Main Server ID**:")
    try:
        main_server_msg = await bot.wait_for("message", timeout=60, check=check)
        main_server_id = main_server_msg.content

        # Validate Main Server ID
        main_server = bot.get_guild(int(main_server_id))
        if not main_server:
            await ctx.send("Invalid Main Server ID or bot is not in that server. Please try again.")
            return

        # Ask for Hits Server ID
        await ctx.send("Please provide the **Hits Server ID**:")
        hits_server_msg = await bot.wait_for("message", timeout=60, check=check)
        hits_server_id = hits_server_msg.content

        # Validate Hits Server ID
        hits_server = bot.get_guild(int(hits_server_id))
        if not hits_server:
            await ctx.send("Invalid Hits Server ID or bot is not in that server. Please try again.")
            return

        # Store Server IDs in config
        config["main_server_id"] = main_server_id
        config["hits_server_id"] = hits_server_id
        with open("config.json", "w") as f:
            json.dump(config, f)

        # Confirm setup
        await ctx.send(
            f"Setup complete!\n"
            f"- Main Server: {main_server.name} (`{main_server_id}`)\n"
            f"- Hits Server: {hits_server.name} (`{hits_server_id}`)"
        )

    except asyncio.TimeoutError:
        await ctx.send("Setup timed out. Please try again.")
    except ValueError:
        await ctx.send("Invalid server ID format. Please provide a valid numeric ID.")

@bot.command()
async def stats(ctx, user: discord.Member):
    # Check if Hits Server ID is set
    if "hits_server_id" not in config:
        await ctx.send("Hits Server ID is not set. Please run `/setup` first.")
        return

    # Get the Hits Server
    hits_server = bot.get_guild(int(config["hits_server_id"]))
    if not hits_server:
        await ctx.send("Hits Server not found. Please check the configuration.")
        return

    # Initialize user data
    user_data = {
        "total_sum": 0,
        "total_robux": 0,
        "total_rap": 0,
        "biggest_sum": 0,
        "biggest_robux": 0,
        "total_hits": 0,
    }

    # Scan messages in the Hits Server
    for channel in hits_server.text_channels:
        try:
            async for message in channel.history(limit=1000):  # Adjust limit as needed
                if user.mentioned_in(message):
                    # Extract data from the message
                    content = message.content.lower()
                    if "robux" in content:
                        robux = extract_robux(content)
                        user_data["total_robux"] += robux
                        user_data["biggest_robux"] = max(user_data["biggest_robux"], robux)
                    if "rap" in content:
                        rap = extract_rap(content)
                        user_data["total_rap"] += rap
                    if "sum" in content:
                        sum_value = extract_sum(content)
                        user_data["total_sum"] += sum_value
                        user_data["biggest_sum"] = max(user_data["biggest_sum"], sum_value)
                    user_data["total_hits"] += 1
        except discord.Forbidden:
            continue  # Skip channels the bot doesn't have access to

    # Send embedded response
    embed = discord.Embed(title=f"Stats for {user.name}", color=0x00ff00)
    embed.add_field(name="Total Sum", value=user_data["total_sum"], inline=False)
    embed.add_field(name="Total Robux", value=user_data["total_robux"], inline=False)
    embed.add_field(name="Total RAP", value=user_data["total_rap"], inline=False)
    embed.add_field(name="Biggest Sum", value=user_data["biggest_sum"], inline=False)
    embed.add_field(name="Biggest Robux", value=user_data["biggest_robux"], inline=False)
    embed.add_field(name="Total Hits", value=user_data["total_hits"], inline=False)
    await ctx.send(embed=embed)

def extract_robux(content):
    # Example: Extract Robux value from a message like "User earned 1000 Robux"
    if "robux" in content:
        parts = content.split()
        for part in parts:
            if part.isdigit():
                return int(part)
    return 0

def extract_rap(content):
    # Example: Extract RAP value from a message like "User has 5000 RAP"
    if "rap" in content:
        parts = content.split()
        for part in parts:
            if part.isdigit():
                return int(part)
    return 0

def extract_sum(content):
    # Example: Extract sum value from a message like "User spent 2000 Robux"
    if "sum" in content:
        parts = content.split()
        for part in parts:
            if part.isdigit():
                return int(part)
    return 0

bot.run("MTMzNzE1NDM5NTcyNDMxNjY3Mg.GKodQT.sLYLbFcsu2eCBJ2HSaKSlSKtanGHZnxss0HhiA")
