import discord

async def play_error(message: discord.Message, error: str):
    error_value = error.split(": ")
    embed = discord.Embed(
        title = f"Error: {error_value[0]}",
        description = error_value[1],
        color = 0xfa0909
    )
    return embed