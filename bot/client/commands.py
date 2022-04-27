import json
import asyncio
import aioconsole
import aiohttp
from .DiscordGateway import discordgateway



class handler:

    def __init__(self, dg: discordgateway):
        self.channel = None
        self.guild = None
        self.desc = {
            "Help": "The help command, provides list of all the commands",
            "Something": "Placeholder thing",
            "Stream": "Begin streaming with this command",
        }
        self.options = {
            "help": self.help,
            "stream": self.stream
        }
        with open('./data/config.json') as f:
            config = json.load(f)
        self.prefix = config.get("prefix")
        self.token = config.get("token")
        self.dg = dg

        self.useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.135 Chrome/91.0.4472.164 Electron/13.6.6 Safari/537.36"

    async def error(self):
        await self.send_msg("```ansi\n[1;31mYou suck! Command isn't real >:(```")

    async def on_msg(self):
        
        while True:
            event = await self.dg.recv_json()
            if event["t"] == "MESSAGE_CREATE":
                # print(event["d"]["content"].strip().lower().startswith(self.prefix)) # if a message create event occurs
                if event["d"]["content"].strip().lower().startswith(self.prefix): # removes whitespace and checks if message starts with prefi
                    self.channel = event['d']['channel_id']
                    if "guild_id" in event['d']:
                        self.guild = event['d']['guild_id']
                    # print(event["d"]["content"].strip().lower().split(" ")[0].replace(self.prefix, ""))()
                    await self.options.get(event["d"]["content"].strip().lower().split(" ")[0].replace(self.prefix, ""), self.error)()
                    # await aioconsole.aprint(event['d'])
                    # await aioconsole.aprint(event["d"]["content"].strip().lower().split(" ")[0].replace(self.prefix, ""))

    async def help(self):
        msg = "```ansi\n[1;31mSTREAMER BOT MADE BY SHELL\n"
        for name, desc in self.desc.items():
            msg += f"[1;31m{name}:  [1;32m{desc}\n"
        msg += "```"
        await self.send_msg(msg)

    async def stream(self):
        msg = "```ansi\n[1;31mSTREAMER BOT MADE BY SHELL\n[1;32mConnecting to vc...```"
        await self.send_msg(msg)
        # await aioconsole.aprint("Test")
        await self.dg.vc_simple_connect(self.channel, self.guild)
        
        # await asyncio.sleep(2)
        # await aioconsole.aprint("First")
        # await self.dg.connect_stream2(self.channel, self.guild)

    async def send_msg(self, msg):
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://canary.discord.com/api/v9/channels/{self.channel}/messages", headers={"authorization":self.token, "user-agent":self.useragent}, json={"content":msg}) as resp:
                j = await resp.json()
                await aioconsole.aprint(f"{resp.status}")