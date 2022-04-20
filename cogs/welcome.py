import discord
from discord.ext import commands
import asyncio
import datetime
import sqlite3

class WelcomeCog(commands.Cog, name='Welcome'):

	def __init__(self,bot):
		self.bot = bot

	@commands.Cog.listener():
	async def on_member_join(self, member)
		db = sqlite3.connect('main.sqlite')
		cursor = db.cursor()
		cursor.execute(f'SELECT channel_id FROM main WHERE guild_id = {member.guild.id}')
		result = cursor.fetchone()
		if result is None:
			return
		else:
			cursor.execute(f'SELECT msg FROM main WHERE guild_id = {member.guild.id}')
			result1 = cursor.fetchone()
			embed = discord.Embed(colour=0x95efcc, description=f"{result1[0]}")
			embed.set_thumbnail(url=f"{member.avatar_url}")
			embed.set_author(name=f"{member.name}", icon_url=f"{member.avatar_url}")
			embed.set_footer(text=f"{member.guild}", icon_url=f"{member.guild.icon_url}")
			embed.timestamp = datetime.datetime.utcnow()

			channel = bot.get_channel(id=809567750431178825)

			await channel.send(embed=embed)


	@commands.group(invoke_without_command = True)
	async def welcome(self,ctx):
		await ctx.send('Available Setup Commands: \nWelcome channel <#channel>\nwelcome text<message>')

	@welcome.command()
	async def channel(self, ctx, channel:discord.TextChannel):
		if ctx.message.author.guild_permissions.manage_messages:
			db = sqlite3.connect('main.sqlite')
			cursor = db.cursor()
			cursor.execute(f'SELECT channel_id FROM main WHERE guild_id = {ctx.guild.id}')
			result = cursor.fetchone()
			if result is None:
				sql = ("INSERT INTO main(guild_id, channel_id) VALUES(?,?)")
				val = (ctx.guild.id, channel.id)
				await ctx.send(f"Channel has been set to {channel.mention}")
			elif result is not None:
				sql = ("UPDATE main SET channel_id = ? WHERE guild_id = ?")
				val = (channel.id, ctx.guild.id)
				await ctx.send(f"Channel has been updated to {channel.mention}")
			cursor.execute(sql, val)
			db.commit()
			cursor.close()
			db.close()

	@welcome.command()
	async def text(self, ctx, *, text):
		if ctx.message.author.guild_permissions.manage_messages:
			db = sqlite3.connect('main.sqlite')
			cursor = db.cursor()
			cursor.execute(f'SELECT channel_id FROM main WHERE guild_id = {ctx.guild.id}')
			result = cursor.fetchone()
			if result is None:
				sql = ("INSERT INTO main(guild_id, msg) VALUES(?,?)")
				val = (ctx.guild.id, text)
				await ctx.send(f"Message has been set to {text}")
			elif result is not None:
				sql = ("UPDATE main SET msg = ? WHERE guild_id = ?")
				val = (text, ctx.guild.id)
				await ctx.send(f"Message has been updated to {text}")
			cursor.execute(sql, val)
			db.commit()
			cursor.close()
			db.close()

def setup(bot):
	bot.add_cog(WelcomeCog(bot))
	print('WelcomeCog is loaded')