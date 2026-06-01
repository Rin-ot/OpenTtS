from discord.ext import commands
from discord.commands import slash_command, Option
from discord.ui import View, Button
import discord, json, os

class ServerDictionary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    _dic = discord.SlashCommandGroup("dict", "辞書に関するコマンドです。")

    @_dic.command(name="add", description="サーバー専用の辞書に単語を追加します。")
    async def add(self, ctx, 
        word: Option(str, "追加する単語", required = True),
        read: Option(str, "単語の読み", required = True)
    ):
        if os.path.isfile(f"./dict/{ctx.guild.id}.json"):
            with open(f"./dict/{ctx.guild.id}.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                f.close()

        else: data = {}

        if word in data:
            await ctx.respond(f"その単語は既に登録されています。\n読み: {data[word]}", ephemeral=True)
            return

        data[word] = read

        with open(f"./dict/{ctx.guild.id}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.close()

        e = discord.Embed(
            title = "辞書登録 - 完了", 
            description = f"単語: {word}\n読み: {read}", 
            color = 0x3bd37b
        )
        await ctx.respond(embed = e)

    def word_list(ctx):
        with open(f"./dict/{ctx.interaction.guild.id}.json", "r") as f:
            words = json.load(f)
            f.close()
        return [f"{word}" for word in list(words.keys()) if (ctx.value.lower() in word.lower())]

    @_dic.command(name="remove", description="サーバー専用の辞書から単語を削除します。")
    async def remove(self, ctx, 
        word: Option(str, "削除する単語", required = True, autocomplete = word_list)
    ):
        if os.path.isfile(f"./dict/{ctx.guild.id}.json"):
            with open(f"./dict/{ctx.guild.id}.json", "r", encoding="utf-8") as f:
                words = json.load(f)
                f.close()

        else: 
            await ctx.respond("このサーバーには辞書が存在しません。", ephemeral=True)
            return

        if not word in list(words.keys()):
            await ctx.respond("その単語は登録されていません。", ephemeral=True)
            return

        read = words[word]
        del words[word]

        with open(f"./dict/{ctx.guild.id}.json", "w", encoding="utf-8") as f:
            json.dump(words, f, ensure_ascii=False, indent=4)
            f.close()

        e = discord.Embed(
            title = "辞書削除 - 完了", 
            description = f"単語: {word}\n読み: {read}", 
            color = 0xff5964
        )
        await ctx.respond(embed = e)

    @_dic.command(name="list", description="サーバー専用の辞書に登録されている単語を一覧表示します。")
    async def _list(self, ctx):
        if os.path.isfile(f"./dict/{ctx.guild.id}.json"):
            with open(f"./dict/{ctx.guild.id}.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                f.close()

        else: 
            await ctx.respond("このサーバーには辞書が存在しません。", ephemeral=True)
            return

        if len(data) == 0:
            await ctx.respond("このサーバーの辞書には単語が登録されていません。", ephemeral=True)
            return

        e = discord.Embed(
            title = "サーバー辞書一覧", 
            description = "\n".join([f"**{word}**: {read}" for word, read in data.items()]), 
            color = 0x7289da
        )
        await ctx.respond(embed = e)

def setup(bot):
    bot.add_cog(ServerDictionary(bot))