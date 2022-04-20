import discord
from discord.ext import commands , tasks
import json
from json import JSONEncoder
import re
import random 
from random import randint
import asyncio
import copy
import time
import os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 



class cah(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.database = load_cah()
		self.players = {}

		with open("cah/default_answers.json", encoding='utf-8') as f:
			answers = json.load(f)

		self.answers = answers

		with open("cah/default_questions.json", encoding='utf-8') as fi:
			questions = json.load(fi)
		
		self.questions = questions


	@commands.Cog.listener()
	async def on_ready(self):

		
		#---Debug----
		#Erase data to test
		data = {}
		self.database = {}

		with open("cah/cah_data.json", "w") as f:
			json.dump(data, f)
		#------------

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):

		channel = str(payload.channel_id)
		author = str(payload.user_id)
		author_tag = await self.bot.fetch_user(payload.user_id)
		message = payload.message_id
		send_channel = self.bot.get_channel(int(payload.channel_id))
		emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣","5️⃣","6️⃣","7️⃣", "8️⃣"]

		########################
		### Open Invitations ###
		########################

		if channel in self.database and message in self.database[channel]["open_invitations"] and not author_tag.bot and payload.emoji.name == "🍬": 
			channel_send = self.bot.get_channel(int(channel))
			member = await self.bot.fetch_user(int(author))
			
			if self.database[channel]["p_number"] < 8:
				
				if author not in self.database[channel]["players"]:
					

					try:
						embed3=discord.Embed(title="Mensaje de confirmación",description=("La partida se ha creado con éxito. Para salirse use el comando `cah salir` con el prefijo adecuado"), color=0x28fc28)
						await member.send(embed=embed3)		
					except Exception: 
						embed2=discord.Embed(title="Acceso denegado",  description="No se pudo enviar mensaje directo. Permita que usuarios dentro del mismo servidor puedan enviarle mensajes.", color=0xff1717)
						await channel_send.send(embed=embed2)	
						return
					
					embed = discord.Embed(title=None, description=(member.mention + " se ha unido a la partida."), color=0x32a883)
					await channel_send.send(embed=embed)	

					if str(member.id) in self.players:
						self.players[str(member.id)].append(channel)
					else:  
						self.players[str(member.id)] = [channel]
					self.database[channel]["players"][author] = player_template()
					
					if self.database[channel]["on_game"] == True:
						deal_cards(self.database, channel, author)
						if self.database[channel]["phase"] == "reveal":
							self.database[channel]["waiting_for"].append(author)
					
					self.database[channel]["p_number"] += 1
					print(self.database[channel]["p_number"])
					if self.database[channel]["p_number"] >= 8:
						await full_house(self, channel)
					

				else:
					embed = discord.Embed(title=None, description=("No se puede unir dos veces a una partida."), color=0xd63e3e)
					await member.send(embed=embed)

			else:
				embed = discord.Embed(title=None,description="La sala está llena.", color=0xd63e3e)
				to_del = await channel_send.send(embed=embed)
				await asyncio.sleep(3)
				await to_del.delete()


		#######################
		### Popularity Vote ###
		#######################

		if channel in self.database and message in self.database[channel]["popularity_id"] and payload.emoji.name in emojis and not author_tag.bot:
			index = emojis.index(payload.emoji.name)
			winner_str = self.database[channel]["voters"][index]

			if author == winner_str:
				pass
			else:
				self.database[channel]["players"][winner_str]["popularity"] += 1
				winner_tag = await self.bot.fetch_user(int(winner_str))


		###############
		### Phases ####
		###############

		elif author in self.players:
			db = self.database

			################################################
			## Checking player, message, channel relation ##
			################################################

			for e in self.players[author]:


				#######################
				## Accept Invitation ##
				#######################

				if e in db and str(message) in db[e]["dm_invitations"] and payload.emoji.name == "✅":
					
					member = await self.bot.fetch_user(payload.user_id)

					if self.database[e]["p_number"] >= 8:
						embed = discord.Embed(title=None,description="La sala está llena.", color=0xd63e3e)
						await member.send(embed=embed)

					else:
						self.database[e]["players"][author] = player_template()
						self.database[e]["dm_invitations"].pop(str(message))
						self.database[e]["p_number"] += 1
						print(self.database[e]["p_number"] )

						if self.database[e]["p_number"] >= 8:
							await full_house(self, e)

						if self.database[e]["on_game"] == True:
							deal_cards(self.database, e, author)
							if self.database[e]["phase"] == "reveal":
								self.database[e]["waiting_for"].append(author)


						
						user_send = self.bot.get_channel(payload.channel_id)
						channel_send = self.bot.get_channel(int(e))
						
						embed = discord.Embed(title=None, description=(member.mention + " ha aceptado la invitación."), color=0x32a883)
						embed2 = discord.Embed(title=None, description=("Invitación aceptada."), color=0x32a883)

						await user_send.send(embed=embed2)
						await channel_send.send(embed=embed)
						

						


				##################
				## Reveal Phase ##
				##################

				if e in db and message in db[e]["reveal_id"] and payload.emoji.name == "✅" and db[e]["phase"] == "reveal":
					if author == self.database[e]["judge"]:
						
						lenght = len(db[e]["questions"])
						new_card = db[e]["questions"][more_random(lenght-1)]
						send_channel = self.bot.get_channel(int(payload.channel_id))

						update_reveal(self, e)

						await reveal_question(self, e, new_card, send_channel)
						

						for player in self.database[e]["players"]:
							if player != self.database[e]["judge"]:

								await play_card_msg(self, channel, player, emojis, new_card)
						
						discard_question(self.database, channel, new_card)
						self.database[e]["phase"] = "playing"



				#########################
				## Playing phase ##
				#########################

				elif e in db and message in db[e]["reaction_id"] and payload.emoji.name in emojis and db[e]["phase"] == "playing":
					
					index = emojis.index(payload.emoji.name)
					card = self.database[e]["players"][author]["hand"][index]


					update_playing(self, e, author, card)

					if self.database[e]["players"][author]["remaining"] == 0:
						choice_made(self, e, message, author)
						await played_card_message(self, e, author, send_channel, card)
		
					#########################
					## Termino de Votación ##
					#########################

					if not self.database[e]["waiting_for"] and self.database[e]["voting_sent"] == False:
						self.database[e]["voting_sent"] = True
						await vote_messages(self, e, emojis)
			
			###################
			## Judging Phase ##
			###################

				elif e in db and message in db[e]["reaction_id"] and db[e]["phase"] == "judging":
				
					if payload.emoji.name == "🚫":

						update_judge(self, e, message)

						channel_send = self.bot.get_channel(int(e))
						embed = discord.Embed(title="El juez ha dicho", description="Nadie ganó esta ronda. Ninguna respuesta fue de su agrado. ", color=0xd63e3e)
						await channel_send.send(embed=embed)

						self.database[e]["voters"] = []
						new_judge(self, e)

						if self.database[e]["turn"] <= self.database[e]["last_turn"]:

							await score_message(self, e)
							await reveal_message(self, e)					

						else:
							await victory_message(self, e)
							await score_message(self, e)
							endgame(self, e)


					elif payload.emoji.name in emojis:

						update_judge(self, e, message)

						print("Estos son los vovoovotantes" + str(self.database[e]["voters"]))
						await winner_message(self, e, payload, emojis)
						await post_image(self, e, payload, emojis)

						new_judge(self, e)

						if self.database[e]["turn"] <= self.database[e]["last_turn"]:

							await score_message(self, e)
							await reveal_message(self, e)					

						else:
							await victory_message(self, e)
							await score_message(self, e)
							endgame(self, e)

				else:
					print("Reaction detected but nothing happened")
					if e in db: print("e in db") 
					else: print("e not in db") 
					if message in db[e]["reaction_id"]: print("message in db reaction id")
					else: print("message not in reaction id")
					if payload.emoji.name in emojis: print("in emojis")
					else: print("wrong emoji")
					print("Phase: " + db[e]["phase"])


	#####################
	### Removing vote ###
	#####################

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		channel = str(payload.channel_id)
		author = str(payload.user_id)
		message = payload.message_id
		send_channel = self.bot.get_channel(int(payload.channel_id))
		author_tag = await self.bot.fetch_user(payload.user_id)
		msg_tag = await send_channel.fetch_message(int(message))
		emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣","5️⃣","6️⃣","7️⃣", "8️⃣"]

		################################
		### Removing Popularity Vote ###
		################################

		if channel in self.database and message in self.database[channel]["popularity_id"] and not author_tag.bot:

			index = emojis.index(payload.emoji.name)
			winner_str = self.database[channel]["voters"][index]
			if author == winner_str:
				pass
			else:
				self.database[channel]["players"][winner_str]["popularity"] -= 1

		################################
		### Removing Judge Vote ###
		################################

		if author in self.players:
			db = self.database
			for e in self.players[author]:
				if e in db and message in db[e]["reaction_id"] and payload.emoji.name in emojis and db[e]["phase"] == "playing":
					index = emojis.index(payload.emoji.name)
					card = self.database[e]["players"][author]["hand"][index]
					self.database[e]["players"][author]["choice"].remove(card)
					self.database[e]["players"][author]["remaining"] += 1


	@commands.group(invoke_without_command = True)
	async def cah(self,ctx):
		await ctx.send('Available Setup Commands: \nWelcome channel <#channel>\nwelcome text<message>')

	@cah.command()
	async def quick(self, ctx):
		emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣","5️⃣","6️⃣","7️⃣", "8️⃣"]
		db = self.database
		channel = str(ctx.channel.id)	

		# if not db:
		# 	self.bot.loop.create_task(time_police(self, channel))
		# 	print("Time Police on TIME!")

		self.players[str(ctx.author.id)] = [str(ctx.channel.id)]
		self.players[str(816038728069021698)] = [str(ctx.channel.id)]
		# Le super bots
		# self.players[str(265331722814619648)] = [str(ctx.channel.id)] #zaito
		# self.players[str(238824154990772225)] = [str(ctx.channel.id)] #capucha
		# self.players[str(701860854957735997)] = [str(ctx.channel.id)] #Eliza
		# self.players[str(606306056477343756)] = [str(ctx.channel.id)] #honey
		# self.players[str(736350604816941136)] = [str(ctx.channel.id)] #alice
		# Sopa de cebolla
		# self.players[str(670725624134107186)] = [str(ctx.channel.id)]
		# self.players[str(738079145430483035)] = [str(ctx.channel.id)]


		## Create new game ##

		if str(ctx.channel.id) not in db: 
			players_template = {"hand": [],"choice": [], "score": 0, "popularity": 0, "private_channel": None,"waiting_reaction": False,"remaining": 0}

			db[channel] =  cah_template(ctx.guild.id, ctx.author.id, self)
			db[channel]["last_active"] = time.time()
			db[channel]["players"][str(816038728069021698)] = copy.deepcopy(players_template)
			# Le super bots
			# db[channel]["players"][str(265331722814619648)] = copy.deepcopy(players_template) #zaito
			# db[channel]["players"][str(238824154990772225)] = copy.deepcopy(players_template) #capucha
			# db[channel]["players"][str(701860854957735997)] = copy.deepcopy(players_template) #eliza
			# db[channel]["players"][str(606306056477343756)] = copy.deepcopy(players_template) #honey
			# db[channel]["players"][str(736350604816941136)] = copy.deepcopy(players_template) #alice
			# Sopa de cebolla
			# db[channel]["players"][str(670725624134107186)] = players_template
			# db[channel]["players"][str(738079145430483035)] = players_template

			players_list = db[channel]["players"]
			key = random.choice(list(players_list))
			db[channel]["judge"] = key

			### Voters ###

			# for player in db[channel]["players"]:
			# 	if player != db[channel]["judge"]:
			# 		db[channel]["waiting_for"].append(player)

			# print("Waiting for al inicio" + str(db[channel]["waiting_for"]))
			await ctx.send("El juego ha iniciado")

			### Invitations ###
			#------------------------------------
			# self.database[channel]["invitations"] = False
			#------------------------------------

			for player in db[channel]["players"]:
				
				deal_cards(self.database, channel, player)
			
			# self.database[channel]["phase"] = "reveal"
			await reveal_message(self, channel)
			
		else:
			embed = discord.Embed(title=None, description="Ya se creó la partida")
			await ctx.send(embed=embed)	


	@cah.command(pass_context = True , aliases=['invitar'])
	async def invite(self, ctx, members: commands.Greedy[discord.Member]):

		forbidden = []
		accepted = []
		author = str(ctx.author.id)
		channel = str(ctx.channel.id)
		accept_embed = discord.Embed(title="Invitación 💌", description=("Ha recibido una invitación para jugar **Cartas contra la Humanidad**, reaccione a este mensaje para aceptar la invitación. \n\n**Servidor:** " + ctx.guild.name + "\n**Canal**: #" + ctx.channel.name), color=0xf5588c)

		
		if not ctx.guild:
			pass
		elif str(ctx.channel.id) in self.database:
			if author in self.database[channel]["admins"]:
				for member in members:
					if str(member.id) not in self.database[channel]["players"]:
						print("here")
						if member not in accepted:
							try:
								msg = await member.send(embed=accept_embed)	
								await msg.add_reaction("✅")
								accepted.append(member)

								self.database[channel]["dm_invitations"][str(msg.id)] = str(member.id)

							except Exception as e: 
								print(e)
								print("got here")
								forbidden.append(member)
				
				if accepted:
					accepted_msg = ""
					for member in accepted:
						nicky = await get_nickname(self, channel, member.id)
						accepted_msg += ("**"+ nicky + "**\n")
						if str(member.id) in self.players:
							self.players[str(member.id)].append(str(ctx.channel.id))
						else:  
							self.players[str(member.id)] = [str(ctx.channel.id)]


					accepted_embed = discord.Embed(title="Invitaciones enviadas", description=("Se ha enviado exitosamente una invitación a los siguientes usuarios: \n\n" + accepted_msg), color=0x28fc28)
					await ctx.send(embed=accepted_embed)

				if forbidden:
					
					forbid_msg = ""

					for member in forbidden:
						forbid_msg += (member.mention + "\n")

					forbid_embed = discord.Embed(title="Acceso denegado", description=("No se pudo enviar mensaje directo a algunos usuarios. Se requiere el permiso para que usuarios dentro del mismo servidor puedan enviarle mensajes. \n\n**Usuarios:\n**" + forbid_msg), color=0xff1717)
					await ctx.send(embed=forbid_embed)
			else:
				await no_permission(ctx.channel)
		else:
			embed = discord.Embed(title=None, description="No se ha creado ninguna partida en este canal. Para empezar una, usa el comando `cah crear`", color=0x549fd1)
			await ctx.send(embed=embed)

	@cah.command(pass_context = True , aliases=['invitaciones'])
	async def invitations(self, ctx, arg=None):

		channel = str(ctx.channel.id)
		author = str(ctx.author.id)

		if not ctx.guild:
			pass
		elif channel in self.database:
			if author in self.database[channel]["admins"]:
				if arg == "abiertas":
					embed = discord.Embed(title="Invitaciones Abiertas",description="Tome un dulce para unirse a la partida!",color=0xb53680)
					msg = await ctx.send(embed=embed)
					await msg.add_reaction("🍬")
					self.database[channel]["open_invitations"].append(msg.id)

				elif arg == "cerradas":
					
					embed = discord.Embed(title="Invitaciones Cerradas",description=None,color=0x521137)
					await ctx.send(embed=embed)
					for message in self.database[channel]["open_invitations"]:
						del_msg = await ctx.channel.fetch_message(message)
						await del_msg.delete()
					self.database[channel]["open_invitations"] = []
				else:
					embed2 = discord.Embed(title=None,description="**Argumentos invalidos** \n\n Este comando solo acepta dos opciones:\n\n`cah invitaciones abiertas` \n `cah invitaciones cerradas`",color=0x521137)
					await ctx.send(embed=embed2)
			else:
				await no_permission(ctx.channel)
		else:
			embed = discord.Embed(title=None, description="No se ha creado ninguna partida en este canal. Para empezar una, usa el comando `cah crear`", color=0x549fd1)
			await ctx.send(embed=embed)


	@cah.command(pass_context = True , aliases=['empezar', 'iniciar'])
	async def start(self, ctx):
	
		emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣","5️⃣","6️⃣","7️⃣", "8️⃣"]
		db = self.database
		channel = str(ctx.channel.id)
		author = str(ctx.author.id)

		if not ctx.guild:
			pass	
		elif channel in db: 
			
			if author in self.database[channel]["admins"]:
			
				if self.database[channel]["on_game"] == False:

					no_players = 0
					for player in self.database[channel]["players"]:
						no_players += 1

					if no_players > 1:

						update_rounds(self, channel)

						self.database[channel]["on_game"] = True
						players_list = db[channel]["players"]
						key = random.choice(list(players_list))
						db[channel]["judge"] = key

						for player in db[channel]["players"]:
							
							deal_cards(self.database, channel, player)
						
						# self.database[channel]["phase"] = "reveal"
						await reveal_message(self, channel)

					else:
						embed = discord.Embed(title=None, description="Se requieren mínimo 2 jugadores." ,color=0xd63e3e)
						await ctx.send(embed=embed)		


				else:
					embed = discord.Embed(title=None, description="Ya se ha iniciado la partida", color=0x32a883)
					msg = await ctx.send(embed=embed)
					await asyncio.sleep(3)
					await msg.delete()


				
			else:
				await no_permission(ctx.channel)		

		else:
			embed = discord.Embed(title=None, description="No se ha creado ninguna partida en este canal. Para empezar una, usa el comando `cah crear`", color=0x549fd1)
			await ctx.send(embed=embed)

				

	@cah.command(pass_context = True , aliases=['play','crear', 'preparar', 'jugar'])
	async def set(self, ctx):

		emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣","5️⃣","6️⃣","7️⃣", "8️⃣"]

		db = self.database
		channel = str(ctx.channel.id)
		
		if not ctx.guild:
			pass	
		elif str(ctx.channel.id) not in db: 

			embed=discord.Embed(title="Partida creada",description=("`cah iniciar` \n Se le dará comienzo al juego. \n\n`cah invitar [usuarios]` \n Se envíara invitaciones a los usuarios. \n\n `cah invitaciones [abiertas/cerradas]` \n Se enviara un mensaje con el que cualquiera podrá unirse / o se deshabilitaran aquellos mensajes  \n\n `cah terminar` \n Se cerrará la partida."), color=0x28fc28)

			try:
				embed3=discord.Embed(title="Mensaje de confirmación",description=("La partida se ha creado con éxito, las instrucciones se encuentran en el canal donde se abrió la partida."), color=0x28fc28)
				await ctx.author.send(embed=embed3)		
			except Exception: 
				embed2=discord.Embed(title="Acceso denegado",  description="No se pudo enviar mensaje directo. Permita que usuarios dentro del mismo servidor puedan enviarle mensajes.", color=0xff1717)
				await ctx.send(embed=embed2)	
				return

			await ctx.send(embed=embed)


			if str(ctx.author.id) in self.players:
				self.players[str(ctx.author.id)].append(str(ctx.channel.id))
			else:
				self.players[str(ctx.author.id)] = [str(ctx.channel.id)]

			db[channel] =  cah_template(ctx.guild.id, ctx.author.id, self)
	

		else:
			embed = discord.Embed(title=None, description="Ya se creó la partida")
			await ctx.send(embed=embed)	

	@cah.command(pass_context = True)
	async def admin(self, ctx, members: commands.Greedy[discord.Member] = None):
		channel = str(ctx.channel.id)
		author = str(ctx.author.id)

		if not ctx.guild:
			pass	
		elif str(ctx.channel.id) in self.database: 

			if author in self.database[channel]["admins"]:		

				added = []

				if not members:
					
					msg = ""
					title = ""

					if len(self.database[channel]["admins"]) > 1:
						title = "Admins"
					else:
						title = "Admin"

					for admin in self.database[channel]["admins"]:
						nicky = await get_nickname(self, channel, int(admin))
						msg += (nicky + "\n")

					embed = discord.Embed(title=title, description=msg, color=0xeb8467)
					await ctx.send(embed=embed)
				
				else:
					msg = ""
					title = ""
					
					for member in members:
						if str(member.id) not in self.database[channel]["admins"] and str(member.id) in self.database[channel]["players"]:
							msg += (member.mention + "\n")
							added.append(str(member.id))
							if str(member.id) not in self.database[channel]["admins"]:
								self.database[channel]["admins"].append(str(member.id))

					if len(added) != 0:			
						if len(added) > 1:
							title = "Admins añadidos"
						else:
							title = "Admin añadido"

						embed = discord.Embed(title=title, description=msg, color=0xeb8467)
						await ctx.send(embed=embed)
					else:
						embed = discord.Embed(title=None, description="No se pudo otorgar permisos. Puede ser porque los usuarios no están en el juego o ya son administradores.", color=0xd63e3e)
						await ctx.send(embed=embed)

			else:
				await no_permission(ctx.channel)	
		else:
			embed = discord.Embed(title=None, description="No se ha creado ninguna partida en este canal. Para empezar una, usa el comando `cah crear`", color=0x549fd1)
			await ctx.send(embed=embed)


	@cah.command(pass_context = True)
	async def unadmin(self, ctx, members: commands.Greedy[discord.Member] = None):

		author = str(ctx.author.id)		
		channel = str(ctx.channel.id)

		if not ctx.guild:
			pass	
		elif str(ctx.channel.id) in self.database: 

			if author in self.database[channel]["admins"]:			
				if not members:

					embed = discord.Embed(title=None, description="Este comando requiere de menciones `cah unadmin [usuario/usuarios]`", color=0xeb8467)
					await ctx.send(embed=embed)
				
				else:

					if len(self.database[channel]["admins"]) > 1:

						msg = ""

						for member in members:
							
							
							if str(member.id) in self.database[channel]["admins"]:
								nicky = await get_nickname(self, channel, member.id)
								msg += (nicky + "\n")
								self.database[channel]["admins"].remove(str(member.id))

						if msg != "":
							embed = discord.Embed(title="Se han quitado los permisos a:", description=msg, color=0xd63e3e)
							await ctx.send(embed=embed)
					else:
						embed = discord.Embed(title=None, description="Se requieren más de una personas con permisos de administrador para usar este comando", color=0xd63e3e)
						await ctx.send(embed=embed)

			else:
				await no_permission(ctx.channel)				
		else:
			embed = discord.Embed(title=None, description="No se ha creado ninguna partida en este canal. Para empezar una, usa el comando `cah crear`", color=0x549fd1)
			await ctx.send(embed=embed)					


	@cah.command(pass_context = True, aliases=['saltar','siguiente','next'])
	async def skip(self, ctx, arg=None):
		channel = str(ctx.channel.id)
		author = str(ctx.author.id)

		if not ctx.guild:
			pass	
		elif str(ctx.channel.id) in self.database: 

			if author in self.database[channel]["admins"]:			
				

				if self.database[channel]['phase'] == 'playing':

					theres_choice = False

					while not theres_choice:
						for player in self.database[channel]["players"]:
							if self.database[channel]["players"][player]["choice"]:
								print("Choices: " + str(self.database[channel]["players"][player]["choice"]))
								theres_choice = True
						break
							
						### Esto se puede simplificar en una funcion para reutilizar multiples veces
						
					if theres_choice:

						emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣","5️⃣","6️⃣","7️⃣", "8️⃣"]
						self.database[channel]["waiting_for"] = []

						await vote_messages(self, channel, emojis)


					else:
						everyone_send = self.bot.get_channel(int(channel))
						await everyone_send.send("Nadie jugó!")
						self.database[channel]["reaction_id"] = []
						self.database[channel]["phase"] = "reveal"
						self.database[channel]["waiting_for"] = []
						self.database[channel]["turn_time"] = []
						self.database[channel]["voters"] = []
						for player in self.database[channel]["players"]:
							self.database[channel]["players"][player]["choice"] = []
						

						new_judge(self, channel)

						if self.database[channel]["turn"] <= self.database[channel]["last_turn"]:

							await reveal_message(self, channel)	
							self.database[channel]['phase'] = "reveal"				

						else:
							await victory_message(self, channel)
							await score_message(self, channel)
							endgame(self, channel)


					print(self.database[channel]['phase'])

				elif self.database[channel]['phase'] == 'judging':
					print("Fase cuando skipeas judging: "+ self.database[channel]['phase'])
					self.database[channel]["reaction_id"] = []
					self.database[channel]["phase"] = "reveal"
					self.database[channel]["waiting_for"] = []
					self.database[channel]["turn_time"] = []
					self.database[channel]["voters"] = []

					update_judge(self, channel, "filler")

					new_judge(self, channel)

					if self.database[channel]["turn"] <= self.database[channel]["last_turn"]:

						await score_message(self, channel)
						await reveal_message(self, channel)	
						# self.database[channel]['phase'] = "reveal"					

					else:
						await victory_message(self, channel)
						await score_message(self, channel)
						endgame(self, channel)



				elif self.database[channel]['phase'] == 'reveal':

					self.database[channel]["reaction_id"] = []
					self.database[channel]["phase"] = "reveal"
					self.database[channel]["waiting_for"] = []
					self.database[channel]["turn_time"] = []
					self.database[channel]["voters"] = []

					update_judge(self, channel, "filler")

					
					new_judge(self, channel)

					if self.database[channel]["turn"] <= self.database[channel]["last_turn"]:
						await score_message(self, channel)
						await reveal_message(self, channel)	
						# self.database[channel]['phase'] = "reveal"					

					else:
						await victory_message(self, channel)
						await score_message(self, channel)
						endgame(self, channel)

					print(self.database[channel]['phase'])

			else:
				await no_permission(ctx.channel)				
		else:
			embed = discord.Embed(title=None, description="No se ha creado ninguna partida en este canal. Para empezar una, usa el comando `cah crear`", color=0x549fd1)
			await ctx.send(embed=embed)		



	@cah.command(pass_context = True, aliases=['rondas', 'ronda','round'])
	async def rounds(self, ctx, arg=None):

		author = str(ctx.author.id)		
		channel = str(ctx.channel.id)

		if not ctx.guild:
			pass	
		elif str(ctx.channel.id) in self.database: 

			if author in self.database[channel]["admins"]:			
				
				if arg == None:
					round_number = self.database[channel]["rounds"]
					msg = ""

					if round_number == None:
						msg = "Default"
					else:
						msg = str(round_number)

					embed = discord.Embed(title=None, description=("**Rondas:** " + msg), color= 0x32a883)
					await ctx.send(embed=embed)

				else:
					if RepresentsInt(arg):
						self.database[channel]["rounds"] = arg
						embed = discord.Embed(title=None, description=("**Rondas del juego:** " + arg), color= 0x32a883)
						await ctx.send(embed=embed)
					elif arg.lower() == "default":
						self.database[channel]["rounds"] = None
						embed = discord.Embed(title=None, description=("**Rondas del juego:** Default"), color= 0x32a883)
						await ctx.send(embed=embed)
					else:
						embed2 = discord.Embed(title=None,description="**Argumentos invalidos** \n\n Este comando solo acepta dos opciones:\n\n`cah rondas default` \n `cah rondas [número]`",color=0x521137)
						await ctx.send(embed=embed2)	

			else:
				await no_permission(ctx.channel)				
		else:
			embed = discord.Embed(title=None, description="No se ha creado ninguna partida en este canal. Para empezar una, usa el comando `cah crear`", color=0x549fd1)
			await ctx.send(embed=embed)		



	@cah.command(pass_context = True , aliases=['salir', 'abandonar','salirse'])
	async def leave(self, ctx,  members: commands.Greedy[discord.Member] = None):
		author = str(ctx.author.id)		
		channel = str(ctx.channel.id)

		if not ctx.guild:
			pass	
		elif str(ctx.channel.id) in self.database: 
			tag = str(ctx.author.id)
			nicky = await get_nickname(self, channel, tag)

			if tag in self.database[channel]["players"]:
				
				if len(self.database[channel]["admins"]) > 1 and tag in self.database[channel]["admins"]:
					self.database[channel]["admins"].remove(tag)
				elif len(self.database[channel]["admins"]) == 1 and tag in self.database[channel]["admins"]:
					embed = discord.Embed(title=None, description="No puedes abandonar la partida debido a que eres el único administrador. \n\nPuedes hacer lo siguiente:\n-Dar permisos a otra persona `cah admin [usuarios]`\n-Terminar la partida `cah terminar`")
					await ctx.send(embed=embed)
					return

				if tag in self.database[channel]["voters"]:
					self.database[channel]["voters"].remove(tag)

				if tag in self.database[channel]["waiting_for"]:
					self.database[channel]["waiting_for"].remove(tag)

				self.database[channel]["p_number"] -= 1
				self.database[channel]["players"].pop(tag)


				if len(self.database[channel]["players"]) <= 1 and self.database[channel]["on_game"] == True:

					embed2 = discord.Embed(title=None, 
										description=(nicky + " ha sido expulsado"), 
										color=0xF0FFFF)

					await ctx.send(embed=embed2)

					delete_this = []
					self.database.pop(str(ctx.channel.id))
					for player in self.players:
						if str(ctx.channel.id) in self.players[player]:
							self.players[player].remove(str(ctx.channel.id))
						if not self.players[player]:
							delete_this.append(player)
					if delete_this:
						for e in delete_this:
							self.players.pop(e)

					embed = discord.Embed(title=None, description="Se ha eliminado la partida debido a falta de jugadores.", color=0x000)
					await ctx.send(embed=embed)

				elif self.database[channel]["judge"] == tag:
					
					embed = discord.Embed(title=None, 
										description="El juez ha dejado la partida, la ronda comenzará de nuevo.", 
										color=0xd63e3e)

					await ctx.send(embed=embed)
					
					self.database[channel]["reaction_id"] = []
					self.database[channel]["phase"] = "reveal"
					self.database[channel]["waiting_for"] = []
					self.database[channel]["turn_time"] = []
					for player in self.database[channel]["players"]:
						self.database[channel]["players"][player]["choice"] = []
					
					

					new_judge(self, channel)

					await reveal_message(self, channel)
					self.database[channel]["turn"] -= 1	

				else:
					self.database[channel]["players"].pop(tag)		
					embed = discord.Embed(title=None, 
										description=(nicky + " dejó la partida."), 
										color=0xF0FFFF)

					await ctx.send(embed=embed)
		
				

			else:
				embed = discord.Embed(title=None,description="Lo sentimos pero no estás en la sala.")
				await ctx.author.send(embed=embed)

		else:
			embed = discord.Embed(title=None, description="No se ha creado ninguna partida en este canal. Para empezar una, usa el comando `cah crear`", color=0x549fd1)
			await ctx.send(embed=embed)		

	@cah.command(pass_context = True , aliases=['patear', 'expulsar'])
	async def kick(self, ctx,  members: commands.Greedy[discord.Member] = None):
		author = str(ctx.author.id)		
		channel = str(ctx.channel.id)

		if not ctx.guild:
			pass	
		elif str(ctx.channel.id) in self.database: 

			if author in self.database[channel]["admins"]:

				if members == None:
					embed = discord.Embed(title=None, description="Este comando requiere a los usuarios que desee expulsar.", color=0xd63e3e)
				else:
					for member in members:
						tag = str(member.id)
						nicky = await get_nickname(self, channel, member.id)

						if tag in self.database[channel]["players"]:
						

							if len(self.database[channel]["admins"]) > 1 and tag in self.database[channel]["admins"]:
								self.database[channel]["admins"].remove(tag)
							elif len(self.database[channel]["admins"]) == 1 and tag in self.database[channel]["admins"]:
								embed = discord.Embed(title=None, description="No puedes abandonar la partida debido a que eres el único administrador. \n\nPuedes hacer lo siguiente:\n-Dar permisos a otra persona `cah admin [usuarios]`\n-Terminar la partida `cah terminar`")
								await ctx.send(embed=embed)
								continue

							if tag in self.database[channel]["voters"]:
								self.database[channel]["voters"].remove(tag)

							if tag in self.database[channel]["waiting_for"]:
								self.database[channel]["waiting_for"].remove(tag)

							self.database[channel]["p_number"] -= 1

							if len(self.database[channel]["players"]) == 2 and self.database[channel]["on_game"] == True:

								embed2 = discord.Embed(title=None, 
													description=(nicky + " ha sido expulsado"), 
													color=0xF0FFFF)

								await ctx.send(embed=embed2)

								delete_this = []
								self.database.pop(str(ctx.channel.id))
								for player in self.players:
									if str(ctx.channel.id) in self.players[player]:
										self.players[player].remove(str(ctx.channel.id))
									if not self.players[player]:
										delete_this.append(player)
								if delete_this:
									for e in delete_this:
										self.players.pop(e)

								embed = discord.Embed(title=None, description="Se ha eliminado la partida debido a falta de jugadores.", color=0x000)
								await ctx.channel.send(embed=embed)

							if self.database[channel]["judge"] == tag:
								
								embed = discord.Embed(title=None, 
													description="El juez ha dejado la partida, la ronda comenzará de nuevo.", 
													color=0xd63e3e)

								await ctx.send(embed=embed)
								
								self.database[channel]["reaction_id"] = []
								self.database[channel]["phase"] = "reveal"
								self.database[channel]["waiting_for"] = []
								self.database[channel]["turn_time"] = []
								for player in self.database[channel]["players"]:
									self.database[channel]["players"][player]["choice"] = []
								
								

								new_judge(self, channel)
								self.database[channel]["players"].pop(tag)

								self.database[channel]["turn"] -= 1	
								await reveal_message(self, channel)


							else:
								self.database[channel]["players"].pop(tag)		
								embed = discord.Embed(title=None, 
													description=(nicky + " ha sido expulsado"), 
													color=0xF0FFFF)

								await ctx.send(embed=embed)
					
						# if len(self.database[channel]["players"]) <= 1 and self.database[channel]["on_game"] == True:

						# 	delete_this = []
						# 	self.database.pop(str(ctx.channel.id))
						# 	for player in self.players:
						# 		if str(ctx.channel.id) in self.players[player]:
						# 			self.players[player].remove(str(ctx.channel.id))
						# 		if not self.players[player]:
						# 			delete_this.append(player)
						# 	if delete_this:
						# 		for e in delete_this:
						# 			self.players.pop(e)

						# 	embed = discord.Embed(title=None, description="Se ha eliminado la partida debido a falta de jugadores.", color=0x000)
						# 	await ctx.channel.send(embed=embed)




			else:
				await no_permission(ctx.channel)				
		else:
			embed = discord.Embed(title=None, description="No se ha creado ninguna partida en este canal. Para empezar una, usa el comando `cah crear`", color=0x549fd1)
			await ctx.send(embed=embed)		


	@cah.command(pass_context = True , aliases=['terminar', 'finish'])
	async def end(self, ctx):
		delete_this = []
		author = str(ctx.author.id)		
		channel = str(ctx.channel.id)

		if not ctx.guild:
			pass	
		elif channel in self.database: 

			if author in self.database[channel]["admins"]:

				self.database.pop(str(ctx.channel.id))
				for player in self.players:
					if str(ctx.channel.id) in self.players[player]:
						self.players[player].remove(str(ctx.channel.id))
					if not self.players[player]:
						delete_this.append(player)
				if delete_this:
					for e in delete_this:
						self.players.pop(e)

				embed = discord.Embed(title=None, description="Se ha eliminado la partida.", color=0x000)
				await ctx.channel.send(embed=embed)

			else:
				await no_permission(ctx.channel)				
		else:
			embed = discord.Embed(title=None, description="No se ha creado ninguna partida en este canal. Para empezar una, usa el comando `cah crear`", color=0x549fd1)
			await ctx.send(embed=embed)			

