import discord
from discord.ext import commands
import pymongo
from PIL import Image, ImageFont, ImageDraw
import requests
import os

client = pymongo.MongoClient(f"mongodb+srv://qwithu:{os.environ.get('BOT_TOKEN')}@qwithu.ywfyc.mongodb.net/qwithudata?retryWrites=true&w=majority")
db = client['qwithudata']
collection = db['qwithucoll']

class Levels(commands.Cog):
    """docstring for Levels."""

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        word_len = round(len(message.content)/10)
        xp = collection.find_one({'_id': message.author.id})['xp']
        LEVEL = collection.find_one({'_id': message.author.id})['level']
        collection.update_one({'_id': message.author.id}, {"$inc": {'xp': word_len}})
        if not message.author.bot:
            if xp >= LEVEL*200:
                await message.channel.send(f'{message.author.mention}, ты получаешь уровень {LEVEL + 1}')
                collection.update_one({'_id': message.author.id}, {"$inc": {'level': 1}})

    @commands.command(name = 'level', aliases = ['rang', 'rank', 'me'])
    async def level_(self, ctx):
        XP = collection.find_one({'_id': ctx.author.id})['xp']
        LEVEL = collection.find_one({'_id': ctx.author.id})['level']
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
        # await ctx.send(f'Уровень: {LEVEL}\nОпыт: {xp}')
def setup(client):
    client.add_cog(Levels(client))
