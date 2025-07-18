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

    @slash_command(name = f"force-join", description = f"ボイスチャンネルに強制的に接続します。")
    async def force_join(self, ctx):
        try:
            await self.vc_connect(ctx)
        except:
            e = discord.Embed(
                title = "エラー: 接続失敗",
                description = f"エラーが発生しました。\n※何度もこのエラーが発生する場合、運営にお問い合わせください。", 
                color = 0xfa0909
            )
            await ctx.respond(embed = e)

            _er = discord.Embed(
                title = "エラー: 強制接続失敗", 
                description = f"ユーザ: 強制接続に失敗しました。", 
                color = 0xfa0909
            )
            _er.add_field(
                name = f"エラー内容", 
                value = f"```py\n{traceback.format_exc()}\n```"
            )
            _er.add_field(
                name = f"発生したサーバー", 
                value = f"名前: `{ctx.guild.name}`\nID: `{ctx.guild.id}`\nチャンネル権限: {ctx.channel.permissions_for(ctx.guild.me)}"
            )
            error_channel = self.bot.get_channel(self.error_channel)
            await error_channel.send(embed = _er)

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
        if member.id == self.bot.user.id: return

        elif before.channel is None: return

        elif after.channel is None: 
            cm = ChannelManager()
            ch = cm.get_text_id(before.channel.id)
            if ch is not None:
                if len(before.channel.members) == 1:
                    try:
                        channel = self.bot.get_channel(ch)
                        e = discord.Embed(
                            title = "読み上げ終了", 
                            description = f"通話からユーザーがいなくなったため、自動で読み上げを終了しました。", 
                            color = 0x3bd37b
                        )
                        await channel.send(embed = e)
                    except:
                        pass
                    voice = discord.utils.get(self.bot.voice_clients, guild = member.guild)
                    await voice.disconnect()

                    cm.delete_voice(before.channel.id)

def setup(bot):
    bot.add_cog(Voice(bot))