async def time_police(self, channel):

	if self.database:
		print("Theres database")
	while self.database:        
		await asyncio.sleep(10)
		now = time.time()

		################
		### Turn End ###
		################


		if  self.database[channel]["turn_time"] and self.database[channel]["phase"] == "playing":
			print("Theres turn time")
			result = now - self.database[channel]["turn_time"][0]
			round_time = len(self.database[channel]["players"]) * 15 #+ 10
			theres_choice = False

			if result > round_time:
				
				while not theres_choice:
					for player in self.database[channel]["players"]:
						if self.database[channel]["players"][player]["choice"]:
							print("Choices: " + str(self.database[channel]["players"][player]["choice"]))
							theres_choice = True
					break
					
				### Esto se puede simplificar en una funcion para reutilizar multiples veces
				
				if theres_choice:

					emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣","5️⃣","6️⃣","7️⃣", "8️⃣"]
					print("running theres choice code")
					self.database[channel]["waiting_for"] = []

					vote_messages(self, channel, emojis)


				else:
					everyone_send = self.bot.get_channel(int(channel))
					
					embed = discord.Embed(title=None,description="Se acabó el tiempo!", color=0xd63e3e)
					await everyone_send.send(embed=embed)
					self.database[channel]["reaction_id"] = []
					self.database[channel]["phase"] = "reveal"
					self.database[channel]["waiting_for"] = []
					self.database[channel]["turn_time"] = []
					for player in self.database[channel]["players"]:
						self.database[channel]["players"][player]["choice"] = []
					

					new_judge(self, channel)

					if self.database[channel]["turn"] <= self.database[channel]["last_turn"]:

						await reveal_message(self, channel)					

					else:
						await victory_message(self, channel)
						endgame(self, channel)

		###########################
		### Popularity timeouts ###
		###########################

		for game in self.database:
			if self.database[game]["popularity_time"]:
				for timestamp in self.database[game]["popularity_time"]:
					result = now - timestamp
					if result > 15:
						pop_index = self.database[channel]["popularity_time"].index(timestamp)
						del self.database[channel]["popularity_id"][pop_index]
						self.database[channel]["popularity_time"].remove(timestamp)


		#####################
		### Inactive game ###
		#####################

		inactive_result = now - self.database[channel]["last_active"]
		print("inactive_result: " + str(inactive_result))
		if inactive_result > 120:
			reveal_send = self.bot.get_channel(int(channel))
			for key in self.database:
				print("This is key: " + key)

			await reveal_send.send("El juego termino por inactividad.")
			for player in self.database[channel]["players"]:
				self.players[player].remove(channel)
				if not self.players[player]:
					self.players.pop(player)

			self.database.pop(channel)

		print("Time police working")

	print("The time police has finished it's job")


