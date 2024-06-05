import datetime

import discord
from discord.ext import commands
from discord import app_commands

class Mod(commands.GroupCog, name="mod"):
    def __init__(self, client):
        self.client = client
        self.status = True

    @app_commands.command(name="purge", description="Clears a specified number of messages optionally from a specific user.")
    async def purge(self, interaction: discord.Interaction, amount: int, member: discord.Member = None):
        if amount <= 0:
            await interaction.response.send_message("Please provide a valid number of messages to delete.", ephemeral=True)
            return

        if interaction.channel is None:
            await interaction.response.send_message("This command cannot be used in a private message.", ephemeral=True)
            return

        if not interaction.channel.permissions_for(interaction.guild.me).manage_messages:
            await interaction.response.send_message("I don't have permission to manage messages.", ephemeral=True)
            return

        try:
            if not member:
                deleted_messages = await interaction.channel.purge(limit=amount, bulk=False)
            else:
                deleted_messages = await interaction.channel.purge(limit=amount, check=lambda m: m.author == member if member else None, bulk=False)

            if member:
                await interaction.response.send_message(f"Deleted {len(deleted_messages)} messages for {member.display_name}.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Deleted {len(deleted_messages)} messages.", ephemeral=True)
        except discord.errors.NotFound:
            print("Interaction not found or expired. Ignoring the command.")
            await interaction.response.send_message(f"Deleted {len(deleted_messages)} messages.", ephemeral=True)

        except Exception as error:
            print(f'An exception occurred: {error}')
    
    async def report_messagee(self, interaction: discord.Interaction, message: discord.Message) -> None:
        await interaction.response.send_message(
            f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
        )

        log_channel = interaction.guild.get_channel(int(self.client.logChannelId))
        print(f"channel : {log_channel}")
        embed = discord.Embed(title='Reported Message')
        if message.content:
            embed.description = message.content

        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.timestamp = message.created_at

        url_view = discord.ui.View()
        url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))
        
        await log_channel.send(embed=embed, view=url_view)

async def setup(client):
    if Mod(client).status:
        print(f"[{datetime.datetime.now()}] [\033[1;33mCONSOLE\033[0;0m]: Cog [\033[1;33m{Mod.__name__}\033[0;0m] loaded : Status [\033[1;32mEnable\033[0;0m]")
        await client.add_cog(Mod(client))
    else:
        print(f"[{datetime.datetime.now()}] [\033[1;33mCONSOLE\033[0;0m]: Cog [\033[1;33m{Mod.__name__}\033[0;0m] loaded : Status [\033[1;31mUnable\033[0;0m]")