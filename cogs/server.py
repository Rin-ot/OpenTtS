#coding=utf-8
from discord.ui import Select, View, Button
from discord.commands import Option, slash_command
from discord.ext import commands
import discord

# Local Module
from modules.guild import GuildManager

class ServerSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name = f"setting", 
        description = f"サーバーの設定を変更できます。"
    )
    async def server_settings(self, ctx):
        guild = GuildManager()
        setting_text = guild.read(ctx.guild.id)

        e = discord.Embed(
            title = "サーバー設定", 
            description = f"{setting_text}"
        )
        await ctx.respond(embed = e)

def setup(bot):
    bot.add_cog(ServerSettings(bot))