def update_rounds(self, channel):
	num_players = 0
	for player in self.database[channel]["players"]:
		num_players += 1

	print(num_players)
	print(self.database[channel]["rounds"])
	last_turn = self.database[channel]["last_turn"]

	if self.database[channel]["rounds"] == None:
		print("aca")
		if num_players == 2: 
			last_turn = 6
		elif num_players == 3: 
			last_turn = 6
		elif num_players == 4: 
			last_turn = 8
		elif num_players == 5:
			last_turn = 5
		elif num_players == 6: 
			last_turn = 6
		elif num_players == 7: 
			last_turn = 7
		elif num_players == 8: 
			last_turn = 8
	else:
		print("alla")
		last_turn = int(num_players) * int(self.database[channel]["rounds"])

	self.database[channel]["last_turn"] = last_turn
	print("Last turn is: " + str(self.database[channel]["last_turn"]))
	print("Current turn is: " + str(self.database[channel]["turn"]))


############################
### INVITATION FUNCTIONS ###
############################

async def full_house(self, channel):
	channel_tag = self.bot.get_channel(int(channel))


	if self.database[channel]["dm_invitations"]:
		for invited in self.database[channel]["dm_invitations"]:
			tag = self.database[channel]["dm_invitations"][invited]
			member = await self.bot.fetch_user(int(tag))
			message_tag = await member.fetch_message(int(invited))
			await message_tag.delete()
			embed = discord.Embed(title=None, description="La invitación para jugar 'Cartas contra la humanidad' ha expirado", color=0xad1c32)
			await member.send(embed=embed)
			
		self.database[channel]["dm_invitations"] = []


	if self.database[channel]["open_invitations"]:
		channel_send = self.bot.get_channel(int(channel))
		embed = discord.Embed(title="Invitaciones Cerradas",description=None,color=0x521137)
		await channel_send.send(embed=embed)
		for message in self.database[channel]["open_invitations"]:
			del_msg = await channel_tag.fetch_message(message)
			await del_msg.delete()
		self.database[channel]["open_invitations"] = []


