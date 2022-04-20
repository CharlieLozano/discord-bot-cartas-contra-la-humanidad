import discord
from discord.ext import commands
import random
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
import math


class botella(commands.Cog):
	def __init__(self, bot, age):
		self.bot = bot	
		self.db = {}
		self.msgs = []
	

	@commands.command()
	async def botella(self, ctx):
		channel = str(ctx.channel.id)

		self.db[channel] = botella_template()

		embed = discord.Embed(title="¡Botella!", description="**Jugadores**\nPancho\nPancha \nPanchiux \nPancheco \n\n🟢 Unirse :: 🔴 Retirarse :: 🔄 Girar la botella", color=0x13f2a1)
		embed.set_footer(text="El juego se cerrara por inactividad en: 24hrs")


		msg = await ctx.send(embed=embed)
		await msg.add_reaction("🟢")
		await msg.add_reaction("🔴")
		await msg.add_reaction("🔄")
		self.db[channel]['msg_id'].append(msg.id)

	@commands.command()
	async def bote(self, ctx):
		channel = str(ctx.channel.id)


		center = 250
		radius = 200

		def get_x(angle):	
			rad = math.radians(angle)
			width, height  = img.size
			x = int(center + (radius * (math.sin(rad))) - 15)

			return x

		def get_y(angle):	
			rad = math.radians(angle + 180)
			width, height  = img.size
			y = int(center + (radius * (math.cos(rad))) - 15)

			return y


		font = ImageFont.truetype("OpenSans-Bold.ttf", 30)
		img = Image.new('RGB', (500, 500), color = 'white')
		draw = ImageDraw.Draw(img)


		marisa= Image.open("marimari.jpg")
		size = (500,500)
		print(get_x(180))
		print(get_y(180))
		marisa.thumbnail((120,120))

		img.paste(marisa,(get_x(150),get_y(150)), None)

	
		img.save("botella.jpg")
		await ctx.send(file = discord.File("botella.jpg"))

def botella_template():
	result = {
		'msg_id': [],
		'last_active': None,
		'players': {}

	}

	return result

def setup(bot):
	bot.add_cog(botella(bot, 23))
	print('Botella comprada!')
