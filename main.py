import json
from bot import discordgateway
from bot import console
import asyncio
import aioconsole
from bot import handler

with open('./data/config.json') as f:
    config = json.load(f)
token = config.get("token")
prefix = config.get("prefix")


async def main():
    await console().menu() # funni ascii
    dg = discordgateway(token)
    await dg.simple_connect()
    await handler(dg).on_msg()


asyncio.run(main())