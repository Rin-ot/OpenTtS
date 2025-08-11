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
        v = View()
        b = Button(
            label = "設定を変更する",
            style = discord.ButtonStyle.primary,
            custom_id = "server_settings_change"
        )
        v.add_item(b)
        await ctx.respond(embed = e, view = v)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.custom_id is None: return

        elif interaction.custom_id == "server_settings_change":
            guild = GuildManager()
            setting_text = guild.read(interaction.guild.id)

            e = discord.Embed(
                title = "サーバー設定", 
                description = f"{setting_text}"
            )
            v = View()

            opts = []
            for opt in guild.default_dict:
                if opt == "auto_connect":
                    opts.append(discord.SelectOption(label = "自動接続設定", value = "auto_connect"))
                elif opt == "read_user_join_leave":
                    opts.append(discord.SelectOption(label = "ユーザーの接続/切断の読み上げ", value = "read_user_join_leave"))
                elif opt == "read_attachment":
                    opts.append(discord.SelectOption(label = "添付ファイルの読み上げ", value = "read_attachment"))
                elif opt == "read_only_vc":
                    opts.append(discord.SelectOption(label = "VCのみの読み上げ", value = "read_only_vc"))

            s = Select(
                placeholder = f"変更する設定を選択：", 
                options = opts
            )
            v.add_item(s)
            await interaction.response.edit_message(embed=e, view=v)

def setup(bot):
    bot.add_cog(ServerSettings(bot))