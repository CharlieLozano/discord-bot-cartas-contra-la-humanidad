import discord
from discord.ext import commands
import random


class Fun(commands.Cog):
	def __init__(self, bot, age):
		self.bot = bot	

	def coinflip(self):
		return random.randint(0, 1)

	

	@commands.command()
	async def ping(self, ctx):
		await ctx.send("Pong")

	@commands.command()
	async def coin(self, ctx):
		await ctx.send(str(self.coinflip()))

	@commands.command()
	async def author(self, ctx):
		await ctx.send(the_author)


def setup(bot):
	bot.add_cog(Fun(bot, 23))
	print('Fun is loaded')