########################
### REVEAL FUNCTIONS ###
########################

def update_reveal(self, channel):
	self.database[channel]["reveal_id"] = []
	self.database[channel]["turn_time"].append(time.time())
	self.database[channel]["last_active"] = time.time()


async def reveal_question(self, channel, card, send_channel):





	self.database[channel]["question"] = str(card)
	question_msg = str(self.questions[str(card)][0]).replace("_", "\\_\\_\\_\\_\\_\\_\\_\\_")
	
	embed = discord.Embed(title="Pregunta", description=("▫️" + question_msg), color=0x000)
	embed.set_footer(text="Se ha enviado un mensaje a los jugadores para que determinen sus respuestas.")
	await send_channel.send(embed=embed)

	self.database[channel]["fields"] = self.questions[str(card)][1]



async def play_card_msg(self, channel, player, emojis, card):
	self.database[channel]["players"][player]["remaining"] = self.questions[str(card)][1]

	question_id =  self.database[channel]["question"]
	question = self.questions[question_id][0]
	question_no = self.questions[question_id][1]
	choose_cards = ""
	if question_no > 1:
		choose_cards = "¡Escoge tus cartas!"
	else:
		choose_cards = "¡Escoge tu carta!"
	question = question.replace("_", "\\_\\_\\_\\_\\_\\_")
	your_cards = ""
	your_cards_index = 0 

	for card in self.database[channel]["players"][player]["hand"]:
		your_cards += (emojis[your_cards_index] + " - " + self.answers[str(card)] + "\n")
		your_cards_index += 1

	user_sent = await self.bot.fetch_user(int(player)) 


	embed=discord.Embed(title=choose_cards,  description=None, color=0x000)

	embed.add_field(name="La \"pregunta\":", value=(question), inline=False) 
	embed.add_field(name="Cartas requeridas:", value=(question_no), inline=False) 
	embed.add_field(name="Tus cartas:", value=(your_cards), inline=False) 
	
	msg = await user_sent.send(embed=embed)
	
	for emoji in emojis:
		await msg.add_reaction(emoji)

	self.database[channel]["reaction_id"].append(msg.id)





