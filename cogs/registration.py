import discord
from discord.ext import commands
from discord import app_commands

from asyncpg import Record
import time

from src.bot import IdleBot


class Registration(commands.Cog):
    # Commands to register with the bot
    # Each user gets a starting balance of $10
    @app_commands.command(
        name="register", description="Register a profile with the bot"
    )
    async def register(self, interaction: discord.Interaction[IdleBot]):
        # Check to see if the user has already registered
        user_already_exists: Record | None = await interaction.client.pool.fetchrow(
            "SELECT * FROM users WHERE id=$1", interaction.user.id
        )

        print("Searched database.")

        if user_already_exists is not None:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Whoops!",
                    description="You are already registered!",
                    colour=discord.Colour.red(),
                ),
                ephemeral=True,
            )

        print("User does not exist.")

        await interaction.client.pool.execute(
            "INSERT INTO users (id, origin_guild, last_updated) VALUES ($1, $2, $3)",
            interaction.user.id,
            interaction.guild.id,  # type: ignore
            round(time.time()),
        )

        await interaction.client.pool.execute(
            "INSERT INTO bank (id, balance) VALUES ($1, $2)", interaction.user.id, 10
        )

        print("Added user.")

        return await interaction.response.send_message(
            embed=discord.Embed(
                title="Success!",
                description="You have been registered!",
                colour=discord.Colour.green(),
            )
        )

    # Command to unregister from the bot
    @app_commands.command(name="leave", description="Delete your profile from the bot.")
    async def leave(self, interaction: discord.Interaction[IdleBot]):
        # Check to see if the user has already registered
        user_already_exists: Record | None = await interaction.client.pool.fetchrow(
            "SELECT * FROM users WHERE id=$1", interaction.user.id
        )

        if user_already_exists is None:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Whoops!",
                    description="You don't have an account!",
                    colour=discord.Colour.red(),
                )
            )

        await interaction.client.pool.execute(
            "DELETE FROM users WHERE id=$1", interaction.user.id
        )

        await interaction.client.pool.execute(
            "DELETE FROM bank WHERE id=$1", interaction.user.id
        )

        return await interaction.response.send_message(
            embed=discord.Embed(
                title="Success!",
                description="Your account has been deleted.",
                colour=discord.Colour.green(),
            )
        )


async def setup(bot):
    await bot.add_cog(Registration(bot))
