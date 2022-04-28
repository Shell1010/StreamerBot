import socket
import aioconsole
import opuslib
import struct
import ctypes
from .DiscordGateway import discordgateway
from yt_dlp import YoutubeDL
import aiohttp
import json
import aiofiles
import nacl.secret
import nacl.utils




SAMPLING_RATE = 48000
CHANNELS = 2
FRAME_LENGTH = 20  # in milliseconds
SAMPLE_SIZE = struct.calcsize('h') * CHANNELS
SAMPLES_PER_FRAME = int(SAMPLING_RATE / 1000 * FRAME_LENGTH)
DELAY = FRAME_LENGTH / 1000.0


class voice_client:
    def __init__(self, dg: discordgateway):
        self.socket = None
        self.sequence = 0
        self.dg = dg

    async def play_audio(self, url):
        # if not self.dg.is_connected:
        #     await aioconsole.aprint("I am not connected to a voice channel!")
        
        ydl_opts = {'outtmpl': './data/Songs/song.wav',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        self.checked_add("sequence", 1, 65535)
        async with aiofiles.open("./data/Songs/song.wav", mode='rb') as f:
            data = await f.read()
        # await aioconsole.aprint(data)

        encoder = opuslib.Encoder(SAMPLING_RATE, CHANNELS, opuslib.APPLICATION_AUDIO)
        try:
            stuf = encoder.encode(data, SAMPLES_PER_FRAME)
            # await aioconsole.aprint(stuf)
        except Exception as e:
            await aioconsole.aprint(e)
        
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(False)
        packet = self.get_voice_packet(data)
        self.socket.sendto(packet, (self.dg.address, self.dg.port))

        self.checked_add('timestamp', SAMPLES_PER_FRAME, 4294967295)

        
    def get_voice_packet(self, data):
        header = bytearray(12)

        # Formulate rtp header
        header[0] = 0x80
        header[1] = 0x78
        struct.pack_into('>H', header, 2, self.sequence)
        struct.pack_into('>I', header, 4, 0)
        struct.pack_into('>I', header, 8, 0)

        encrypt_packet = getattr(self, "_encrypt_"+ self.dg.mode)
        return encrypt_packet(header, data)

    def _encrypt_xsalsa20_poly1305(self, header: bytes, data) -> bytes:
        box = nacl.secret.SecretBox(bytes(self.dg.secret_key))
        nonce = bytearray(24)
        nonce[:12] = header

        return header + box.encrypt(bytes(data), bytes(nonce)).ciphertext

    def checked_add(self, attr: str, value: int, limit: int) -> None:
        val = getattr(self, attr)
        if val + value > limit:
            setattr(self, attr, 0)
        else:
            setattr(self, attr, val + value)


    
