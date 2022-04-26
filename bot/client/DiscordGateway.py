import asyncio
import websockets
import aioconsole
import json

class discordgateway:
    def __init__(self, token: str):
        self.token = token
        
    async def recv_json(self):
        item = await self.ws.recv()
        if item:
            return json.loads(item)

    async def send_json(self, payload: dict):
        await self.ws.send(json.dumps(payload))

    async def connect(self):
        self.ws = await websockets.connect("wss://gateway.discord.gg/?v=9&encording=json")

    async def identify(self):
        payload = {
            'op': 2,
            "d": {
                "token": self.token,
                "properties": {
                    "$os": "windows",
                    "$browser": "chrome",
                    "$device": 'pc'
                }
                
            }
        }
        await self.send_json(payload)

    async def heartbeat(self, interval):
        await aioconsole.aprint(f"Hearbeat loop has began with the interval of {interval} seconds!")
        heartbeatJSON = {
            "op": 1,
            "d": "null"
        }
        while True:
            await asyncio.sleep(interval)
            await self.send_json(heartbeatJSON)
            await aioconsole.aprint("Sent heartbeat!")

    async def simple_connect(self):
        await self.connect()
        interval = await self.recv_json()
        await self.identify()
        asyncio.create_task(self.heartbeat(interval['d']['heartbeat_interval'] / 1000))

    





    