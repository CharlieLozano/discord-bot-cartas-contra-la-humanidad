import discord
import json 
import os
from discord.ext import commands, tasks
from PIL import Image 
from io import BytesIO
import random

with open('config.json') as f:
	config = json.load(f)

intents = discord.Intents().all()
intents.members = True 
bot = commands.Bot(command_prefix = ".m ", intents=intents)
bot.load_extension('cogs.Fun')
bot.load_extension('cogs.cah')
bot.load_extension('cogs.botella')


@bot.event
async def on_ready():
	print("Bot is ready")
	

@bot.command()
async def slap(ctx, members: commands.Greedy[discord.Member], *, reason='no reason'):
	slapped = ", ".join(x.name for x in members)
	await ctx.send('{} just got slapped for {}'.format(slapped, reason))


@bot.command()
async def kick(ctx, members: commands.Greedy[discord.Member]):
	msg = ""
	for member in members:
		msg += (str(member.mention) + " ")
	await ctx.send('{} han sido pateados '.format(msg))
	with open('tenor.gif', 'rb') as f:
	    picture = discord.File(f)
	    await ctx.send(file=picture)
	


bot.run(config["code"])