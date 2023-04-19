import typing
import discord
from discord import app_commands
from discord.ext import commands


class Development(commands.Cog):
    development = app_commands.Group(
        name="development", description="Commands for use during development"
    )

    @development.command(name="schema", description="Allows reloading of schema files")
    @app_commands.choices(
        action=[
            app_commands.Choice(name="load", value="load"),
            app_commands.Choice(name="drop", value="drop"),
        ]
    )
    async def schema(
        self, interaction: discord.Interaction, action: app_commands.Choice[str]
    ):
        ...
