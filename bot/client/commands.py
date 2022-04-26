import json
import asyncio
import aioconsole
import aiohttp
from .DiscordGateway import discordgateway


class commands:

    def __init__(self):
        self.channel = None
        self.desc = {

        }
        with open('./data/config.json') as f:
            config = json.load(f)
        self.token = config.get("token")
        self.dg = discordgateway(self.token)
        self.useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.135 Chrome/91.0.4472.164 Electron/13.6.6 Safari/537.36"


    async def on_msg(self):
        self.options = {
            "help": await self.help()
        }
        while True:
            event = await self.dg.recv_json()
            if event["t"] == "MESSAGE_CREATE": # if a message create event occurs
                if event["d"]["content"].strip().lower().startswith(prefix): # removes whitespace and checks if message starts with prefix
                    self.channel = event['d']['channel_id']
                    self.options.get(event["d"]["content"].strip().lower().split()[1])
            
        await aioconsole.aprint("Done")

    async def help(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://canary.discord.com/api/v9/channels/{self.channel}/messages", headers={"authorization":self.token, "user-agent":self.useragent}, json={"content":"YOu have been helped"}) as resp:
                j = await resp.json()
                await aioconsole.aprint(f"{j}")