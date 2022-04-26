import asyncio
from colorama import Fore as Color
import os
import aioconsole
import discord
from discord.ext import commands

class console:
    async def clear(self):
        os.system('clear')

    async def menu(self):
        await self.clear()
        art = f"""{Color.RED}
╔════════════════════╬════════════════════╗
║    ╔═╗═╦═┬─┐┌─┐┌─┐┌┬┐┌─┐┬─┐╔╗ ┌─┐═╦═    ║  
║    ╚═╗ ║ ├┬┘├┤ ├─┤│││├┤ ├┬┘╠╩╗│ │ ║     ║
║    ╚═╝ ╩ ┴└─└─┘┴ ┴┴ ┴└─┘┴└─╚═╝└─┘ ╩     ║
╚════════════════════╬════════════════════╝
        {Color.RESET}"""
        await aioconsole.aprint(art)

