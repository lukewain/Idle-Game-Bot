from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands

import traceback

if TYPE_CHECKING:
    from .bot import IdleBot


class IdleTree(app_commands.CommandTree):
    async def on_error(
        self,
        interaction: discord.Interaction[IdleBot],
        error: app_commands.AppCommandError,
        /,
    ):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(error, ephemeral=True)

        else:
            print(traceback.format_exc())
