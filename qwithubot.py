#import module
from PIL import Image, ImageFont, ImageDraw
import time
import discord
import youtube_dl
import sqlite3
import os
import json
from typing import List, Tuple, Optional
import re
import dpath.util
import requests

#setting
from discord.ext import commands
print("all ok")
client = commands.Bot(command_prefix = 'q+', intents = discord.Intents.all())
client.remove_command("help")

db = sqlite3.connect('bot.db')
cursor = db.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS server (
    serverID INT,
    musicCommand INT,
    linkModer INT,
    badWordsModer INT,
    inviteModer INT,
    memberLevel INT,
    clearCommand INT,
    serverCommand INT,
    memberJoinMessage INT,
    memberRemoveMessage INT,
    reactionChannel INT,
    reaction_in TEXT,
    ignoreLinkChannel INT,
    ignoreInviteLinkChannel INT,
    ignoreBadWordsChannel INT,
    music_playing TEXT,
    SPrefix TEXT
)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS members (
    member_ID INT,
    member_level INT,
    member_warns INT,
    member_XP BIGINT,
    member_cash BIGINT
)""")
db.commit()

youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


@client.event
#if bot ready
async def on_ready():
    await client.change_presence(activity=discord.Game(name='q+help'))
    for guild in client.guilds:
            if cursor.execute(f"SELECT serverID FROM server WHERE serverID = {guild.id}").fetchone() == None:
                cursor.execute("INSERT INTO server VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (guild.id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '0', 0, 0, 0, '0', '0'))
                db.commit()
                print(f'[LOG] data insert. Guild: {guild.name}')

            for member in guild.members:
                if cursor.execute(f"SELECT member_ID FROM members WHERE member_ID = {member.id}").fetchone() == None:
                    cursor.execute("INSERT INTO members VALUES (?, ?, ?, ?, ?)",
                    (member.id, 1, 0, 0, 0))
                    db.commit()
                    print(f'[LOG] data insert. member: {member.display_name}')
    print('Logged on')
@client.event
async def on_guild_join(guild):
    cursor.execute("INSERT INTO server VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    (guild.id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '0', 0, 0, 0, '0', '0'))
    db.commit()
    print('[LOG] data insert')
@client.event
async def on_guild_remove(guild):
    cursor.execute(f"DELETE FROM server WHERE serverID = {guild.id}")
    db.commit()
    print('[LOG] data delete')
@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.author == client.user:
        return
    XP = cursor.execute(f"SELECT member_XP FROM members WHERE member_ID = {message.author.id}").fetchone()[0]
    word_XP = len(message.content)
    cursor.execute(f"UPDATE members SET member_XP = {XP + word_XP} WHERE member_ID = {message.author.id}")
    db.commit()
    LEVEL = cursor.execute(f"SELECT member_level FROM members WHERE member_ID = {message.author.id}").fetchone()[0]

    if XP >= 200 * LEVEL:
        await message.channel.send(f'{message.author.mention}, ты получаешь уровень {LEVEL}!')
        cursor.execute(f"UPDATE  members SET member_Level = {LEVEL + 1} WHERE member_ID = {message.author.id}")
        db.commit()
        cursor.execute(f"UPDATE  members SET member_XP = {XP - 200} WHERE member_ID = {message.author.id}")
        db.commit()
    #for server st1m3x standoff2 and Qwithu programme
    if message.channel.id in [768049320623603722, 779274877995581460]:
        await message.add_reaction('🤣')
@client.command()
async def level(ctx):
    try:
        XP = cursor.execute(f"SELECT member_XP FROM members WHERE member_ID = {ctx.author.id}").fetchone()[0]
        LEVEL = cursor.execute(f"SELECT member_level FROM members WHERE member_ID = {ctx.author.id}").fetchone()[0]

        img = Image.new('RGBA', (300, 100), '#232529')
        url = str(ctx.author.avatar_url)[:-10]

        response = requests.get(url, stream = True).raw
        response = Image.open(response)
        response = response.resize((80, 80))

        img.paste(response, (10, 10))

        idraw = ImageDraw.Draw(img)
        name = ctx.author.name + "#" + str(ctx.author.discriminator)
        headline = ImageFont.truetype('impact.ttf', size = 18)
        xp_text = ImageFont.truetype('arial.ttf', size = 16)

        idraw.text((100, 10), name, font = headline)
        idraw.text((100, 35), f'опыт: {XP}/{200 * LEVEL}', font = xp_text)
        idraw.text((100, 60), f'{LEVEL} уровень', font = xp_text)
        img.save('card.png')

        await ctx.send(file = discord.File('card.png'))
    except Exception as err:
        await ctx.send(err)
@client.command()
@commands.has_permissions(administrator = True)
async def set_level(ctx, level: int, member: discord.Member):
    cursor.execute(f"UPDATE members SET member_level = {level} WHERE member_ID = {member.id}")
    db.commit()
    await ctx.message.add_reaction('✅')
#member join
@client.event
async def on_member_join(member):
    cursor.execute(f"SELECT memberJoinMessage FROM server WHERE serverID = {member.guild.id}")
    if cursor.fetchone()[0] == 0:
        return
    channel = client.get_channel(cursor.execute(f"SELECT memberJoinMessage FROM server WHERE serverID = {member.guild.id}").fetchone()[0])
    emb = discord.Embed(description = f'Привет, {member}! Тебя приветствует сервер {member.guild.name}, а я его бот. Напиши q+help, чтобы узнать больше о моих возможностях!', color = discord.Color.blue())
    emb.set_thumbnail(url = member.avatar_url)
    await channel.send(embed = emb)
@client.event
async def on_member_remove(member):
    adm_user = client.get_user(615595496525791295)
    await adm_user.send(f'{member} вышел с сервера {member.guild.name}:(')
#ban
@client.command(pass_context = True)
@commands.has_permissions(administrator = True)
async def ban(ctx, member: discord.Member, *, reason = None):
    emb = discord.Embed(title = 'Участник забанен на сервере', color = discord.Color.red())
    emb.set_author(name = member, icon_url = member.avatar_url)
    emb.add_field(name = 'Модератор:', value = client.user.name )
    emb.set_footer(text = 'Забанен пользователем {0.author}'.format(ctx))
    await ctx.send(embed = emb)
    await member.ban(reason = reason)
#kick
@client.command()
@commands.has_permissions(administrator = True)
async def kick(ctx, member: discord.Member, reason = None):
    emb = discord.Embed(title = 'Участника выгнали с сервера', color = discord.Color.red())
    emb.set_author(name = member, icon_url = member.avatar_url)
    emb.add_field(name = 'Модератор:', value = client.user.name )
    emb.set_footer(text = 'Выгнан пользователем {0.author}'.format(ctx))
    await ctx.send(embed = emb)
    await member.kick(reason = reason)
#clear message
@client.command(pass_context = True)
async def clear(ctx, amout : int):
    delmsg = amout + 1
    await ctx.channel.purge(limit = delmsg)
    message = await ctx.send(f'Я очистел {amout} сообщений')
    time.sleep(3)
    await message.delete()
@client.command()
async def sourceCode(ctx):
    await ctx.send(file = discord.File('qwithubot —sourceCode.py'))
@client.command()
async def info(ctx):
    developer = client.get_user(615595496525791295)
    emb = discord.Embed(title = 'Сервер бота', color = discord.Color.blue(), url = 'https://discord.gg/FkjVW6mden')
    emb.set_author(name = 'Информаця:', icon_url = 'https://avatars.mds.yandex.net/get-zen-logos/246004/pub_5a9fbe7077d0e62d97459518_5acceae55991d30775549330/xxh')
    emb.set_thumbnail(url = developer.avatar_url)
    emb.add_field(name = 'Разработчик:', value = developer.name)
    emb.add_field(name = 'Имя бота на этом сервере:', value = client.user.name)
    emb.add_field(name = 'Список серверов с ботом:', value = [y.name for y in client.guilds])
    emb.set_footer(text = f'{client.user.name} - проект с открытым исходным кодом', icon_url = client.user.avatar_url)
    await ctx.send(embed = emb)


@client.command()
async def join(ctx):
    global voice
    if not ctx.author.voice:
        emb = discord.Embed(description = 'Вы не в голосовом какнале!', color = discord.Color.red())
        await ctx.send(embed = emb)
        return
    channel = ctx.message.author.voice.channel
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    if voice and voice.connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'
PATTERNS = [
    re.compile(r'window\["ytInitialData"\] = (\{.+?\});'),
    re.compile(r'var ytInitialData = (\{.+?\});'),
]

session = requests.Session()
session.headers['User-Agent'] = USER_AGENT


def get_ytInitialData(url: str) -> Optional[dict]:
    rs = session.get(url)

    for pattern in PATTERNS:
        m = pattern.search(rs.text)
        if m:
            data_str = m.group(1)
            return json.loads(data_str)

def search_youtube(text_or_url: str) -> List[Tuple[str, str]]:
    if text_or_url.startswith('http'):
        url = text_or_url
    else:
        text = text_or_url
        url = f'https://www.youtube.com/results?search_query={text}'

    items = []

    data = get_ytInitialData(url)
    if not data:
        return items

    videos = dpath.util.values(data, '**/videoRenderer')
    if not videos:
        videos = dpath.util.values(data, '**/playlistVideoRenderer')

    for video in videos:
        if 'videoId' not in video:
            continue

        url = 'https://www.youtube.com/watch?v=' + video['videoId']
        try:
            title = dpath.util.get(video, 'title/runs/0/text')
        except KeyError:
            title = dpath.util.get(video, 'title/simpleText')
        items.append((url))

    return items[0]


@client.command()
async def play(ctx, *, video_name):
    if cursor.execute(f"SELECT musicCommand FROM server WHERE serverID = {ctx.guild.id}").fetchone()[0] == 0:
        emb = discord.Embed(title = 'Администратор сервера отключил эту возможность.', color = discord.Color.red())
        await ctx.send(embed = emb)
        return
    url = search_youtube(video_name)
    global music_message
    global v_client
    v_client = ctx.voice_client
    if not ctx.author.voice:
        emb = discord.Embed(description = 'Вы не в голосовом какнале!', color = discord.Color.red())
        await ctx.send(embed = emb)
        return
    channel = ctx.message.author.voice.channel
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    try:
        if voice and voice.connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
    except AttributeError:
        print('[LOG] Attribute Error')
    ctx.voice_client.stop()
    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop = client.loop)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
    emb = discord.Embed(
    title = player.title,
    color = discord.Color.blue(),
    url = url)
    emb.add_field(name = 'Управление:',
    value = 'Вы можете использовать команды pause, resume и stop для управления музыкой.')
    music_message = await ctx.send(embed = emb)

@client.command()
async def stop(ctx):
    try:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
    except AttributeError:
        print('[LOG] AttributeError')
    for file in os.listdir('./'):
        if file.endswith('.webm'):
            time.sleep(1)
            try:
                os.remove(file)
                print('[LOG] файл удален')
            except PermissionError:
                print('[LOG] Не удалось удалить файл')
@client.command()
async def pause(ctx):
    ctx.voice_client.pause()
    await ctx.message.add_reaction('✅')

@client.command()
async def resume(ctx):
    await ctx.message.add_reaction('✅')
    ctx.voice_client.resume()


@client.command()
@commands.has_permissions(administrator = True)
async def setJoinChannel(ctx, channel: discord.TextChannel):
    cursor.execute(f"UPDATE server SET memberJoinMessage = {channel.id} WHERE serverID = {ctx.guild.id}")
    db.commit()
    await ctx.send(f'{channel.mention} теперь канал для приветствий!')

@client.command()
@commands.has_permissions(administrator = True)
async def removeJoinChannel(ctx):
    cursor.execute(f"UPDATE server SET memberJoinMessage = {0} WHERE serverID = {ctx.guild.id}")
    db.commit()
    await ctx.send('Канал для приветствий был отключён.')
@client.command()
@commands.has_permissions(administrator = True)
async def playMusic(ctx, status = None):
    if status == 'on':
        cursor.execute(f"UPDATE server SET musicCommand = {1} WHERE serverID = {ctx.guild.id}")
        db.commit()
        await ctx.message.add_reaction('✅')
    elif status == 'off':
        cursor.execute(f"UPDATE server SET musicCommand = {0} WHERE serverID = {ctx.guild.id}")
        db.commit()
        await ctx.message.add_reaction('✅')
    else:
        emb = discord.Embed(title = 'Укажите значение (on/off)', color = discord.Color.red())
        await ctx.send(embed = emb)
        return
#help command
@client.command(pass_context = True)
async def help(ctx):
    emb = discord.Embed(title = "Команды:", color = discord.Color.blue())
    emb.add_field(name = 'Общее', value = 'help, info')
    emb.add_field(name = 'Модерация', value = 'clear, ban, kick')
    emb.add_field(name = 'Дополнительно', value = 'sourceCode')
    emb.add_field(name = 'Музыка:', value = 'join, play, stop, pause, resume')
    emb.add_field(name = 'Настройка:', value = 'playMusic(on/off), removeJoinChannel, setJoinChannel(канал)')
    await ctx.send(embed = emb)
token = os.environ.get('BOT_TOKEN')
client.run(token)