######################
### PLAY FUNCTIONS ###
######################

def update_playing(self, channel, author, card):
	self.database[channel]["players"][author]["choice"].append(card)
	self.database[channel]["players"][author]["remaining"] -= 1
	self.database[channel]["last_active"] = time.time()

def choice_made(self, channel, message, author):
	print("Voters: "+str(self.database[channel]["voters"]))
	print("Waiting for:"+str(self.database[channel]["waiting_for"]))
	print("Reaction: "+str(self.database[channel]["reaction_id"]))	
	self.database[channel]["reaction_id"].remove(message)
	self.database[channel]["waiting_for"].remove(author)
	self.database[channel]["voters"].append(author)	
	print("Voters: "+str(self.database[channel]["voters"]))
	print("Waiting for:"+str(self.database[channel]["waiting_for"]))
	print("Reaction: "+str(self.database[channel]["reaction_id"]))

async def played_card_message(self, channel, author, send_channel, card):
	cards = self.database[channel]["players"][author]["choice"]
	player_tag = await self.bot.fetch_user(author)
	server_channel = self.bot.get_channel(int(channel))

	embed2=discord.Embed(title="Tu respuesta",  description=(), color=0xF0FFFF)

	if len(self.database[channel]["players"][author]["choice"]) == 1:
		
		embed1=discord.Embed(title=None,  description=(self.answers[str(cards[0])]), color=0xF0FFFF)
		embed1.set_footer(text="Tu respuesta")
		embed2=discord.Embed(title=None,  description=(str(self.answers[str(cards[0])]) + "\n\n"+ player_tag.mention), color=0xF0FFFF)
		
		await send_channel.send(embed=embed1)
		await server_channel.send(embed=embed2)

		self.database[channel] = play_card(self.database[channel], card, author)
		
		
	
	else:
		jugaste_msg = ""
		

		for choice in cards:
			jugaste_msg += ("▫️  " + self.answers[str(choice)] + "\n")	
			self.database[channel] = play_card(self.database[channel], choice, author)
		
		embed1=discord.Embed(title=None,  description=jugaste_msg, color=0xF0FFFF)
		embed1.set_footer(text="Tu respuesta")
		embed2=discord.Embed(title=None,  description=(jugaste_msg + "\n"+ player_tag.mention), color=0xF0FFFF)


		await send_channel.send(embed=embed1)
		await server_channel.send(embed=embed2)


