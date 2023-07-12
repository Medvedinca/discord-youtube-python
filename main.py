import os
import asyncio
from pytube import YouTube
import re
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
intents.voice_states = True
client = commands.Bot(command_prefix='!', intents=intents)

target_channel_id = 1128358101402263612
target_voice_id = 1001371112942346384


def is_youtube_link(text):
    pattern = r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/).+"
    match = re.search(pattern, text)
    return bool(match)


@client.event
async def on_ready():
    print('Бот готов')


@client.event
async def on_message(message):
    # Избежание рекурсии
    if message.author == client.user:
        return

    channel = client.get_channel(target_channel_id)

    # Проверяем, содержит ли сообщение упоминание бота
    if client.user in message.mentions:
        mentioned_message = message.content.replace(client.user.mention, "")

        if is_youtube_link(mentioned_message):
            url = mentioned_message.strip()
            try:
                yt = YouTube(url)
                video = yt.streams.filter(only_audio=True).first()
                video.download(output_path=".", filename="audio.mp3")
                print("Аудиофайл успешно загружен!")
            except Exception as e:
                print("Произошла ошибка при скачивании:", str(e))

            # Подключение к аудиоканалу
            channel_id = target_voice_id
            voice_channel = client.get_channel(channel_id)
            voice_client = await voice_channel.connect()

            # Воспроизведение скачанного аудиофайла
            audio_source = discord.FFmpegPCMAudio(executable=r'C:\ffmpeg-2023-07-10-git-1c61c24f5f-full_build\bin\ffmpeg.exe', source='audio.mp3')
            voice_client.play(audio_source)

            while voice_client.is_playing():
                await asyncio.sleep(1)

            # Отключение от аудиоканала
            await voice_client.disconnect()

            # Удаление скачанного аудиофайла
            os.remove('audio.mp3')

        await channel.send(mentioned_message)
    await client.process_commands(message)


client.run('')
