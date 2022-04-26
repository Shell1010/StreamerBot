import json
from bot import discordgateway
from bot import console
import asyncio
import aioconsole
from bot import commands

with open('./data/config.json') as f:
    config = json.load(f)
token = config.get("token")
prefix = config.get("prefix")


async def main():
    await console().menu() # funni ascii
    dg = discordgateway(token)
    await dg.connect() # funni connect to gateway
    interval = await dg.recv_json() # function to make response json
    await aioconsole.aprint("Done")
    await dg.identify() # identify to gateway
    await aioconsole.aprint("Done")
    asyncio.create_task(dg.heartbeat(interval['d']['heartbeat_interval'] / 1000)) # heartbeat interval thing that runs in background foreva
    

    await commands().on_msg()
    await aioconsole.aprint("Done")
    
    


asyncio.run(main())