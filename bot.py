import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import json
import datetime
import os
from typing import Literal, Optional

from preset import create_embed

with open('config.json', 'r') as f:
    config = json.load(f)

    token = config["token"]

    logChannelId = config["logChannelId"]
    guildId = config["GuildId"]
    reportChannelId = config["reportChannelId"]
    
    botName = config["botName"]



MY_GUILD = discord.Object(id=guildId)

async def change_bot_status(guild_count, total_member):
    await client.wait_until_ready() 

    while not client.is_closed():
        await client.change_presence(activity=discord.Game(name="docs : projectBot.xyz"), status=discord.Status.idle)

        await asyncio.sleep(4)
        await client.change_presence(activity=discord.Game(name="{} members in {} servers".format(total_member, guild_count)), status=discord.Status.online)

        await asyncio.sleep(4)



class MyBot(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(command_prefix='!', intents=intents)
        self.logChannelId = logChannelId
        self.remove_command("help")
        self.reportChannelId = reportChannelId

    def create_tables(self, guild_id):
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS projects_{guild_id}  
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT,
                                    description TEXT,
                                    created_at TEXT,
                                    updated_at TEXT,
                                    assigned_to TEXT,
                                    owner TEXT,
                                    authorized_to TEXT,
                                    status TEXT)''') 
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS tasks_{guild_id}
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    project_id INTEGER,
                                    name TEXT,
                                    description TEXT,
                                    assigned_to TEXT,
                                    created_at TEXT,
                                    updated_at TEXT,
                                    due_date TEXT,
                                    priority TEXT,
                                    progress_status TEXT,
                                    assigned_user_priority TEXT,
                                    authorized_to TEXT,
                                    comments TEXT,
                                    file_links TEXT,
                                    status TEXT)''')
    async def setup_database(self):
        self.conn = sqlite3.connect('db/mydatabase.db')
        self.cursor = self.conn.cursor()

        print(f"[{datetime.datetime.now()}] [\033[1;35mCONSOLE\033[0;0m]: Database [\033[1;35mSQLite\033[0;0m] setup.") 

        
        try:
            for guild in self.guilds:
                self.create_tables(guild.id)
            print(f"[{datetime.datetime.now()}] [\033[1;35mCONSOLE\033[0;0m]: tables [\033[1;35mSQLite\033[0;0m] created.")
        except Exception as e:
            print(f"[{datetime.datetime.now()}] [\033[91mERROR\033[0;0m]: {e}")

        self.conn.commit()

    async def setup_hook(self):
        await load_all_cogs()

        # guild_ids = [guild.id for guild in self.guilds]
        
        try:
            
            self.tree.copy_global_to(guild=MY_GUILD)
            self.tree.clear_commands(guild=MY_GUILD)
            await self.tree.sync()
            # for guild_id in guild_ids:
                # await self.tree.copy_global_to(guild=discord.Object(id=guild_id))
                # await self.tree.sync(guild=discord.Object(id=guild_id))
            print(f"[{datetime.datetime.now()}] [\033[1;36mCONSOLE\033[0;0m]: Slash commands synchronized with guilds")
        except Exception as e:
            print(f"[{datetime.datetime.now()}] [\033[91mmERROR\033[0;0m]: {e}")
        

    async def close(self):
        await super().close()
        self.conn.close()

intents = discord.Intents.all()
client = MyBot(intents=intents)


async def load_all_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")

@client.event
async def on_ready():
    try:
        await client.setup_database()
            
        print(f"[{datetime.datetime.now()}] [\033[1;32mCONSOLE\033[0;0m]: {botName} ready")

        log_channel = client.get_channel(int(logChannelId))
        now = datetime.datetime.now(datetime.timezone.utc)
        embed = create_embed(client, "info", "Info", f"> {botName} ready", fields={"date :" : f"> {now.strftime('%Y-%m-%d %H:%M:%S')}"})  
        guild_count = len(client.guilds)
        total_members = sum(guild.member_count for guild in client.guilds)
        client.loop.create_task(change_bot_status(guild_count, total_members))
        await log_channel.send(embed=embed)
    except BaseException as error:
        print('An exception occurred: {}'.format(error))


@client.command()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")
    
@client.event
async def on_guild_join(guild):
    try:
        guild_id = guild.id
        client.create_tables(guild_id)
        print(f"[{datetime.datetime.now()}] [\033[1;35mCONSOLE\033[0;0m]: Tables created for guild:  [\033[1;35m{guild.name}\033[0;0m] - [\033[1;35m{guild.id}\033[0;0m] .")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] [\033[91mCONSOLE\033[0;0m]: An error occurred while creating tables for guild:  [\033[1;35m{guild.name}\033[0;0m] - [\033[1;35m{guild.id}\033[0;0m] : {e}")

client.run(token, log_handler=None)