def play_card(db, card, author):
	if not db["deck"]:
		db["deck"] = db["discarded"]
		db["discarded"] = []
	db["players"][author]["hand"].remove(card)
	db["discarded"].append(card)
	lenght = len(db["deck"])
	new_card = db["deck"][randint(0, lenght-1)]
	db["deck"].remove(new_card)
	db["players"][author]["hand"].append(new_card)

	result = db
	return result

async def vote_messages(self, channel, emojis):

	self.database[channel]["turn_time"] = []
	judge_send = await self.bot.fetch_user(int(self.database[channel]["judge"]))
	popularity_send = self.bot.get_channel(int(channel))

	player_index = 1
	emoji_index = 0
	player_choices = 0
	judge_msg = ""

	question_id =  self.database[channel]["question"]
	question = self.questions[question_id][0]
	question = question.replace("_", "\\_\\_\\_\\_\\_\\_\\_\\_")
	
	embed1 = discord.Embed(title="¡Voto Público!",  description=None, color=0xffdc5c)
	embed1.add_field(name="Pregunta", value=(question), inline=False)

	embed2 = discord.Embed(title="¡Voto del Juez!",  description=None, color=0xffdc5c)
	embed2.add_field(name="Pregunta", value=(question), inline=False)
	
	if self.database[channel]["fields"] < 2:
		print("solamente 1 carta")
		for player in self.database[channel]["voters"]:
			if player != self.database[channel]["judge"]:
				judge_msg += (emojis[emoji_index] + " - " + self.answers[str(self.database[channel]["players"][player]["choice"][0])] + "\n")
				player_choices += 1 
				player_index += 1
				emoji_index += 1

	
	else:
		print("mas de una carta")
		for player in self.database[channel]["voters"]:
			if player != self.database[channel]["judge"]:
				judge_msg += (emojis[emoji_index]  + "\n")
				i = 0
				while i < self.database[channel]["fields"]:
					judge_msg += ("▫️  " + self.answers[str(self.database[channel]["players"][player]["choice"][i])] + "\n")
					i += 1
				player_choices += 1 
				player_index += 1
				emoji_index += 1
			
	embed1.add_field(name="Respuestas", value=(judge_msg), inline=False)
	embed2.add_field(name="Respuestas", value=(judge_msg), inline=False)
	embed1.set_footer(text="Se ha enviado un mensaje al juez para su voto. Estos votos son aparte y se iran acumulandose a lo largo del juego.")
	
	judge_reaction = await judge_send.send(embed=embed2)
	popularity_reaction = await popularity_send.send(embed=embed1)


	### Adding reactions and preparing variables for next phase

	for i in range(0, player_choices):
		await judge_reaction.add_reaction(emojis[i])
		await popularity_reaction.add_reaction(emojis[i])

	await judge_reaction.add_reaction("🚫")

	self.database[channel]["popularity_id"].append(popularity_reaction.id)
	self.database[channel]["popularity_time"].append(time.time())
	self.database[channel]["reaction_id"].append(judge_reaction.id)
	print("This is reaction id: "+ str(self.database[channel]["reaction_id"]))
	self.database[channel]["phase"] = "judging"


#########################
### Judging Functions ###
#########################

