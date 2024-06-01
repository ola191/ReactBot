import discord
import datetime

def create_embed(client: discord.Client, embed_type: str, title: str, description: str, fields: dict = None, footer: bool = True, time: bool = True, thumbnail: bool = True):
    color_mapping = {
        "error": discord.Color.red(),
        "warning": discord.Color.orange(),
        "info": discord.Color.blue(),
        "success": discord.Color.green()
    }

    if embed_type not in color_mapping:
        raise ValueError("Invalid embed type. Choose from: 'error', 'warning', 'info', 'success'.")

    embed = discord.Embed(
        title=title,
        description=description,
        color=color_mapping[embed_type]
    )

    if fields:
        for name, value in fields.items():
            embed.add_field(name=name, value=value, inline=False)

    if footer:
        embed.set_footer(text="Support Server - https://discord.gg/2eqhnRPeyU \nProjectBot made with ❤️ by Olcia")
    
    if time:
        embed.timestamp=datetime.datetime.now(datetime.timezone.utc)

    if thumbnail:
        embed.set_thumbnail(
            url=client.user.avatar.url
        )

    return embed