import os
import aiohttp
import discord
from discord.ext import commands
from discord.utils import setup_logging

from dotenv import load_dotenv
from os import environ
import asyncpg
import time

from .tree import IdleTree

setup_logging()
load_dotenv()


class IdleBot(commands.Bot):
    def __init__(
        self, *, pool: asyncpg.Pool, aiosession: aiohttp.ClientSession, dev_mode: bool
    ):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        self.prefix = environ["PREFIX"] if not dev_mode else environ["DEV_PREFIX"]
        self.full_prefix = commands.when_mentioned_or(self.prefix)

        allowed_mentions = discord.AllowedMentions(
            everyone=False, roles=True, users=True
        )

        super().__init__(
            command_prefix=self.full_prefix,
            intents=intents,
            allowed_mentions=allowed_mentions,
            tree_cls=IdleTree,
        )

        self.dev_mode: bool = dev_mode
        self.token: str = environ["TOKEN"] if not dev_mode else environ["DEV_TOKEN"]

        self.github: str = "NO GITHUB"

        self.pool: asyncpg.Pool[asyncpg.Record] = pool
        self._session: aiohttp.ClientSession = aiosession

        self.start_time: int = round(time.time())

    async def setup_hook(self):
        await self.load_extension("jishaku")
        await self.load_extension("cogs.registration")
        await self.load_extension("cogs.wallet")

        # self._log_webhook: discord.Webhook = discord.Webhook.from_url(
        #     url=environ["WEBHOOK_URL"], session=self._session, bot_token=self.token
        # )

        # Load the schema into the db

        with open("./src/schema.sql") as file:
            await self.pool.execute(file.read())

        print("Loaded Schema.")

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user}")
