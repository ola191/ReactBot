import typing
import datetime
from typing import Literal

import json

import discord
from discord.ext import commands
from discord import app_commands

from preset import create_embed


class Report(commands.GroupCog, name="report"):
    def __init__(self, client):
        self.client = client
        self.status = True

    @app_commands.command(name="command", description="Report a command issue")
    async def report_command(self, interaction: discord.Interaction, command: str, description: str):
        try:
            guild_name = interaction.guild.name if interaction.guild else "Direct Message"
            guild_id = interaction.guild.id if interaction.guild else "Direct Message"
            user_id = interaction.user.id
            user_name = interaction.user.name
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            report_content = f"**Command Issue Report**\n\n"
            report_content += f"**Guild ID:** {guild_id}\n"
            report_content += f"**Guild:** {guild_name}\n"
            report_content += f"**User ID:** {user_id}\n"
            report_content += f"**User Name:** {user_name}\n"
            report_content += f"**Time:** {current_time}\n\n"
            report_content += f"**Command:** {command}\n"
            report_content += f"**Description:** {description}\n"

            await self.send_report(interaction, "Report", report_content)
        except Exception as e:
            print(f"An error occurred while reporting a command issue: {e}")
            await interaction.response.send_message("An error occurred while reporting the command issue.", ephemeral=True)

    @app_commands.command(name="error", description="Report an error")
    async def report_error(self, interaction: discord.Interaction, error_type:  Literal[
        "Function Error",
        "Interface Error",
        "Communication Error",
        "Login Error",
        "Display Error",
        "Access Error",
        "Connectivity Error",
        "Configuration Error",
        "Other Error"
    ], description: str):
        try:
            guild_id = interaction.guild.id if interaction.guild else "Direct Message"
            guild_name = interaction.guild.name if interaction.guild else "Direct Message"
            user_id = interaction.user.id
            user_name = interaction.user.name
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            report_content = f"**Error Issue Report**\n\n"
            report_content += f"**Guild ID:** {guild_id}\n"
            report_content += f"**Guild:** {guild_name}\n"
            report_content += f"**User ID:** {user_id}\n"
            report_content += f"**User Name:** {user_name}\n"
            report_content += f"**Time:** {current_time}\n\n"
            report_content += f"**Error:** {error_type}\n"
            report_content += f"**Description:** {description}\n"

            await self.send_report(interaction, "Report", report_content)
        except Exception as e:
            print(f"An error occurred while reporting a error issue: {e}")
            await interaction.response.send_message("An error occurred while reporting the error issue.", ephemeral=True)

    @report_command.autocomplete("command")
    async def report_command_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> typing.List[app_commands.Choice[str]]:
        try:
            choices = []
            for com in self.client.tree.walk_commands():
                if isinstance(com, app_commands.Command):
                    group_name = com.parent.name if com.parent else ""
                    command_name = f"{group_name} {com.name}" if group_name else com.name
                    if current.lower() in command_name.lower():
                        choices.append(app_commands.Choice(name=command_name, value=command_name))
            return choices
        except Exception as e:
            print(f"An error occurred while autocompleting commands: {e}")
            return []



    async def send_report(self, interaction, title, content):
        try:
            report_channel_id = self.client.config.get("reportChannelId")
            if report_channel_id:
                report_channel = self.client.get_channel(int(self.client.reportChannelId))
                if report_channel:
                    em = discord.Embed(
                        title=title,
                        description=content,
                        color=discord.Color.blurple()
                    )
                    await report_channel.send(embed=em)
                    embed = create_embed(self.client, "success", "Success", f"Report sent successfully.")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_message("Report channel not found!", ephemeral=True)
            else:
                await interaction.response.send_message("Report channel ID not configured!", ephemeral=True)
        except Exception as e:
            print(f"An error occurred while sending the report: {e}")

async def setup(client):
    with open('./config.json', 'r') as f:
        client.config = json.load(f)

    if Report(client).status:
        print(f"[{datetime.datetime.now()}] [\033[1;33mCONSOLE\033[0;0m]: Cog [\033[1;33m{Report.__name__}\033[0;0m] loaded : Status [\033[1;32mEnable\033[0;0m]")
        await client.add_cog(Report(client))
    else:
        print(f"[{datetime.datetime.now()}] [\033[1;33mCONSOLE\033[0;0m]: Cog [\033[1;33m{Report.__name__}\033[0;0m] loaded : Status [\033[1;31mUnable\033[0;0m]")
