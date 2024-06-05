import sqlite3
from typing import Literal, Union
import discord
from discord.ext import commands
from discord import app_commands
import datetime

from preset import create_embed

class Task(commands.GroupCog, name="task"):
    def __init__(self, client):
        self.client = client
        self.status = True
        self.conn = sqlite3.connect('db/mydatabase.db')
        self.cursor = self.conn.cursor()

    @app_commands.command(name="add", description="Add a new task")
    async def add_task(self, interaction: discord.Interaction, project_id: int, name: str, description: str, assigned_to: discord.Member, authorized_to: discord.Member, priority: int):
        try:
            created_at = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute(f'''INSERT INTO tasks_{interaction.guild.id} (project_id, name, description, assigned_to, authorized_to, created_at, priority)
                                     VALUES (?, ?, ?, ?, ?, ?, ?)''', (project_id, name, description, assigned_to.id, authorized_to.id, created_at, priority))
            task_id = self.cursor.lastrowid
            self.conn.commit()
            embed = create_embed(self.client,"success", "Success", f"Task '{name}' added successfully. Task Id : {task_id}")
            await interaction.response.send_message(embed = embed)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}")

    @app_commands.command(name="list", description="List all tasks")
    async def list_tasks(self, interaction: discord.Interaction, page: int = 1):
        try:
            start_index = (page - 1) * 10
            end_index = start_index + 10
            self.cursor.execute(f'''SELECT * FROM tasks_{interaction.guild.id} ORDER BY id LIMIT ?, ?''', (start_index, end_index))
            tasks = self.cursor.fetchall()

            if tasks:
                for task in tasks:
                    
                    assigned_to = interaction.guild.get_member(task[8])
                    authorized_to = interaction.guild.get_member(task[9])

                    embed = discord.Embed(title="Task Information", color=0x7289DA)
                    embed.add_field(name="ID", value=task[0], inline=False)
                    embed.add_field(name="Project ID", value=task[1], inline=False)
                    embed.add_field(name="Name", value=task[2], inline=False)
                    embed.add_field(name="Description", value=task[3], inline=False)
                    embed.add_field(name="Assigned To", value=assigned_to.name if assigned_to else "Unknown", inline=False)
                    embed.add_field(name="Authorized To", value=authorized_to.name if authorized_to else "Unknown", inline=False)
                    embed.add_field(name="Created At", value=task[4], inline=False)
                    embed.add_field(name="Priority", value=task[6], inline=False)
                    await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("No tasks found.")
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}")

    @app_commands.command(name="delete", description="Delete a task")
    async def delete_task(self, interaction: discord.Interaction, task_id: int):
        try:
            self.cursor.execute(f'''DELETE FROM tasks_{interaction.guild.id} WHERE id = ?''', (task_id,))
            self.conn.commit()
            await interaction.response.send_message("Task deleted successfully!")
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}")

    # @app_commands.command(name="updatetask", description="Update a task")
    # async def update_task(self, interaction: discord.Interaction, task_id: int, **kwargs):
    #     try:
    #         updates = ', '.join([f"{key} = ?" for key in kwargs])
    #         values = tuple(kwargs.values()) + (task_id,)
    #         self.cursor.execute(f'''UPDATE tasks_{interaction.guild.id} SET {updates} WHERE id = ?''', values)
    #         self.conn.commit()
    #         await interaction.response.send_message("Task updated successfully!")
    #     except Exception as e:
    #         await interaction.response.send_message(f"An error occurred: {e}")

    @app_commands.command(name="change", description="Change a task field")
    async def change(self, interaction: discord.Interaction, task_id: int, field: Literal['project_id', 'name', 'description', 'assigned_to', 'due_date', 'priority', 'progress_status', 'assigned_user_priority', 'authorized_to', 'comments', 'file_links', 'status'], action: Literal['add', 'remove', 'replace'], value: Union[str, None] = None, member: Union[discord.Member, None] = None):
        try:
            if field in ['assigned_to', 'authorized_to', 'assigned_user_priority']:
                if member is None:
                    await interaction.response.send_message("Member argument is required for this field.")
                    return

                self.cursor.execute(f'''SELECT {field} FROM tasks_{interaction.guild.id} WHERE id = ?''', (task_id,))
                result = self.cursor.fetchone()
                if not result:
                    await interaction.response.send_message("Task not found.")
                    return

                current_values = result[0].split(",") if result[0] else []

                if action == 'add':
                    if str(member.id) not in current_values:
                        current_values.append(str(member.id))
                elif action == 'remove':
                    if str(member.id) in current_values:
                        current_values.remove(str(member.id))
                elif action == 'replace':
                    current_values = [str(member.id)]

                new_values = ",".join(current_values)
                self.cursor.execute(f'''UPDATE tasks_{interaction.guild.id} SET {field} = ? WHERE id = ?''', (new_values, task_id))

            else:
                if value is None:
                    await interaction.response.send_message("Value argument is required for this field.")
                    return

                self.cursor.execute(f'''UPDATE tasks_{interaction.guild.id} SET {field} = ? WHERE id = ?''', (value, task_id))

            self.conn.commit()
            await interaction.response.send_message(f"Task {task_id} updated successfully!")

        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}")



async def setup(client):
    if Task(client).status:
        print(f"[{datetime.datetime.now()}] [\033[1;33mCONSOLE\033[0;0m]: Cog [\033[1;33m{Task.__name__}\033[0;0m] loaded : Status [\033[1;32mEnable\033[0;0m]")
        await client.add_cog(Task(client))
    else:
        print(f"[{datetime.datetime.now()}] [\033[1;33mCONSOLE\033[0;0m]: Cog [\033[1;33m{Task.__name__}\033[0;0m] loaded : Status [\033[1;31mUnable\033[0;0m]")