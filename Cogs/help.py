import discord
from discord.ext import commands

class User(commands.Cog):
    """docstring for user."""

    def __init__(self, client):
        self.client = client
    @commands.command()
    async def help(self, ctx):
        emb = discord.Embed(title = "Команды:", color = discord.Color.blue())
        emb.add_field(name = 'Общее', value = 'help, info')
        emb.add_field(name = 'Модерация', value = 'clear, ban, kick')
        emb.add_field(name = 'Дополнительно', value = 'sourceCode')
        emb.add_field(name = 'Музыка:', value = 'join, play, stop, pause, resume, skip, vol')
        emb.add_field(name = 'Настройка:', value = 'playMusic(on/off), removeJoinChannel, setJoinChannel(канал)')
        await ctx.send(embed = emb)
    @commands.command(name = 'info')
    async def info_(self, ctx):
        developer = self.client.get_user(615595496525791295)
        emb = discord.Embed(title = 'Сервер бота', color = discord.Color.blue(), url = 'https://discord.gg/FkjVW6mden')
        emb.set_author(name = 'Информаця:', icon_url = 'https://avatars.mds.yandex.net/get-zen-logos/246004/pub_5a9fbe7077d0e62d97459518_5acceae55991d30775549330/xxh')
        emb.set_thumbnail(url = developer.avatar_url)
        emb.add_field(name = 'Разработчик:', value = developer.name)
        emb.add_field(name = 'Имя бота на этом сервере:', value = self.client.user.name)
        emb.add_field(name = 'Cерверов с ботом:', value = len(self.client.guilds)) #[y.name for y in self.client.guilds]
        emb.set_footer(text = f'{self.client.user.name} - проект с открытым исходным кодом', icon_url = self.client.user.avatar_url)
        await ctx.send(embed = emb)
    @commands.command(name = 'sourceCode', aliases = ['code', 'source', 'github', 'bot'])
    async def code_(self, ctx):
        await ctx.send(file = discord.File('card.png'))
def setup(client):
    client.add_cog(User(client))
