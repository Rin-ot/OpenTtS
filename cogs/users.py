from discord.ext import commands
from discord.commands import slash_command
from discord.ui import View, Button, Select
import discord

# Local Modules
from modules.voice_endpoints import voicevox_data, get_voicevox_speaker, coeiroink_data, get_coeiroink_speaker, ojtalk_data
from modules.user import UserManager

um = UserManager()

class UserSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name = "menu", description = "音声設定を変更できます。")
    async def menu(self, ctx):
        await ctx.defer(ephemeral = True)

        current_voice = um.voice_value(ctx.author.id)

        e = discord.Embed(
            title = "音声設定",
            description = f"現在使用している音声： {current_voice}\n使用したい音声を選択してください：",
            color = 0x3bd37b
        )
        v = View()
        opt = [
            discord.SelectOption(
                label = f"gTTS", 
                description = f"クレジット: ©Google Text-to-Speach",
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

        _ojtalk = await ojtalk_data()
        if _ojtalk[0] == 200:
            opt.append(
                discord.SelectOption(
                    label = f"Open JTalk", 
                    description = f"クレジット: © Open JTalk", 
                    value = f"ojtalk"
                )
            )

        else:
            e.add_field(
                name = f"Open JTalkに関するエラー", 
                value = f"Open JTalkが使用できない環境のため、\n現在使用できません。", 
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

                elif value == "ojtalk":
                    _ojtalk = await ojtalk_data()
                    if _ojtalk[0] != 200:
                        e = discord.Embed(
                            title = "エラー", 
                            description = f"Open JTalkの動作が未検証です！", 
                            color = 0xfa0909
                        )
                        await interaction.response.edit_message(embed = e, view = None)
                        return

                    else:
                        v = View()
                        opt = []
                        charas = _ojtalk[1]
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
                                chara = list(charas.keys())[chara_id]
                                opt.append(
                                    discord.SelectOption(
                                        label = f"{chara}", 
                                        value = f"{chara}"
                                    )
                                )

                        sel = Select(
                            placeholder = f"キャラクターを選択…", 
                            options = opt, 
                            custom_id = f"select_ojtalk"
                        )
                        v.add_item(sel)
                        await interaction.response.edit_message(view = v)

        elif interaction.custom_id == "select_voicevox":
            _voicevox = await voicevox_data()
            if _voicevox[0] != 200:
                e = discord.Embed(title = "エラー", description = f"VOICEVOXサーバーとの通信に失敗しました。", color = 0xfa0909)
                await interaction.response.edit_message(embed = e, view = None)
                return

            value = interaction.data['values'][0]
            charas = _voicevox[1]
            
            if value.startswith("next:"):
                _vlen = int(value[len("next:"):])
                v = View()
                opt = []
                # Add previous page option
                if _vlen > 24:
                    opt.append(discord.SelectOption(label="≪ 前のページ", value=f"prev:{_vlen - 24}"))
                
                remaining_slots = 25 - len(opt)
                end_index = _vlen + remaining_slots -1
                
                for chara_id in range(_vlen, min(len(charas), end_index + 1)):
                    if chara_id == end_index and chara_id < len(charas) -1:
                        opt.append(discord.SelectOption(label="他の音声を使用する", value=f"next:{chara_id + 1}"))
                    else:
                        chara = charas[chara_id]
                        opt.append(discord.SelectOption(label=f"{chara['name']}", value=f"{chara['speaker_uuid']}"))
                
                sel = Select(placeholder="キャラクターを選択…", options=opt, custom_id="select_voicevox")
                v.add_item(sel)
                await interaction.response.edit_message(view=v)
                return

            target_chara = next((c for c in charas if c['speaker_uuid'] == value), None)
            if not target_chara:
                e = discord.Embed(title="エラー", description="話者を検索中にエラーが発生しました。", color=0xfa0909)
                await interaction.response.edit_message(embed=e, view=None)
                return

            v = View()
            opt = []
            styles = target_chara['styles']

            if len(styles) <= 25:
                for style in styles:
                    opt.append(discord.SelectOption(label=style['name'], value=str(style['id'])))
            else:
                for i in range(24):
                    opt.append(discord.SelectOption(label=styles[i]['name'], value=str(styles[i]['id'])))
                opt.append(discord.SelectOption(label="他のスタイルを使用する", value=f"page:{value}:24"))

            sel = Select(placeholder="スタイルを選択…", options=opt, custom_id="select_voicevox_style")
            v.add_item(sel)
            await interaction.response.edit_message(view=v)

        elif interaction.custom_id == "select_voicevox_style":
            value = interaction.data['values'][0]

            if value.startswith("page:"):
                _, uuid, start_str = value.split(":")
                start_index = int(start_str)

                _voicevox = await voicevox_data()
                if _voicevox[0] != 200:
                    e = discord.Embed(title="エラー", description="VOICEVOXサーバーとの通信に失敗しました。", color=0xfa0909)
                    await interaction.response.edit_message(embed=e, view=None)
                    return

                charas = _voicevox[1]
                target_chara = next((c for c in charas if c['speaker_uuid'] == uuid), None)

                if not target_chara:
                    e = discord.Embed(title="エラー", description="話者を検索中にエラーが発生しました。", color=0xfa0909)
                    await interaction.response.edit_message(embed=e, view=None)
                    return

                v = View()
                opt = []
                styles = target_chara['styles']
                
                if start_index > 0:
                    prev_start = max(0, start_index - 24)
                    opt.append(discord.SelectOption(label="≪ 前のページ", value=f"page:{uuid}:{prev_start}"))
                
                slots = 25 - len(opt)
                end_index = start_index + slots
                
                for i in range(start_index, min(len(styles), end_index)):
                    style = styles[i]
                    opt.append(discord.SelectOption(label=style['name'], value=str(style['id'])))
                
                if end_index < len(styles):
                    if len(opt) == 25: opt.pop()
                    opt.append(discord.SelectOption(label="次のページ ≫", value=f"page:{uuid}:{end_index}"))

                sel = Select(placeholder="スタイルを選択…", options=opt, custom_id="select_voicevox_style")
                v.add_item(sel)
                await interaction.response.edit_message(view=v)
                return

            data = {"voice": f"voicevox:{value}"}
            um.write(interaction.user.id, data)

            _voicevox = await voicevox_data()
            if _voicevox[0] != 200:
                e = discord.Embed(title="音声変更", description=f"音声を **{value}** (詳細取得不可) に変更しました。", color=0x33bbdd)
                e.set_footer(text="※情報は正しく保存されていますが、音声の生成に失敗する可能性があります。")
            else:
                chara_style = await get_voicevox_speaker(value)
                e = discord.Embed(title="音声変更", description=f"音声を **{chara_style}** に変更しました。", color=0x3bd37b)

            await interaction.response.edit_message(embed=e, view=None)

        elif interaction.custom_id == "select_coeiroink":
            _coeiroink = await coeiroink_data()
            if _coeiroink[0] != 200:
                e = discord.Embed(title = "エラー", description = f"COEIROINKサーバーとの通信に失敗しました。", color = 0xfa0909)
                await interaction.response.edit_message(embed = e, view = None)
                return

            value = interaction.data['values'][0]
            charas = _coeiroink[1]

            if value.startswith("next:"):
                _vlen = int(value[len("next:"):])
                v = View()
                opt = []
                if _vlen > 24:
                    opt.append(discord.SelectOption(label="≪ 前のページ", value=f"prev:{_vlen - 24}"))
                
                remaining_slots = 25 - len(opt)
                end_index = _vlen + remaining_slots - 1
                
                for chara_id in range(_vlen, min(len(charas), end_index + 1)):
                    if chara_id == end_index and chara_id < len(charas) - 1:
                        opt.append(discord.SelectOption(label="他の音声を使用する", value=f"next:{chara_id + 1}"))
                    else:
                        chara = charas[chara_id]
                        opt.append(discord.SelectOption(label=f"{chara['speakerName']}", value=f"{chara['speakerUuid']}"))

                sel = Select(placeholder="キャラクターを選択…", options=opt, custom_id="select_coeiroink")
                v.add_item(sel)
                await interaction.response.edit_message(view=v)
                return

            target_chara = next((c for c in charas if c['speakerUuid'] == value), None)
            if not target_chara:
                e = discord.Embed(title="エラー", description="話者を検索中にエラーが発生しました。", color=0xfa0909)
                await interaction.response.edit_message(embed=e, view=None)
                return

            v = View()
            opt = []
            styles = target_chara['styles']

            if len(styles) <= 25:
                for style in styles:
                    opt.append(discord.SelectOption(label=style['styleName'], value=str(style['styleId'])))
            else:
                for i in range(24):
                    opt.append(discord.SelectOption(label=styles[i]['styleName'], value=str(styles[i]['styleId'])))
                opt.append(discord.SelectOption(label="他のスタイルを使用する", value=f"page:{value}:24"))

            sel = Select(placeholder="スタイルを選択…", options=opt, custom_id="select_coeiroink_style")
            v.add_item(sel)
            await interaction.response.edit_message(view=v)

        elif interaction.custom_id == "select_coeiroink_style":
            value = interaction.data['values'][0]

            if value.startswith("page:"):
                _, uuid, start_str = value.split(":")
                start_index = int(start_str)

                _coeiroink = await coeiroink_data()
                if _coeiroink[0] != 200:
                    e = discord.Embed(title="エラー", description="COEIROINKサーバーとの通信に失敗しました。", color=0xfa0909)
                    await interaction.response.edit_message(embed=e, view=None)
                    return

                charas = _coeiroink[1]
                target_chara = next((c for c in charas if c['speakerUuid'] == uuid), None)

                if not target_chara:
                    e = discord.Embed(title="エラー", description="話者を検索中にエラーが発生しました。", color=0xfa0909)
                    await interaction.response.edit_message(embed=e, view=None)
                    return
                
                v = View()
                opt = []
                styles = target_chara['styles']
                
                if start_index > 0:
                    prev_start = max(0, start_index - 24)
                    opt.append(discord.SelectOption(label="≪ 前のページ", value=f"page:{uuid}:{prev_start}"))

                slots = 25 - len(opt)
                end_index = start_index + slots

                for i in range(start_index, min(len(styles), end_index)):
                    style = styles[i]
                    opt.append(discord.SelectOption(label=style['styleName'], value=str(style['styleId'])))

                if end_index < len(styles):
                    if len(opt) == 25: opt.pop()
                    opt.append(discord.SelectOption(label="次のページ ≫", value=f"page:{uuid}:{end_index}"))

                sel = Select(placeholder="スタイルを選択…", options=opt, custom_id="select_coeiroink_style")
                v.add_item(sel)
                await interaction.response.edit_message(view=v)
                return

            data = {"voice": f"coeiroink:{value}"}
            um.write(interaction.user.id, data)

            _coeiroink = await coeiroink_data()
            if _coeiroink[0] != 200:
                e = discord.Embed(title="音声変更", description=f"音声を **{value}** (詳細取得不可) に変更しました。", color=0x33bbdd)
                e.set_footer(text="※情報は正しく保存されていますが、音声の生成に失敗する可能性があります。")
            else:
                chara_style = await get_coeiroink_speaker(value)
                e = discord.Embed(title="音声変更", description=f"音声を **{chara_style}** に変更しました。", color=0x3bd37b)

            await interaction.response.edit_message(embed=e, view=None)

        elif interaction.custom_id == "select_ojtalk":
            _ojtalk = await ojtalk_data()
            if _ojtalk[0] != 200:
                e = discord.Embed(title="エラー", description="Open JTalkの動作が未検証です！", color=0xfa0909)
                await interaction.response.edit_message(embed=e, view=None)
                return

            value = interaction.data['values'][0]
            charas = _ojtalk[1]

            if value.startswith("next:"):
                _vlen = int(value.split(":")[1])
                v = View()
                opt = []
                if _vlen > 24:
                    opt.append(discord.SelectOption(label="≪ 前のページ", value=f"prev:{_vlen - 24}"))
                
                chara_keys = list(charas.keys())
                remaining_slots = 25 - len(opt)
                end_index = _vlen + remaining_slots - 1

                for chara_id in range(_vlen, min(len(chara_keys), end_index + 1)):
                    if chara_id == end_index and chara_id < len(chara_keys) - 1:
                        opt.append(discord.SelectOption(label="他の音声を使用する", value=f"next:{chara_id + 1}"))
                    else:
                        chara = chara_keys[chara_id]
                        opt.append(discord.SelectOption(label=f"{chara}", value=f"{chara}"))
                
                sel = Select(placeholder="キャラクターを選択…", options=opt, custom_id="select_ojtalk")
                v.add_item(sel)
                await interaction.response.edit_message(view=v)
                return

            if value not in charas:
                e = discord.Embed(title="エラー", description="話者を検索中にエラーが発生しました。", color=0xfa0909)
                await interaction.response.edit_message(embed=e, view=None)
                return

            v = View()
            opt = []
            styles = [s for s in charas[value] if s.endswith(".htsvoice")]

            if len(styles) <= 25:
                for style in styles:
                    opt.append(discord.SelectOption(label=style[:-len(".htsvoice")], value=style))
            else:
                for i in range(24):
                    opt.append(discord.SelectOption(label=styles[i][:-len(".htsvoice")], value=styles[i]))
                opt.append(discord.SelectOption(label="他のスタイルを使用する", value=f"page:{value}:24"))
            
            sel = Select(placeholder="スタイルを選択…", options=opt, custom_id="select_ojtalk_style")
            v.add_item(sel)
            await interaction.response.edit_message(view=v)

        elif interaction.custom_id == "select_ojtalk_style":
            value = interaction.data['values'][0]

            if value.startswith("page:"):
                _, chara_name, start_str = value.split(":", 2)
                start_index = int(start_str)

                _ojtalk = await ojtalk_data()
                if _ojtalk[0] != 200:
                    e = discord.Embed(title="エラー", description="Open JTalkの動作が未検証です！", color=0xfa0909)
                    await interaction.response.edit_message(embed=e, view=None)
                    return

                charas = _ojtalk[1]
                if chara_name not in charas:
                    e = discord.Embed(title="エラー", description="話者を検索中にエラーが発生しました。", color=0xfa0909)
                    await interaction.response.edit_message(embed=e, view=None)
                    return

                v = View()
                opt = []
                styles = [s for s in charas[chara_name] if s.endswith(".htsvoice")]

                if start_index > 0:
                    prev_start = max(0, start_index - 24)
                    opt.append(discord.SelectOption(label="≪ 前のページ", value=f"page:{chara_name}:{prev_start}"))

                slots = 25 - len(opt)
                end_index = start_index + slots

                for i in range(start_index, min(len(styles), end_index)):
                    style = styles[i]
                    opt.append(discord.SelectOption(label=style[:-len(".htsvoice")], value=style))

                if end_index < len(styles):
                    if len(opt) == 25: opt.pop()
                    opt.append(discord.SelectOption(label="次のページ ≫", value=f"page:{chara_name}:{end_index}"))

                sel = Select(placeholder="スタイルを選択…", options=opt, custom_id="select_ojtalk_style")
                v.add_item(sel)
                await interaction.response.edit_message(view=v)
                return

            data = {"voice": f"ojtalk:{value[:-len('.htsvoice')]}"}
            um.write(interaction.user.id, data)

            e = discord.Embed(title="音声変更", description=f"音声を **{value[:-len('.htsvoice')]}** に変更しました。", color=0x3bd37b)
            await interaction.response.edit_message(embed=e, view=None)

def setup(bot):
    bot.add_cog(UserSettings(bot))