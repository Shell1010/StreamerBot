import socket
import aioconsole
import opuslib.api.encoder
import struct
import ctypes
from .DiscordGateway import discordgateway
from yt_dlp import YoutubeDL
import aiohttp
import json
import aiofiles


SAMPLING_RATE = 48000
CHANNELS = 2
FRAME_LENGTH = 20  # in milliseconds
SAMPLE_SIZE = struct.calcsize('h') * CHANNELS
SAMPLES_PER_FRAME = int(SAMPLING_RATE / 1000 * FRAME_LENGTH)
DELAY = FRAME_LENGTH / 1000.0


class voice_client:
    def __init__(self, dg: discordgateway):
        self.socket = None
        self.dg = dg

    async def play_audio(self, url):
        # if not self.dg.is_connected:
        #     await aioconsole.aprint("I am not connected to a voice channel!")
        
        ydl_opts = {'outtmpl': './data/Songs/song.mp3',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        



        enc = opuslib.api.encoder.create_state(SAMPLING_RATE, CHANNELS, opuslib.APPLICATION_VOIP)
        async with aiofiles.open("./data/Songs/song.mp3", mode='r', encoding="utf-8") as f:
            data = await f.read()

        stuf = opuslib.api.encoder.encode(enc, data, FRAME_LENGTH, len(data))
        await aioconsole.aprint(stuf)

    
