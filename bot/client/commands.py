import json
import asyncio
import aioconsole
import aiohttp
from .DiscordGateway import discordgateway


class commands:

    def __init__(self, dg: discordgateway):
        self.channel = None
        with open('./data/config.json') as f:
            config = json.load(f)
        self.prefix = config.get("prefix")
        self.token = config.get("token")
        self.dg = dg
        self.useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.135 Chrome/91.0.4472.164 Electron/13.6.6 Safari/537.36"

    async def error(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://canary.discord.com/api/v9/channels/{self.channel}/messages", headers={"authorization":self.token, "user-agent":self.useragent}, json={"content":"Command not REAL"}) as resp:
                await aioconsole.aprint(f"{resp.status}")


    async def on_msg(self):
        self.options = {
            "help": self.help
        }
        while True:
            event = await self.dg.recv_json()
            if event["t"] == "MESSAGE_CREATE":
                # print(event["d"]["content"].strip().lower().startswith(self.prefix)) # if a message create event occurs
                if event["d"]["content"].strip().lower().startswith(self.prefix): # removes whitespace and checks if message starts with prefix
                    self.channel = event['d']['channel_id']
                    # print(event["d"]["content"].strip().lower().split(" ")[0].replace(self.prefix, ""))()
                    await self.options.get(event["d"]["content"].strip().lower().split(" ")[0].replace(self.prefix, ""), self.error)()

            
        await aioconsole.aprint("Done")

    async def help(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://canary.discord.com/api/v9/channels/{self.channel}/messages", headers={"authorization":self.token, "user-agent":self.useragent}, json={"content":"YOu have been helped"}) as resp:
                j = await resp.json()
                await aioconsole.aprint(f"{j}")