from discord.ext import commands
from discord.commands import slash_command
from discord.ui import View, Button, Select
import discord, json

# Local Modules
from modules.voice_endpoints import voicevox_data, get_voicevox_speaker, coeiroink_data, get_coeiroink_speaker
from modules.user import UserManager

class UserSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name = "menu", description = "音声設定を変更できます。")
    async def menu(self, ctx):
        await ctx.defer(ephemeral = True)

        e = discord.Embed(
            title = "音声設定",
            description = "使用したい音声を選択してください：",
            color = 0x3bd37b
        )
        v = View()
        opt = [
            discord.SelectOption(
                label = f"gTTS", 
                description = f"©Google Text-to-Speach",
                value = f"gTTS:0",
            )
        ]

        _voicevox = await voicevox_data()
        if _voicevox[0] == 200:
            opt.append(
                discord.SelectOption(
                    label = f"VOICEVOX", 
                    description = f"クレジット: ©VOICEVOX/©Hiroshiba", 
                    value = f"voicevox"
                )
            )

        else:
            e.add_field(
                name = f"VOICEVOXに関するエラー", 
                value = f"VOICEVOXサーバーに接続できなかったため、\n現在使用できません。", 
                inline = False
            )

        _coeiroink = await coeiroink_data()
        if _coeiroink[0] == 200:
            opt.append(
                discord.SelectOption(
                    label = f"COEIROINK", 
                    description = f"クレジット: ©COEIROINK", 
                    value = f"coeiroink"
                )
            )

        else:
            e.add_field(
                name = f"COEIROINKに関するエラー", 
                value = f"COEIROINKサーバーに接続できなかったため、\n現在使用できません。", 
                inline = False
            )

        select = Select(
            placeholder = "音声を選択…",
            custom_id = f"select_voice",
            options = opt
        )
        v.add_item(select)
        await ctx.respond(embed = e, view = v, ephemeral = True)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.custom_id is None: return

        elif interaction.custom_id == "select_voice":
            value = interaction.data['values'][0]

            if ":" in value:
                data = {
                    "voice": value
                }
                um = UserManager()
                um.update(interaction.user.id, data)

                if value.startswith("gtts"):
                    voice = f"gTTS"

                else:
                    voice = value.split(":")[0]

                e = discord.Embed(
                    title = "音声変更", 
                    description = f"音声を **{voice}** に変更しました。", 
                    color = 0x3bd37b
                )
                await interaction.response.edit_message(embed = e, view = None)

            else:
                if value == "voicevox":
                    _voicevox = await voicevox_data()
                    if _voicevox[0] != 200:
                        e = discord.Embed(
                            title = "エラー", 
                            description = f"VOICEVOXサーバーとの通信に失敗しました。", 
                            color = 0xfa0909
                        )
                        await interaction.response.edit_message(embed = e, view = None)
                        return

                    else:
                        v = View()
                        opt = []
                        charas = _voicevox[1]
                        for chara_id in range(0, len(charas)):
                            if chara_id >= 25: break
                            elif chara_id == 24:
                                opt.append(
                                    discord.SelectOption(
                                        label = f"他の音声を使用する", 
                                        value = f"next:25"
                                    )
                                )
                            else:
                                chara = charas[chara_id]
                                opt.append(
                                    discord.SelectOption(
                                        label = f"{chara['name']}", 
                                        value = f"{chara['speaker_uuid']}"
                                    )
                                )

                        sel = Select(
                            placeholder = f"キャラクターを選択…", 
                            options = opt, 
                            custom_id = f"select_voicevox"
                        )
                        v.add_item(sel)
                        await interaction.response.edit_message(view = v)

                elif value == "coeiroink":
                    _coeiroink = await coeiroink_data()
                    if _coeiroink[0] != 200:
                        e = discord.Embed(
                            title = "エラー", 
                            description = f"COEIROINKサーバーとの通信に失敗しました。", 
                            color = 0xfa0909
                        )
                        await interaction.response.edit_message(embed = e, view = None)
                        return

                    else:
                        v = View()
                        opt = []
                        charas = _coeiroink[1]
                        for chara_id in range(0, len(charas)):
                            if chara_id >= 25: break
                            elif chara_id == 24:
                                opt.append(
                                    discord.SelectOption(
                                        label = f"他の音声を使用する", 
                                        value = f"next:25"
                                    )
                                )
                            else:
                                chara = charas[chara_id]
                                opt.append(
                                    discord.SelectOption(
                                        label = f"{chara['speakerName']}", 
                                        value = f"{chara['speakerUuid']}"
                                    )
                                )

                        sel = Select(
                            placeholder = f"キャラクターを選択…", 
                            options = opt, 
                            custom_id = f"select_coeiroink"
                        )
                        v.add_item(sel)
                        await interaction.response.edit_message(view = v)

        elif interaction.custom_id == "select_voicevox":
            _voicevox = await voicevox_data()
            if _voicevox[0] != 200:
                e = discord.Embed(
                    title = "エラー", 
                    description = f"VOICEVOXサーバーとの通信に失敗しました。", 
                    color = 0xfa0909
                )
                await interaction.response.edit_message(embed = e, view = None)
                return

            value = interaction.data['values'][0]
            opt = []
            charas = _voicevox[1]
            v = View()

            if value.startswith("next:"):
                _vlen = int(value[len("next:"):]) - 1

                if len(charas) < _vlen:
                    _vlen = len(charas) - 1
                for chara_id in range(_vlen, len(charas)):
                    if chara_id >= _vlen + 25: break
                    elif chara_id == _vlen + 24:
                        opt.append(
                            discord.SelectOption(
                                label = f"他の音声を使用する", 
                                value = f"next:{_vlen + 24}"
                            )
                        )
                    else:
                        chara = charas[chara_id]
                        opt.append(
                            discord.SelectOption(
                                label = f"{chara['name']}", 
                                value = f"{chara['speaker_uuid']}"
                            )
                        )

                sel = Select(
                    placeholder = f"キャラクターを選択…", 
                    options = opt, 
                    custom_id = f"select_voicevox"
                )
                v.add_item(sel)
                await interaction.response.edit_message(view = v)

            else:
                for chara in charas:
                    if chara['speaker_uuid'] != value: continue

                    else:
                        for style in chara['styles']:
                            opt.append(
                                discord.SelectOption(
                                    label = f"{style['name']}", 
                                    value = f"{style['id']}"
                                )
                            )

                        sel = Select(
                            placeholder = f"スタイルを選択…", 
                            options = opt, 
                            custom_id = f"select_voicevox_style"
                        )
                        v.add_item(sel)
                        await interaction.response.edit_message(view = v)

                        return

                e = discord.Embed(
                    title = "エラー", 
                    description = f"話者を検索中にエラーが発生しました。", 
                    color = 0xfa0909
                )
                await interaction.response.edit_message(embed = e, view = None)
                return

        elif interaction.custom_id == "select_voicevox_style":
            value = interaction.data['values'][0]

            data = {
                "voice": f"voicevox:{value}"
            }
            um = UserManager()
            um.write(interaction.user.id, data)

            _voicevox = await voicevox_data()
            if _voicevox[0] != 200:
                e = discord.Embed(
                    title = "音声変更", 
                    description = f"音声を **{value}** (詳細取得不可) に変更しました。", 
                    color = 0x33bbdd
                )
                e.set_footer(text = f"※情報は正しく保存されていますが、音声の生成に失敗する可能性があります。")

            else:
                chara_style = await get_voicevox_speaker(value)
                e = discord.Embed(
                    title = "音声変更", 
                    description = f"音声を **{chara_style}** に変更しました。", 
                    color = 0x3bd37b
                )

            await interaction.response.edit_message(embed = e, view = None)

        elif interaction.custom_id == "select_coeiroink":
            _coeiroink = await coeiroink_data()
            if _coeiroink[0] != 200:
                e = discord.Embed(
                    title = "エラー", 
                    description = f"COEIROINKサーバーとの通信に失敗しました。", 
                    color = 0xfa0909
                )
                await interaction.response.edit_message(embed = e, view = None)
                return

            value = interaction.data['values'][0]
            opt = []
            charas = _coeiroink[1]
            v = View()

            if value.startswith("next:"):
                _vlen = int(value[len("next:"):]) - 1

                if len(charas) < _vlen:
                    _vlen = len(charas) - 1
                for chara_id in range(_vlen, len(charas)):
                    if chara_id >= _vlen + 25: break
                    elif chara_id == _vlen + 24:
                        opt.append(
                            discord.SelectOption(
                                label = f"他の音声を使用する", 
                                value = f"next:{_vlen + 24}"
                            )
                        )
                    else:
                        chara = charas[chara_id]
                        opt.append(
                            discord.SelectOption(
                                label = f"{chara['speakerName']}", 
                                value = f"{chara['speakerUuid']}"
                            )
                        )

                sel = Select(
                    placeholder = f"キャラクターを選択…", 
                    options = opt, 
                    custom_id = f"select_coeiroink"
                )
                v.add_item(sel)
                await interaction.response.edit_message(view = v)

            else:
                for chara in charas:
                    if chara['speakerUuid'] != value: continue

                    else:
                        for style in chara['styles']:
                            opt.append(
                                discord.SelectOption(
                                    label = f"{style['styleName']}", 
                                    value = f"{style['styleId']}"
                                )
                            )

                        sel = Select(
                            placeholder = f"スタイルを選択…", 
                            options = opt, 
                            custom_id = f"select_coeiroink_style"
                        )
                        v.add_item(sel)
                        await interaction.response.edit_message(view = v)

                        return

                e = discord.Embed(
                    title = "エラー", 
                    description = f"話者を検索中にエラーが発生しました。", 
                    color = 0xfa0909
                )
                await interaction.response.edit_message(embed = e, view = None)
                return

        elif interaction.custom_id == "select_coeiroink_style":
            value = interaction.data['values'][0]

            data = {
                "voice": f"coeiroink:{value}"
            }
            um = UserManager()
            um.write(interaction.user.id, data)

            _coeiroink = await coeiroink_data()
            if _coeiroink[0] != 200:
                e = discord.Embed(
                    title = "音声変更", 
                    description = f"音声を **{value}** (詳細取得不可) に変更しました。", 
                    color = 0x33bbdd
                )
                e.set_footer(text = f"※情報は正しく保存されていますが、音声の生成に失敗する可能性があります。")

            else:
                chara_style = await get_coeiroink_speaker(value)
                e = discord.Embed(
                    title = "音声変更", 
                    description = f"音声を **{chara_style}** に変更しました。", 
                    color = 0x3bd37b
                )

            await interaction.response.edit_message(embed = e, view = None)

def setup(bot):
    bot.add_cog(UserSettings(bot))