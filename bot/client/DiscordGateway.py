import asyncio
import websockets
import aioconsole
import json

class discordgateway:
    def __init__(self, token: str):
        self.token = token
        self.id = None
        
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
        event = await self.recv_json()
        while True:
            if event["t"] == "READY":
                self.id = event["d"]["user"]["id"]
            break

    async def connect_stream(self, channel, guild=None):
        payload = {
            "op":18,
            "d": {
                "channel_id": channel,
                "guild_id": guild,
                "type": "call" if guild is None else "guild"
            }
        }
        await self.send_json(payload)
    
    # async def connect_stream2(self, channel, guild=None):
    #     payload = {
    #         "op":"22",
    #         "d": {
    #             "stream_key":f"call:{channel}:{self.id}" if guild is None else f"guild:{guild}:{channel}:{self.id}",
    #             "paused":False
    #         }
    #     }

    async def connect_vc(self, channel, guild=None):
        payload = {
            "op": 4,
            "d": {
                "guild_id": guild,
                "channel_id": channel,
                "self_mute": False,
                "self_deaf": False,
                "self_video": False,
            }
        }
        await self.send_json(payload)
        await aioconsole.aprint(guild, channel)
        while True:
            event = await self.recv_json()
            try:
                if event['t'] == "VOICE_SERVER_UPDATE":
                    webs_token = event['d']['token']
                    webs_endpoint = event['d']['endpoint']
                if event['t'] == "VOICE_STATE_UPDATE":
                    session_id = event['d']['session_id']
                if session_id is not None and webs_token is not None and webs_endpoint is not None:
                    break
            except:
                continue
        return webs_endpoint, webs_token, session_id

            





    
