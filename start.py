import asyncio
import asyncpg
import os
import aiohttp

from dotenv import load_dotenv

load_dotenv()

from src.bot import IdleBot

dev_mode: bool = os.environ["DEV"] == "True"


async def run():
    async with asyncpg.create_pool(
        dsn=os.environ["BACKUP_PG_DSN"]
    ) as pool, aiohttp.ClientSession() as session:
        async with IdleBot(
            pool=pool, aiosession=session, dev_mode=dev_mode  # type: ignore
        ) as bot:
            await bot.start(bot.token)


asyncio.run(run())