def update_judge(self, channel, message):
	if message == "filler":
		self.database[channel]["reaction_id"] = []
	else:	
		self.database[channel]["reaction_id"].remove(message)
	self.database[channel]["phase"] = "reveal"
	self.database[channel]["last_active"] = time.time()
	self.database[channel]["voting_sent"] = False

async def winner_message(self, channel, payload, emojis):
	
	winner_channel = self.bot.get_channel(int(channel))
	index = emojis.index(payload.emoji.name)
	winner_str = self.database[channel]["voters"][index]
	print("este es el index: " + str(index))
	print("de nuevo los bonovotantes: " + str(self.database[channel]["voters"]))
	
	winner = await self.bot.fetch_user(int(winner_str))
	question_id =  self.database[channel]["question"]
	question = self.questions[question_id][0]
	fields = self.database[channel]["fields"]
	final_phrase = ""
	final_phrase += question

	if "_" in question:
		print("si tiene _")
		for i in range(0, fields):
			da_choice = self.database[channel]["players"][winner_str]["choice"][i]
			replace = self.answers[str(da_choice)][:-1]
			print("This is the prompt: " + str(replace))
			final_phrase = final_phrase.replace("_", ("**"+ str(replace) + "**"), 1)

	else:
		print("NO tiene _")
		final_phrase += " "
		for i in range(0, fields):
			da_choice = self.database[channel]["players"][winner_str]["choice"][i]
			to_add = self.answers[str(da_choice)][:-1]
			print("This is the prompt: " + str(to_add))
			final_phrase += ("**" + to_add + "**")
			
	embed=discord.Embed(title="Frase Ganadora",  description=(final_phrase + "\n\n" + winner.mention), color=0xffdc5c)

	await winner_channel.send("🎉")
	await winner_channel.send(embed=embed)
	# await asyncio.sleep(3)


async def score_message(self, channel):
	
	score_channel_send = self.bot.get_channel(int(channel))
	player_table = ""
	score_table = ""
	popularity_table = ""

	for player in self.database[channel]["players"]:
		guild = self.bot.get_guild(self.database[channel]["guild"])
		self.database[channel]["players"][player]["choice"] = []
		member = guild.get_member(int(player))
		print_member = None
		if member:
			if member.nick:
				print_member = member.nick
			else:
				print_member = member.name
		else:
			result = await guild.query_members(limit=1, user_ids=[player])
			member = result[0]
			if member.nick:
				print_member = member.nick
			else:
				print_member = member.name

		player_table += (print_member + "\n")
		score_table +=  (str(self.database[channel]["players"][player]["score"]) + "\n")
		popularity_table += (str(self.database[channel]["players"][player]["popularity"]) + "\n")

		# score_count += ("**" + str(print_member)  + "**- Puntaje: " + 
		# 	str(self.database[channel]["players"][player]["score"]) + " Popularidad: " +
		# 	str(self.database[channel]["players"][player]["popularity"]) + "\n")
	
	embed=discord.Embed(title="Puntaje",  description=None, color=0x32a883)
	embed.add_field(name="Jugadores", value=player_table, inline=True) 
	embed.add_field(name="Puntos", value=score_table, inline=True) 
	embed.add_field(name="Popularidad", value=popularity_table, inline=True) 

	await score_channel_send.send(embed=embed)


async def reveal_message(self, channel):

	send_channel = self.bot.get_channel(int(channel))
	judge = await self.bot.fetch_user(self.database[channel]["judge"])
	turn_msg = ""

	if self.database[channel]["turn"] == 1:
		turn_msg = "**Primer Turno**"

	elif self.database[channel]["turn"] < self.database[channel]["last_turn"]:
		turn_msg = ("Turno número: **" + str(self.database[channel]["turn"]) + "**")

	elif self.database[channel]["turn"] == self.database[channel]["last_turn"]:
		turn_msg = "**ULTIMO TURNO**"
	
	self.database[channel]["turn"] += 1

	### Embed
	embed=discord.Embed(title=turn_msg,  
		description=None, 
		color=0x000)
	embed.add_field(name="El juez es:", value=(judge.mention + "\n\n ⚖️  **Reacciona para revelar la \"pregunta\".**"), inline=False) 


	msg = await send_channel.send(embed=embed)
	
	self.database[channel]["reveal_id"].append(msg.id)
	print(self.database[channel]["reveal_id"])
	await msg.add_reaction("✅")

	for player in self.database[channel]["players"]:
		if player != self.database[channel]["judge"]:		
			self.database[channel]["waiting_for"].append(player)

	self.database[channel]['phase'] = "reveal"


async def victory_message(self, channel):
	

	send_channel = self.bot.get_channel(int(channel))
	winner = None
	famous = []

	for player in self.database[channel]["players"]:
		if winner == None:
			winner = player
		elif self.database[channel]["players"][player]["score"] > self.database[channel]["players"][winner]["score"]:
			winner = player
		elif  self.database[channel]["players"][player]["score"] == self.database[channel]["players"][winner]["score"]:
			if self.database[channel]["players"][player]["popularity"] == self.database[channel]["players"][winner]["popularity"]:
				winner = player


		print("This is the player for famouse: " + player)
		if not famous:
			print("Not famous")
			if self.database[channel]["players"][player]["popularity"] > 0:
				print("se anadio a " + player + " por tener mas de 0")
				famous = [player]
		elif self.database[channel]["players"][player]["popularity"] > self.database[channel]["players"][famous[0]]["score"]:
			print("Se remplazo famous con " + player)
			famous = [player]
		elif self.database[channel]["players"][player]["popularity"] == self.database[channel]["players"][famous[0]]["popularity"]:
			print("se anadio a " + player)
			famous.append(player)
		else:
			print("No se anadio a " + player)

	popularity_msg = ""
	popularity_title = "El jugador más popular:"
	popular_count = 0

	for player in famous:
		popular_tag = await self.bot.fetch_user(int(player))
		popularity_msg += (popular_tag.mention + "\n")
		popular_count += 1

	if popular_count > 1:
		popularity_title = "Los jugadores más populares:"

	winner_tag = await self.bot.fetch_user(int(winner))


	embed = discord.Embed(title="El ganador del juego es:",  description=winner_tag.mention, color=0xffdc5c)
	if famous:
		print("arrived here")
		embed.add_field(name=(popularity_title), value=(popularity_msg), inline=False) 

	msg = await send_channel.send("🥁")
	await asyncio.sleep(4)
	await msg.delete()
	await send_channel.send("👑")
	await send_channel.send(embed=embed)
	# await asyncio.sleep(4)


def endgame(self, channel):
	for player in self.database[channel]["players"]:
		self.players[player].remove(channel)
		if not self.players[player]:
			self.players.pop(player)
	self.database.pop(channel)

def get_cah():
	with open("cah/cah_data.json") as f:
		data = f
	return data


def load_cah():
	with open("cah/cah_data.json") as f:
		data = json.load(f)

	return data

def discard_question(database, channel, card):

	if not database[channel]["questions"]:
		database[channel]["questions"] = db["discarded_questions"]
		database[channel]["discarded_questions"] = []
	database[channel]["questions"].remove(card)
	database[channel]["discarded_questions"].append(card)


def deal_cards(data, channel, players):


	
	
	jug = players
	changes = data

	print(jug)
	changes[str(channel)]["players"][jug]["hand"] = []

	i = 1
	while i <= 8:
		lenght = len(data[channel]["deck"])
		card = None
		card = changes[channel]["deck"][randint(0, lenght-1)]
		changes[str(channel)]["deck"].remove(card)
		changes[str(channel)]["players"][jug]["hand"].append(card)

		print("mano: " + str(changes[str(channel)]["players"][jug]["hand"]))

		i += 1


def new_judge(self, channel):

	now_playing = []
	for player in self.database[channel]["players"]:
		now_playing.append(player)
	
	index = now_playing.index(self.database[channel]["judge"])
	lenght = len(now_playing) - 1
	
	if index >= lenght:
		index = 0
	else:
		index += 1
	
	self.database[channel]["judge"] = now_playing[index]

