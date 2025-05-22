import os, traceback, discord
from json import load, dump
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN")
prefix = os.getenv("PREFIX")

class OpenTtS(commands.Bot):
    def __init__(self, command_prefix, **kwargs):
        super().__init__(command_prefix, **kwargs)
        self.load_error = False

        for cog in os.listdir("./cogs/"):
            if cog.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{cog[:-3]}")
                except Exception:
                    self.load_error = True
                    print(f"[Err] {traceback.format_exc()}")

    async def on_ready(self):
        if self.load_error: pass
        else:
            from platform import system as _os
            if _os() == "Linux":
                os.system('clear')
            elif _os() == "Windows":
                os.system('cls')

        print(f"[Log] Logged on as {self.user}.")
        await self.change_presence(
            activity = discord.Game(name = f"Ver.{open('version.txt').read()}"),
        )

if __name__ == '__main__':
    bot = OpenTtS(
        command_prefix = prefix, 
        intents = discord.Intents.all(), 
        )
    bot.run(token)