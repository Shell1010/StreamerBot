import asyncio
import websockets
import aioconsole
import json
import time
import struct
import socket

import ctypes

class discordgateway:
    def __init__(self, token: str):
        self.token = token
        self.id = None
        self.is_connected = False
        self.mode = "xsalsa20_poly1305"
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(False)
        
        
    async def recv_json(self):
        item = await self.ws.recv()
        if item:
            return json.loads(item)

    async def send_json(self, payload: dict):
        await self.ws.send(json.dumps(payload))

    async def vc_recv_json(self):
        item = await self.vc_ws.recv()
        if item:
            return json.loads(item)

    async def vc_send_json(self, payload: dict):
        await self.vc_ws.send(json.dumps(payload))

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
        if event["t"] == "READY":
            self.id = event["d"]["user"]["id"]
                
            

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
        while True:
            event = await self.recv_json()
            try:
                # await aioconsole.aprint(event["t"])
                if event['t'] == "VOICE_SERVER_UPDATE":
                    
                    self.webs_token = event['d']['token']
                    self.webs_endpoint = event['d']['endpoint']
                if event['t'] == "VOICE_STATE_UPDATE":
                    self.session_id = event['d']['session_id']
                if self.session_id is not None and self.webs_token is not None and self.webs_endpoint is not None:
                    break
            except:
                continue
        self.vc_ws = await websockets.connect(f"wss://{self.webs_endpoint[:-4]}/?v=6")

    async def leave_vc(self):
        payload = {
            "op": 4,
            "d": {
                "guild_id": None,
                "channel_id": None,
                "self_mute": False,
                "self_deaf": False,
                "self_video": False,
            }
        }
        await self.send_json(payload)
        self.is_connected = False


    async def vc_identify(self, server):
        payload ={
            "op": 0,
            "d": {
                "server_id": f"{server}",
                "user_id":  self.id,
                "session_id": f"{self.session_id}",
                "token": f"{self.webs_token}",
                "video":True,
                "streams":[{"type":"screen","rid":"100","quality":100}]
            }
        }
        await self.vc_send_json(payload)
        while True:
            event = await self.vc_recv_json()
            try:
                if event['op'] == 8:
                    interval = event['d']['heartbeat_interval']
                if event['op'] == 2:
                    data = event['d']
                if data is not None and interval is not None:
                    break
            except:
                continue
        self.address = data['ip']
        self.port = data['port']
        self.ssrc = data['ssrc']

        return interval

    async def vc_heartbeat(self, interval):
        await aioconsole.aprint(f"Voice websocket heartbeat loop has begain with the interval of {interval} seconds")

        while True:
            if not self.is_connected:
                await aioconsole.aprint("No longer connected!")
                break
            payload = {
                "op": 3,
                "d": int(time.time())
            }
            await asyncio.sleep(interval)
            await self.vc_send_json(payload)
            await aioconsole.aprint("Voice heartbeat sent!")


    async def udp_connect(self):
        payload = {
            "op": 1,
            "d": {
                "protocol": "udp",
                "data": {
                    "address": self.ip,
                    "port": self.me_port,
                    "mode": self.mode
                }
            }
        }
        await self.vc_send_json(payload)
        while True:
            event = await self.vc_recv_json()
            try:
                if event['op'] == 4:
                    self.secret_key = event['d']['secret_key']
                    break
            except:
                continue


    async def ip_discovery(self):

        packet = bytearray(70)
        struct.pack_into('>H', packet, 0, 1)  # 1 = Send
        struct.pack_into('>H', packet, 2, 70)  # 70 = Length
        struct.pack_into('>I', packet, 4, self.ssrc)
        self.socket.sendto(packet, (self.address, self.port))
        while True:
            try:
                data = self.socket.recv(70)
                break
            except:
                continue
        # await aioconsole.aprint(data)
        ip_start = 4
        ip_end = data.index(0, ip_start)
        self.ip = data[ip_start:ip_end].decode("ascii")
        self.me_port = struct.unpack_from(">H", data, len(data) - 2)[0]
        # await aioconsole.aprint(f"{self.ip}:{self.port}")


    async def vc_simple_connect(self, channel, guild=None):
        await self.connect_vc(channel, guild)
        interval = await self.vc_identify(channel if guild is None else guild)
        self.is_connected = True
        asyncio.create_task(self.vc_heartbeat(interval/1000))
        await self.ip_discovery()
        
        await self.udp_connect()
        # await self.connect_stream(channel, guild)

    

    

    
            





    
