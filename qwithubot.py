#import module
import time
import discord
import youtube_dl
import sqlite3
import os
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
    await client.change_presence(activity=discord.Game(name='q+help')) #тех. работы〡
    print('Logged on')
@client.event
async def on_guild_join(guild):
    if cursor.execute("SELECT serverID FROM server").fetchone() == guild.id:
        return
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
    # if not message.content.find('https://') == -1:
    #     await message.delete()
    #     await message.channel.send('{0.author}, оставлять ссылки на нашем сервере запрещено!'.format(message))
    if message.author == client.user:
        if message.content.startswith('Я очистел'):
            time.sleep(2)
            await message.delete()
    #for server st1m3x standoff2 and Qwithu programme
    if message.channel.id in [768049320623603722, 779274877995581460]:
        await message.add_reaction('🤣')
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
    await ctx.send(f'Я очистел {amout} сообщений')
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

@client.command()
async def play(ctx, url):
    if cursor.execute(f"SELECT musicCommand FROM server WHERE serverID = {ctx.guild.id}").fetchone()[0] == 0:
        emb = discord.Embed(title = 'Администратор сервера отключил эту возможность.', color = discord.Color.red())
        await ctx.send(embed = emb)
        return
    if str(url).find('https://') == -1:
        emb = discord.Embed(
        title = f'{ctx.message.author}, я могу проигрывать аудио только с помощью ссылки на YouTube видео!',
        color = discord.Color.red())
        await ctx.send(embed = emb)
        return
    global music_message
    global v_client
    v_client = ctx.voice_client
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
    await ctx.voice_client.disconnect()
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
    #create embed
    emb = discord.Embed(title = "Команды:", color = discord.Color.blue())
    emb.add_field(name = 'Общее', value = 'help, info')
    emb.add_field(name = 'Модерация', value = 'clear, ban, kick')
    emb.add_field(name = 'Дополнительно', value = 'sourceCode')
    emb.add_field(name = 'Музыка:', value = 'join, play, stop, pause, resume')
    emb.add_field(name = 'Настройка:', value = 'playMusic(on/off), removeJoinChannel, setJoinChannel(канал)')
    await ctx.send(embed = emb)
token = os.environ.get('BOT_TOKEN')
client.run(token)
