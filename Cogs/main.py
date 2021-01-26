import discord
from discord.ext import commands
import pymongo
import os

client = pymongo.MongoClient(f"mongodb+srv://qwithu:{os.environ.get('TABLE_PASS')}@qwithu.ywfyc.mongodb.net/qwithudata?retryWrites=true&w=majority")
db = client['qwithudata']
collection = db['qwithucoll']

class User(commands.Cog):
    """docstring for user."""

    def __init__(self, client):
        self.client = client
    @commands.Cog.listener()
    async def on_ready(self):
        for g in self.client.guilds:
            if collection.count_documents({'_id': g.id}) == 0:
                collection.insert_one({'_id': g.id, 'prefix': 'q+'})
                print(f'insert guild: {g.name}')
            for member in g.members:
                if collection.count_documents({'_id': member.id}) == 0:
                    collection.insert_one({'_id': member.id, 'xp': 0, 'level': 0, 'guild_id': member.guild.id})
                    print(f'insert member: {member.display_name}')
        print('all ok')
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if collection.count_documents({'_id': member.id}) == 0:
            collection.insert_one({'_id': member.id, 'xp': 0, 'level': 0, 'guild_id': member.guild.id})
            print(f'insert member: {member.display_name}')
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if collection.count_documents({'_id': guild.id}) == 0:
            collection.insert_one({'_id': guild.id, 'prefix': 'q+'})
            print(f'insert guild: {guild.name}')
def setup(client):
    client.add_cog(User(client))
