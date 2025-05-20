from discord.ext import commands
from discord.commands import slash_command
from discord.ui import View, Button
import discord, os, traceback
from gtts import gTTS

from dotenv import load_dotenv
load_dotenv()

# Local Module
from modules.channels import ChannelManager
from modules.connect import connect_sound

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.error_channel = int(os.getenv("ERROR_CHANNEL"))

    async def vc_connect(self, ctx, value = None):
        if value is None:
            if ctx.author.voice is None:
                e = discord.Embed(
                    title = "エラー", 
                    description = f"ボイスチャンネルに接続してから実行してください。",
                    color = 0xfa0909
                )
                await ctx.respond(embed = e, ephemeral = True)
                return

            voice_channel = ctx.author.voice.channel
            voice = discord.utils.get(self.bot.voice_clients, guild = ctx.guild)
            if voice is not None:
                e = discord.Embed(
                    title = "エラー", 
                    description = f"既に別のVCに接続しています！", 
                    color = 0xfa0909
                )
                await ctx.respond(embed = e, ephemeral = True)
            else:
                try:
                    cm = ChannelManager()
                    cm.register_voices(voice_channel.id, ctx.channel.id)
                    voice = await voice_channel.connect()
                    e = discord.Embed(
                        title = "接続完了", 
                        description = f"ボイスチャンネルに接続しました。\n接続チャンネル: {voice_channel.mention}",
                        color = 0x3bd37b
                    )
                    await ctx.respond(embed = e)
                    await connect_sound(ctx.guild.id, voice)
                except:
                    e = discord.Embed(
                        title = "エラー", 
                        description = f"ボイスチャンネルに接続できませんでした。", 
                        color = 0xfa0909
                    )
                    await ctx.respond(embed = e, ephemeral = True)

                    ve = discord.Embed(
                        title = "エラー: 接続失敗", 
                        description = f"```py\n{traceback.format_exc()}\n```",
                        color = 0xfa0909
                    )
                    channel = self.bot.get_channel(self.error_channel)
                    await channel.send(embed = ve)
                    return

        elif value == "message":
            if ctx.author.voice is None: return

            voice_channel = ctx.author.voice.channel
            voice = discord.utils.get(self.bot.voice_clients, guild = ctx.guild)
            if voice is not None: return
            else:
                try:
                    cm = ChannelManager()
                    cm.register_voices(voice_channel.id, ctx.channel.id)
                    voice = await voice_channel.connect()
                    e = discord.Embed(
                        title = "接続完了", 
                        description = f"ボイスチャンネルに接続しました。\n接続チャンネル: {voice_channel.mention}",
                        color = 0x3bd37b
                    )
                    await ctx.reply(embed = e)
                    await connect_sound(ctx.guild.id, voice)
                except:
                    ve = discord.Embed(
                        title = "エラー: 接続失敗", 
                        description = f"```py\n{traceback.format_exc()}\n```",
                        color = 0xfa0909
                    )
                    channel = self.bot.get_channel(self.error_channel)
                    await channel.send(embed = ve) 
                    return

    async def vc_disconnect(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild = ctx.guild)
        if voice is None:
            e = discord.Embed(
                title = "エラー", 
                description = f"ボイスチャンネルに接続していません！", 
                color = 0xfa0909
            )
            await ctx.respond(embed = e, ephemeral = True)
        else:
            await voice.disconnect()
            e = discord.Embed(
                title = "切断完了",
                description = f"ボイスチャンネルから切断しました。",
                color = 0x3bd37b
            )
            await ctx.respond(embed = e)
            cm = ChannelManager()
            cm.delete_voice(voice.channel.id)

    @slash_command(name = "vc", description = "OpenTtSを実行します。")
    async def vc(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild = ctx.guild)
        if voice is None:
            await self.vc_connect(ctx)
        else:
            await self.vc_disconnect(ctx)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content == "読み上げ開始":
            voice = discord.utils.get(self.bot.voice_clients, guild = message.guild)
            if voice is None:
                await self.vc_connect(message, "message")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None: return

        elif after.channel is None: 
            cm = ChannelManager()
            ch = cm.get_text_id(before.channel.id)
            if ch is not None:
                if len(before.channel.members) == 1:
                    channel = self.bot.get_channel(ch)
                    e = discord.Embed(
                        title = "読み上げ終了", 
                        description = f"通話からユーザーがいなくなったため、自動で読み上げを終了しました。", 
                        color = 0x3bd37b
                    )
                    await channel.send(embed = e)
                    voice = discord.utils.get(self.bot.voice_clients, guild = member.guild)
                    await voice.disconnect()

                    cm.delete_voice(before.channel.id)

def setup(bot):
    bot.add_cog(Voice(bot))