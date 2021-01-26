import discord
import os
import pymongo
from discord.ext import commands

client = pymongo.MongoClient(f"mongodb+srv://qwithu:{os.environ.get('TABLE_PASS')}@qwithu.ywfyc.mongodb.net/qwithudata?retryWrites=true&w=majority")
db = client['qwithudata']
collection = db['qwithucoll']

def get_prefix(bot, message):
    prefix = collection.find_one({'_id': message.guild.id})['prefix']
    return prefix
TokenFile = open("./data/Token.txt", "r")

OWNERID = 615595496525791295

bot = commands.Bot(command_prefix = get_prefix, case_insensitive = True, owner_id = 615595496525791295, intents = discord.Intents.all())
bot.remove_command('help')


@bot.event
async def on_command_error(ctx,error):
    embed = discord.Embed(
    title='',
    color=discord.Color.red())
    if isinstance(error, commands.CommandNotFound):
        pass
    if isinstance(error, commands.MissingPermissions):
        embed.add_field(name=f'Invalid Permissions', value=f'You dont have {error.missing_perms} permissions.')
        await ctx.send(embed=embed)
    else:
        embed.add_field(name = f':x: Terminal Error', value = f"```{error}```")
        await ctx.send(embed = embed)
        raise error

@bot.command()
async def load(ctx, extension):
    if ctx.author.id == OWNERID:
        bot.load_extension(f'Cogs.{extension}')
        await ctx.send(f"Enabled the Cog!")
    else:
        await ctx.send(f"You are not cool enough to use this command")

async def unload(ctx, extension):
    if ctx.author.id == OWNERID:
        bot.unload_extension(f'Cogs.{extension}')
        await ctx.send(f"Disabled the Cog!")
    else:
        await ctx.send(f"You are not cool enough to use this command")

@bot.command(name = "reload")
async def reload_(ctx, extension):
    if ctx.author.id == OWNERID:
        bot.reload_extension(f'Cogs.{extension}')
        await ctx.send(f"Reloaded the Cog!")
    else:
        await ctx.send(f"You are not cool enough to use this command")
@bot.command(name = 'delete_table', aliases = ['del', 'delete'])
@commands.is_owner()
async def delete_table_(ctx):
    collection.delete_many({})
    await ctx.send('Data base was deleted!')

@bot.command(name = 'load_table', aliases = ['load_t', 'lod', 'loadt'])
@commands.is_owner()
async def load_table_(ctx):
    members_count = 0
    guilds_count = 0

    for g in bot.guilds:
        if collection.count_documents({'_id': g.id}) == 0:
            collection.insert_one({'_id': g.id, 'prefix': 'q+'})
            guilds_count += 1
        for member in g.members:
            if collection.count_documents({'_id': member.id}) == 0:
                collection.insert_one({'_id': member.id, 'xp': 0, 'level': 0, 'guild_id': member.guild.id})
                members_count += 1
    await ctx.send(f'Insert {members_count} members and {guilds_count} guilds!')

@bot.command(name = 'set_prefix', aliases = ['prefix', 'pref'])
@commands.has_permissions(administrator = True)
async def set_prefix_(ctx, prefix: str):
    collection.update_one({'_id': ctx.guild.id}, {'$set': {'prefix': prefix}})
    await ctx.send(f'Префикс изменён на: {prefix}')
for filename in os.listdir('./Cogs'):
    if filename.endswith('.py'):
        try:
            bot.load_extension(f'Cogs.{filename[:-3]}')
        except Exception as e:
            print(e)


bot.run(os.environ.get('BOT_TOKEN'))
