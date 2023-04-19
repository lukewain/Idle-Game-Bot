import discord
from discord import app_commands
from discord.ext import commands

import math
from asyncpg import Record
import typing

from src.bot import IdleBot
from components import paginator


class Upgrader(commands.Cog):
    # Check for interactions
    async def interaction_check(
        self, interaction: discord.Interaction[IdleBot]
    ) -> bool:
        profile: Record | None = await interaction.client.pool.fetchrow(
            "SELECT * FROM users WHERE id=$1", interaction.user.id
        )

        if profile is None:
            raise app_commands.CheckFailure(
                "You do not have a profile! Use `/register` to create one"
            )

        else:
            return True

    # Autocomplete for upgrades
    async def upgrade_autocomplete(
        self, interaction: discord.Interaction[IdleBot], current: str
    ) -> typing.List[app_commands.Choice]:
        upgrades = await interaction.client.pool.fetch("SELECT * FROM upgrades")

        return [
            app_commands.Choice(name=upgr["item_name"], value=upgr["item_name"])
            for upgr in upgrades
            if current.lower() in upgr["item_name"].lower()
        ]

    upgrades = app_commands.Group(
        name="upgrades", description="All the commands for upgrading your profile!"
    )

    # Command to view upgrades
    @upgrades.command(
        name="view", description="Allows you to view all the available upgrades"
    )
    async def upgrades_view(self, interaction: discord.Interaction[IdleBot]):
        upgrs: typing.List[Record] = await interaction.client.pool.fetch(
            "SELECT * FROM upgrades"
        )

        pag = paginator.Paginator(page_size=100)

        for record in upgrs:
            pag.add_line(f"Item: `{record['item_name']}`\nCost: `${record['price']}`")

        embed = discord.Embed(
            colour=discord.Colour.blurple(), title="Upgrades", description=pag.pages[0]
        )

        v = paginator.PaginatorView(pag, interaction.user, embed=embed)

        await interaction.response.send_message(view=v, embed=embed)

    @upgrades.command(name="buy", description="Purchase an upgrade from the shop.")
    @app_commands.autocomplete(upgrade=upgrade_autocomplete)
    async def upgrades_buy(
        self, interaction: discord.Interaction[IdleBot], upgrade: str
    ):
        upgr: Record | None = await interaction.client.pool.fetchrow(
            "SELECT * FROM upgrades WHERE item_name=$1 LIMIT 1", upgrade
        )

        if upgr is None:
            return interaction.response.send_message(
                embed=discord.Embed(
                    title="Whoops",
                    description="Something went wrong! The bot developer knows about this!",
                    colour=discord.Colour.red(),
                )
            )

        owned_upgr: Record | None = await interaction.client.pool.fetchrow(
            "SELECT * FROM user_upgrades WHERE name=$1 AND id=$2",
            upgrade,
            interaction.user.id,
        )

        if not owned_upgr:
            owned = 0
            upgr_price: int = upgr["price"]
        else:
            owned: int = owned_upgr["count"]
            upgr_price: int = (
                upgr["price"]
                * math.pow(2.5, math.floor((owned - 1) / 10))
                * math.pow(1.25, owned - 1)
            )

        """
        Type ignored due to wallet never returning None. This is due to 
        the check which does not allow the command to run unless the user has a wallet
        """
        usr_bank: Record = await interaction.client.pool.fetchrow(  # type: ignore
            "SELECT * FROM bank WHERE id=$1 LIMIT 1", interaction.user.id
        )

        if usr_bank["balance"] < upgr_price:
            return interaction.response.send_message(
                embed=discord.Embed(
                    title="Whoah There",
                    description="You do not have enough money for this!",
                )
                .add_field(name="Cost", value=f"${upgr_price}")
                .add_field(name="Balance", value=f"${usr_bank['balance']}")
            )

        # Purchase upgrade logic

        """
        TODO

        - Remove purchase cost from user bal
        - Add one to owned upgrades for that specific upgrade, if upgrade does not exist create record for it
        - Alert user that their upgrade has been purchased and notify them of how many they own

        """

        new_bal = await interaction.client.pool.fetchval(
            "UPDATE bank SET balance = balance - 10 WHERE id=$1 RETURNING balance",
            interaction.user.id,
        )

        if owned == 0:
            new_owned_upgr = await interaction.client.pool.execute(
                "INSERT INTO user_upgrades (id, name, count) VALUES ($1, $2, default)",
                interaction.user.id,
                upgrade,
            )
            new_owned_upgr = await interaction.client.pool.fetchval(
                "SELECT count FROM user_upgrades WHERE id=$1 AND name=$2",
                interaction.user.id,
                upgrade,
            )
        else:
            new_owned_upgr = await interaction.client.pool.fetchval(
                "UPDATE user_upgrades SET count = count + 1 WHERE id=$1 AND name=$2 RETURNING count",
                interaction.user.id,
                upgrade,
            )

        embed = discord.Embed(
            title="Purchase Successful!", description=f"You have purchased 1 {upgrade}"
        )
        embed.add_field(name="Total Owned", value=new_owned_upgr)
        embed.add_field(name="Balance", value=new_bal)

        await interaction.response.send_message(embed=embed)

    @upgrades.command(name="sell", description="Sell an owned upgrade")
    @app_commands.autocomplete(upgrade=upgrade_autocomplete)
    async def upgrades_sell(
        self,
        interaction: discord.Interaction[IdleBot],
        upgrade: str,
    ):
        owned_ugpr: Record | None = await interaction.client.pool.fetchrow(
            "SELECT * FROM user_upgrades WHERE id=$1 AND name=$2",
            interaction.user.id,
            upgrade,
        )

        if owned_ugpr is None:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Whoops",
                    description="You can't sell this upgrade. You do not own it",
                    colour=discord.Colour.red(),
                )
            )


async def setup(bot):
    await bot.add_cog(Upgrader(bot))
