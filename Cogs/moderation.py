import discord
from discord.ext import commands
from asyncio import sleep

class Moderator(commands.Cog):
    """docstring for Moderator."""

    def __init__(self, client):
        self.client = client

    @commands.command(name = 'ban')
    @commands.has_permissions(ban_members = True)
    async def ban_(self, ctx, member: discord.Member = None, *, reason = None):
        if member is None:
            await ctx.send(embed = discord.Embed(description = f'{ctx.author}, вы не указали пользователя.', color = discor.Color.red()))
        else:
            await member.ban(reason = reason)
            emb = discord.Embed(title = 'Участник забанен на сервере', color = discord.Color.red())
            emb.set_author(name = member, icon_url = member.avatar_url)
            emb.add_field(name = 'Модератор:', value = self.client.user.mention )
            emb.set_footer(text = 'Забанен пользователем {0.author}'.format(ctx))
            await ctx.send(embed = emb)

    @commands.command(name = 'kick')
    @commands.has_permissions(kick_members = True)
    async def ban_(self, ctx, member: discord.Member = None, *, reason = None):
        if member is None:
            await ctx.send(embed = discord.Embed(description = f'{ctx.author}, вы не указали пользователя.', color = discor.Color.red()))
        else:
            await member.kick(reason = reason)
            emb = discord.Embed(title = 'Участник выгнан сервере', color = discord.Color.red())
            emb.set_author(name = member, icon_url = member.avatar_url)
            emb.add_field(name = 'Модератор:', value = self.client.user.mention )
            emb.set_footer(text = 'Выгнан пользователем {0.author}'.format(ctx))
            await ctx.send(embed = emb)

    @commands.command(name = 'clear', aliases = ['очистить'])
    @commands.has_permissions(manage_messages = True)
    async def clear_(self, ctx, limit = None):
        if limit is None:
            await ctx.send(f'**{ctx.author.name}**, вы должны указать количество сообщений.')
        else:
            delete = await ctx.channel.purge(limit = int(limit))
            message = await ctx.send(f'Было удалено {len(delete)} сообщений.')
            await sleep(4)
            await message.delete()

def setup(client):
    client.add_cog(Moderator(client))
