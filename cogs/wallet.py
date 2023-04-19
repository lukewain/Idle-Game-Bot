import discord
from discord import Interaction, app_commands
from discord.ext import commands

from asyncpg import Record
import time
from typing import Optional

from src.bot import IdleBot


class Wallet(commands.Cog):
    # Check to make sure that the user has a profile
    async def interaction_check(self, interaction: Interaction[IdleBot]) -> bool:
        profile: Record | None = await interaction.client.pool.fetchrow(
            "SELECT * FROM users WHERE id=$1", interaction.user.id
        )

        if profile is None:
            raise app_commands.CheckFailure(
                "You do not have a profile! Use `/register` to create one"
            )

        else:
            return True

    @app_commands.command(name="wallet")
    async def wallet(
        self, interaction: Interaction[IdleBot], user: Optional[discord.User]
    ):
        if user:
            private: bool = await interaction.client.pool.fetchval(
                "SELECT private FROM users WHERE id=$1", user.id
            )

            if private:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Whoops!",
                        description="You cannot view this user's profile",
                        colour=discord.Colour.red(),
                    ),
                    ephemeral=True,
                )

            wallet_data: Record = await interaction.client.pool.fetchrow(  # type: ignore
                "SELECT * FROM bank WHERE id=$1", user.id
            )

        else:
            wallet_data: Record = await interaction.client.pool.fetchrow(  # type: ignore
                "SELECT * FROM bank WHERE id=$1", interaction.user.id
            )

        embed = discord.Embed(
            title=f"Wallet for {user or interaction.user}",
            colour=discord.Colour.blurple(),
        )

        embed.add_field(name="Balance", value=f"{wallet_data['balance']}")

        return await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Wallet(bot))
