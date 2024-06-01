import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import datetime

from typing import Literal

from preset import create_embed

class Project(commands.GroupCog, name="project"):
    def __init__(self, client):
        self.client = client
        self.conn = sqlite3.connect('mydatabase.db')
        self.cursor = self.conn.cursor()
        self.status = True

    def project_exists(self, name: str, guild_id: int):
        self.cursor.execute(f'''SELECT name FROM projects_{guild_id} WHERE LOWER(name)=?''', (name.lower(),))
        return self.cursor.fetchone() is not None

    @app_commands.command(name="create", description="Create a new project")
    async def create_project(self, interaction: discord.Interaction, name: str, description: str):
        try:
            guild_id = interaction.guild.id

            if self.project_exists(name, guild_id):
                embed = create_embed(self.client,"info", "Info", f"Project with name '{name}' already exists.")
                await interaction.response.send_message(embed = embed)
                return

            current_time = datetime.datetime.utcnow().isoformat()


            self.cursor.execute(f'''INSERT INTO projects_{guild_id} (name, description, created_at, updated_at, owner) 
                                    VALUES (?, ?, ?, ?, ?)''', (name, description, current_time, current_time, str(interaction.user.id)))
            
            self.conn.commit()
            
            embed = create_embed(self.client,"success", "Success", f"Project '{name}' created successfully.")
            await interaction.response.send_message(embed = embed)
        except Exception as e:
            embed = create_embed(self.client,"error", "Error", f"An error occurred: {e}")
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="show", description="Show projects by name, owner or ID")
    async def show_projects(self, interaction: discord.Interaction, query: str):
        try:
            guild_id = interaction.guild.id
            self.cursor.execute(f'''SELECT * FROM projects_{guild_id} WHERE LOWER(name)=? OR LOWER(owner)=? OR id=?''', (query.lower(), query.lower(), query))
            projects = self.cursor.fetchall()
            if projects:
                embed = discord.Embed(title="Projects found", color=0x7289DA)
                for project in projects:
                    owner = await self.client.fetch_user(int(project[6]))
                    assigned_to_ids = project[5].split(",") if project[5] else []
                    authorized_to_ids = project[7].split(",") if project[7] else []

                    assigned_to_names = [await self.client.fetch_user(int(user_id)) for user_id in assigned_to_ids]
                    authorized_to_names = [await self.client.fetch_user(int(user_id)) for user_id in authorized_to_ids]

                    assigned_to_display = ", ".join([user.name for user in assigned_to_names])
                    authorized_to_display = ", ".join([user.name for user in authorized_to_names])

                    embed.add_field(name="ID", value=project[0], inline=False)
                    embed.add_field(name="Name", value=project[1], inline=False)
                    embed.add_field(name="Description", value=project[2], inline=False)
                    embed.add_field(name="Owner", value=owner.name, inline=False)
                    if assigned_to_display != "":
                        embed.add_field(name="Assigned To", value=assigned_to_display, inline=False)
                    if  authorized_to_display != "":
                        embed.add_field(name="Authorized To", value=authorized_to_display, inline=False)
                    if project[8] is not None:
                        embed.set_footer(text=f"Status : {project[8]}")
                    else:
                        embed.set_footer(text=f"Status : None")
                    embed.set_thumbnail(
                        url=self.client.user.avatar.url
                    )
                
                    embed.set_footer(text="Support Server - https://discord.gg/2eqhnRPeyU \nProjectBot made with ❤️ by Olcia")

                await interaction.response.send_message(embed=embed)
            else:
                embed = create_embed(self.client,"info", "Info", f"No projects found with NAME, OWNER or ID : '**{query}**'.")
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = create_embed(self.client,"error", "Error", f"An error occurred: {e}")
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="list", description="List projects")
    async def list_projects(self, interaction: discord.Interaction, page: int = 1, visible: bool = False):
        try:
            if page <= 0:
                raise ValueError("Page number must be a positive integer.")
            
            guild_id = interaction.guild.id
            self.cursor.execute(f"SELECT * FROM projects_{guild_id} ORDER BY id ASC")
            projects = self.cursor.fetchall()

            if not projects:
                embed = create_embed(self.client, "info", "Info", "No projects found.")
                await interaction.response.send_message(embed=embed)
                return

            projects_per_page = 10
            start_index = (page - 1) * projects_per_page
            end_index = min(start_index + projects_per_page, len(projects))
            
            embed_header = discord.Embed(
                title=f"List of Projects - Page {page}",
                description=f"Showing projects {start_index + 1} to {end_index} of {len(projects)}",
                color=0x7289DA
            )
            await interaction.response.send_message(embed=embed_header)
            
            for index, project in enumerate(projects[start_index:end_index], start=start_index):
                
                owner = await self.client.fetch_user(int(project[6]))
                assigned_to_ids = project[5].split(",") if project[5] else []
                authorized_to_ids = project[7].split(",") if project[7] else []

                assigned_to_names = [await self.client.fetch_user(int(user_id)) for user_id in assigned_to_ids]
                authorized_to_names = [await self.client.fetch_user(int(user_id)) for user_id in authorized_to_ids]

                assigned_to_display = ", ".join([user.name for user in assigned_to_names])
                authorized_to_display = ", ".join([user.name for user in authorized_to_names])

                embed_project = discord.Embed(title="", color=0x7289DA)
                embed_project.add_field(name=f"ID : {project[0]}", value="", inline=False)
                embed_project.add_field(name=f"Name : {project[1]}", value="", inline=False)
                embed_project.add_field(name=f"Description : {project[2]}", value="", inline=False)
                # embed_project.add_field(name="Owner", value=owner.name, inline=False)
                # if assigned_to_display:
                    # embed_project.add_field(name="Assigned To", value=assigned_to_display, inline=False)
                # if authorized_to_display:
                    # embed_project.add_field(name="Authorized To", value=authorized_to_display, inline=False)
                # if project[8] is not None:
                    # embed_project.set_footer(text=f"Status : {project[8]}")
                # else:
                    # embed_project.set_footer(text=f"Status : None")
                # embed_project.set_thumbnail(url=self.client.user.avatar.url)
                if visible:
                    channelId = self.client.get_channel(int(interaction.channel.id))
                    await channelId.send(embed=embed_project)
                else:
                    await interaction.followup.send(embed=embed_project)
                
                # if index == len(projects) - 1:
                    # embed_project_last = discord.Embed(title="", color=0x7289DA)
                    # embed_project_last.set_thumbnail(url=self.client.user.avatar.url)
                    # await interaction.followup.send(embed=embed_project_last)

        except Exception as e:
            embed_error = create_embed(self.client, "error", "Error", f"An error occurred: {e}")
            await interaction.response.send_message(embed=embed_error)

    @app_commands.command(name="change", description="Change project details")
    async def change_project(self, interaction: discord.Interaction, project_id: int, field: Literal['name', 'description', 'status', 'assigned_to', 'owner', 'authorized_to'], action: Literal["add", "remove", "replace"], value: str = None, member: discord.Member = None):
        try:
            guild_id = interaction.guild.id
            self.cursor.execute(f'''SELECT {field} FROM projects_{guild_id} WHERE id=?''', (project_id,))
            current_value = self.cursor.fetchone()[0]

            if field in ['assigned_to', 'owner', 'authorized_to']:
                if member is None:
                    embed = create_embed(self.client, "error", "Error", f"You must specify a user to add, remove, or replace.")
                    await interaction.response.send_message(embed=embed)
                    return
                values = current_value.split(",") if current_value else []

                if action == 'add':
                    if str(member.id) in values:
                        embed = create_embed(self.client, "info", "Info", f"User '{member.name}' is already in {field}.")
                        await interaction.response.send_message(embed=embed)
                        return
                    values.append(str(member.id))
                elif action == 'remove':
                    if str(member.id) not in values:
                        embed = create_embed(self.client, "info", "Info", f"User '{member.name}' is not in {field}.")
                        await interaction.response.send_message(embed=embed)
                        return
                    if field == 'owner' and len(values) == 1:
                        embed = create_embed(self.client, "warning", "Warning", f"Cannot remove the only owner.")
                        await interaction.response.send_message(embed=embed)
                        return
                    values.remove(str(member.id))
                elif action == 'replace':
                    values = [str(member.id)]
                updated_value = ",".join(values)
            elif field in ['name', 'description', 'status']:
                if value is None:
                    embed = create_embed(self.client, "warning", "Warning", f"No value specified. You need to specify a value for {field}, not a Discord member object.")
                    await interaction.response.send_message(embed=embed)
                    return
                if action != "replace":
                    embed = create_embed(self.client, "warning", "Warning", f"Cannot add or remove status, use replace instead.")
                    await interaction.response.send_message(embed=embed)
                    return
                updated_value = value

            self.cursor.execute(f'''UPDATE projects_{guild_id} SET {field}=?, updated_at=? WHERE id=?''', (updated_value, datetime.datetime.utcnow().isoformat(), project_id))
            self.conn.commit()
            embed = create_embed(self.client, "success", "Success", f"Project with ID '{project_id}' updated successfully.")
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = create_embed(self.client, "error", "Error", f"An error occurred: {e}")
            await interaction.response.send_message(embed=embed)

    # @app_commands.command(name="add", description="Add users to a project")
    # async def add_users_to_project(self, interaction: discord.Interaction, project_id: int, user: discord.User):
    #     try:
    #         self.cursor.execute('''UPDATE projects SET users=users||? WHERE id=?''', (str(user.id), project_id))
    #         self.conn.commit()
    #         embed = create_embed(self.client,"success", "Success", f"User added to project with ID '{project_id}' successfully.")
    #         await interaction.response.send_message(f"embed=embed")
    #     except Exception as e:
    #         embed = create_embed(self.client,"error", "Error", f"An error occurred: {e}")
    #         await interaction.response.send_message(embed=embed)

    @app_commands.command(name="delete", description="Delete a project by ID")
    async def delete_project(self, interaction: discord.Interaction, project_id: int):
        try:
            guild_id = interaction.guild.id
            self.cursor.execute(f'''SELECT id, owner FROM projects_{guild_id} WHERE id=?''', (project_id,))
            project = self.cursor.fetchone()

            if not project:
                embed = create_embed(self.client, "info", "Info", f"No project found with ID: {project_id}.")
                await interaction.response.send_message(embed=embed)
                return

            if int(project[1]) != interaction.user.id:
                embed = create_embed(self.client, "info", "Info", "You are not the owner of this project. Only the owner can delete it.")
                await interaction.response.send_message(embed=embed)
                return

            confirmation_embed = create_embed(self.client, "info", "Confirmation", f"Are you sure you want to delete project with ID {project_id}? Type 'yes' to confirm or 'no' to cancel. This message will expire in **10 seconds**.")
            await interaction.response.send_message(embed=confirmation_embed)
            confirmation_msg = await interaction.original_response()

            async def countdown():
                for i in range(9, 0, -1):
                    confirmation_embed.description = f"Are you sure you want to delete project with ID {project_id}? Type 'yes' to confirm or 'no' to cancel. This message will expire in **{i} seconds**."
                    await confirmation_msg.edit(embed=confirmation_embed)
                    await asyncio.sleep(1)
                await confirmation_msg.edit(embed=confirmation_embed)

            def check(message):
                return message.author.id == interaction.user.id and message.channel == interaction.channel and message.content.lower() in ['yes', 'no']

            countdown_task = asyncio.create_task(countdown())
            try:
                msg = await self.client.wait_for('message', check=check, timeout=11.0)
                countdown_task.cancel()
                if msg.content.lower() == 'yes':
                    self.cursor.execute(f'''DELETE FROM projects_{guild_id} WHERE id=?''', (project_id,))
                    self.conn.commit()
                    success_embed = create_embed(self.client, "success", "Success", f"Project with ID {project_id} has been deleted successfully.")
                    await interaction.followup.send(embed=success_embed)
                else:
                    cancel_embed = create_embed(self.client, "info", "Cancellation", "Operation cancelled.")
                    await interaction.followup.send(embed=cancel_embed)
            except asyncio.TimeoutError:
                confirmation_embed.description = f"Operation delete project with ID {project_id}. Time's up! ⏰"
                await confirmation_msg.edit(embed=confirmation_embed)
        except Exception as e:
            error_embed = create_embed(self.client, "error", "Error", f"An error occurred: {e}")
            await interaction.followup.send(embed=error_embed)


            
async def setup(client):
    if Project(client).status:
        print(f"[{datetime.datetime.now()}] [\033[1;33mCONSOLE\033[0;0m]: Cog [\033[1;33m{Project.__name__}\033[0;0m] loaded : Status [\033[1;32mEnable\033[0;0m]")
        await client.add_cog(Project(client))
    else:
        print(f"[{datetime.datetime.now()}] [\033[1;33mCONSOLE\033[0;0m]: Cog [\033[1;33m{Project.__name__}\033[0;0m] loaded : Status [\033[1;31mUnable\033[0;0m]")