def more_random(max_num):
	final_digits = []
	index = 0
	lenght = len(str(max_num))

	for numstr in str(max_num):
		
		num = int(numstr)
		top = 9
		digit = 0

		if index == 0:

			top = num
			pool = [randint(0, top),randint(0, top),randint(0, top)]
			digit = pool[randint(0,2)]

			if digit == num:
				print("fue 4")
				if index + 1 == lenght:
					print("fue 4 y solo hay un numero")
					final_digits.append(digit)
				else:

					other = randint(0,9)
					print("Limit: " + str(max_num)[index+1] )
					print("Other: " + str(other))

					if other > int(str(max_num)[index+1]) + 2: #digit:
						print("other fue mas alto que el siguiente numero")
						digit = randint(0, digit-1)

						final_digits.append(digit)
					else:
						print("other fallo")
						final_digits.append(digit)
			else:
				final_digits.append(digit)
		else:
			
			if final_digits[index-1] == int(str(max_num)[index-1]):
				top = int(str(max_num)[index])
				pool = [randint(0, top),randint(0, top),randint(0, top)]
				digit = pool[randint(0,2)]

				final_digits.append(digit)
			
			else: 
				pool = [randint(0, top),randint(0, top),randint(0, top)]
				digit = pool[randint(0,2)]

				final_digits.append(digit)

		index+=1

	index -= 1
	last_number = 0

	for numstr in final_digits:
		num = int(numstr)
		last_number +=  num * (10 ** index)
		index -= 1

	return last_number

##################
# Image function #
##################

async def post_image(self, channel, payload, emojis):

    send_channel = self.bot.get_channel(int(channel))
    index = emojis.index(payload.emoji.name)
    winner_str = self.database[channel]["voters"][index]
    winner = await self.bot.fetch_user(int(winner_str))

    self.database[channel]["players"][winner_str]["score"] += 1
    self.database[channel]["voters"] = []

    width = 621
    height = 200
    question_id = self.database[channel]["question"] 
    question = self.questions[question_id][0]
    answers = self.database[channel]["players"][winner_str]["choice"]
    fields = self.database[channel]["fields"]
    font = ImageFont.truetype("OpenSans-Bold.ttf", 30)
    font_type = "OpenSans-Bold.ttf"
    font_output = 30

    author_font = ImageFont.truetype("OpenSans-LightItalic", 26)

    text_lines = []
    text_line = []
    
    text = question.upper()
    
    final_text = ""

    #####################
    # Filling questions #
    #####################
    print(question)
    print(fields)
    if "_" in question:
        for i in range(0, fields):
            da_choice = self.database[channel]["players"][winner_str]["choice"][i]
            print(self.answers[str(da_choice)])
            replace = ""
            if self.answers[str(da_choice)][-1] == ".":
                print("This is string" + str(self.answers[str(da_choice)][-1]))
                replace = self.answers[str(da_choice)][:-1]
            else:
            	replace = self.answers[str(da_choice)]
            text = text.replace("_", replace, 1)
    else:
        text = question
        text += " [br] | [br] "
        for i in range(0, fields):
            da_choice = self.database[channel]["players"][winner_str]["choice"][i]
            to_add = ""
            if self.answers[str(da_choice)][-1] == "." and  i != fields -1:
                to_add = self.answers[str(da_choice)][:-1]
            else:
                to_add = self.answers[str(da_choice)]
            
            text += (to_add)
            if i != fields - 1:
                text += ", [br] "


    #################
    # Text Wrapping #
    #################
    
    text = text.upper()
    words = text.split()

    for word in words:
            if word == '[BR]':
                text_lines.append(' '.join(text_line))
                text_line = []
                continue
            text_line.append(word)
            w, h = font.getsize(' '.join(text_line))

            if w > width:
                text_line.pop()
                text_lines.append(' '.join(text_line))
                text_line = [word]
            

    if len(text_line) > 0:
        text_lines.append(' '.join(text_line))

    
    print("Text being replaced: " + text)

    ####################
    # Ajustes de altura#
    ####################
    

    final_height = 0
    
    while True:

        ascent, descent = font.getmetrics() 
        line_heights = [font.getmask(text_line).getbbox()[3] + descent for text_line in text_lines]
        height_text = sum(line_heights)
        final_height = height_text
        print(final_height)

        if height_text > height:
                font_output -= 3
                font = ImageFont.truetype(font_type, font_output)
        else:
            break

    final_font=ImageFont.truetype(font_type, font_output)

    ##################
    # Creando imagen #
    ##################
    
    link = ("imgs/" + str(self.database[channel]["img"]) + ".jpg")
    print("imgs/" + str(self.database[channel]["img"]) + ".jpg")
    img = Image.open(link)
    draw = ImageDraw.Draw(img)
    current_h = (432-final_height) / 2

    self.database[channel]["img"] += 1
    if self.database[channel]["img"] > 8:
        self.database[channel]["img"] = 1

    for line in text_lines:
        print("imprimiendo lineas")
        w,h=draw.textsize(line, font=final_font)
        draw.text(((691-w)/2, current_h), line, font=final_font)   
        current_h += h

    #########
    # Autor #
    #########

    guild = self.bot.get_guild(self.database[channel]["guild"])
    member = guild.get_member(int(winner_str))
    print_member = None
   
    if member:
        if member.nick:
            print_member = member.nick
        else:
            print_member = member.name
    else:
        result = await guild.query_members(limit=1, user_ids=[player])
        member = result[0]
        if member.nick:
            print_member = member.nick
        else:
            print_member = member.name

    w,h=draw.textsize("Hoga", font=final_font)
    print("Current Height: " + str(current_h) + "\nFinal Height:"+ str(final_height) + "\n" +str(h))
    draw.text((600, current_h  + h), print_member, font=author_font, anchor="rt")

    img.save('imgs/c' + channel + '.jpg')

    await send_channel.send(file=discord.File('imgs/c' + channel + '.jpg'))

async def get_nickname(self, channel, player):
	guild = self.bot.get_guild(self.database[channel]["guild"])
	member = guild.get_member(int(player))
	print_member = None
	if member:
		if member.nick:
			print_member = member.nick
		else:
			print_member = member.name
	else:
		result = await guild.query_members(limit=1, user_ids=[player])
		member = result[0]
		if member.nick:
			print_member = member.nick
		else:
			print_member = member.name

	return print_member

def player_template():
	result =	{
					"hand": [],
					"choice": [],
					"score": 0,
					"popularity": 0,
					"private_channel": None,
					"waiting_reaction": False,
					"remaining": 0
				}

	return result

def cah_template(guild, user, self):

	x = range(1, 100)
	deck_cards = []

	for i in x:
		deck_cards.append(i)

	question_len = len(self.questions)
	question_cards = []

	for i in range(1, question_len):
		question_cards.append(i)

	var = {
			"guild": guild,
			"on_game" : False,
			"on_message" : False,
			
			"admins":[str(user)],

			"rounds": None,
			"turn": 1,
			"last_turn": 3,

			"invitations" : True,
			"dm_invitations": {},
			"open_invitations": [],
			"voting_sent": False,


			"questions": question_cards,
			"question": None,
			"fields": 0,
			"discarded_questions": [],


			"deck_name":"default",
			"deck": deck_cards,
			"discarded": [],
			
			"reaction_id":[],
			"reveal_id": [],
			"popularity_id":[],	

			"popularity_time": [],
			"turn_time": [],
			"last_active" : None,
			
			"judge": None,
			"waiting_for": [],
			"voters": [],
			"phase": "reveal",
			
			"img" : randint(1,8),
			
			"p_number": 1,
			"players": {
				str(user): {
					"hand": [],
					"choice": [],
					"score": 0,
					"popularity": 0,
					"private_channel": None,
					"waiting_reaction": False,
					"remaining": 0
					}
				}	
			}


	return var

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

async def no_permission(channel_send):
	embed = discord.Embed(title=None, description="No tienes los permisos para usar este comando.", color=0xd63e3e)
	msg = await channel_send.send(embed=embed)
	await asyncio.sleep(10)
	await msg.delete()

def setup(bot):
	bot.add_cog(cah(bot))
	print("Cartas contra la humanidad está funcionando")