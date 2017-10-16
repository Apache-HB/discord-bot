import asyncio
import re
import sys

import discord
import requests
from bs4 import BeautifulSoup
from discord import Message
from discord.ext.commands import Bot

from api import newline_separator, directions, regions, statuses, release_types
from api.request import ApiRequest
from bot_config import latest_limit, newest_header, invalid_command_text, oldest_header, boot_up_message
from utils import limit_int

channel_id = "291679908067803136"
bot_spam_id = "319224795785068545"
rpcs3Bot = Bot(command_prefix="!")
pattern = '[A-z]{4}\\d{5}'


@rpcs3Bot.event
async def on_message(message: Message):
	"""
	OnMessage event listener
	:param message: message
	"""
	if message.author.name == "RPCS3 Bot":
		return
	try:
		if message.content[0] == "!":
			return await rpcs3Bot.process_commands(message)
	except IndexError as ie:
		print(message.content)
		return
	codelist = []
	for matcher in re.finditer(pattern, message.content):
		code = matcher.group(0)
		if code not in codelist:
			codelist.append(code)
			print(code)
	for code in codelist:
		info = await get_code(code)
		if not info == "None":
			await rpcs3Bot.send_message(message.channel, info)


@rpcs3Bot.command()
async def credits(*args):
	"""Author Credit"""
	return await rpcs3Bot.say("```\nMade by Roberto Anic Banic aka nicba1010!\n```")


# noinspection PyMissingTypeHints
@rpcs3Bot.command(pass_context=True)
async def c(ctx, *args):
	"""Searches the compatibility database, USE: !c searchterm """
	await compat_search(ctx, *args)


# noinspection PyMissingTypeHints
@rpcs3Bot.command(pass_context=True)
async def compat(ctx, *args):
	"""Searches the compatibility database, USE: !compat searchterm"""
	await compat_search(ctx, *args)


# noinspection PyMissingTypeHints,PyMissingOrEmptyDocstring
async def compat_search(ctx, *args):
	search_string = ""
	for arg in args:
		search_string += (" " + arg) if len(search_string) > 0 else arg

	request = ApiRequest(ctx.message.author).set_search(search_string)
	response = request.request()
	await dispatch_message(response.to_string())


# noinspection PyMissingTypeHints
@rpcs3Bot.command(pass_context=True)
async def top(ctx, *args):
	"""
	Gets the x (default 10) top oldest/newest updated games
	Example usage:
		!top old 10
		!top new 10 jap
		!top old 10 all
		!top new 10 jap playable
		!top new 10 jap playable bluray
		!top new 10 jap loadable psn
	To see all filters do !filters
	"""
	request = ApiRequest(ctx.message.author)
	if args[0] not in ("new", "old"):
		rpcs3Bot.send_message(discord.Object(id=bot_spam_id), invalid_command_text)

	if len(args) >= 1:
		if args[0] == "old":
			request.set_sort("date", "asc")
			request.set_custom_header(oldest_header)
		else:
			request.set_sort("date", "desc")
			request.set_custom_header(newest_header)
	if len(args) >= 2:
		request.set_amount(limit_int(int(args[1]), latest_limit))
	if len(args) >= 3:
		request.set_region(args[2])
	if len(args) >= 4:
		request.set_status(args[3])
	if len(args) >= 5:
		request.set_release_type(args[4])

	string = request.request().to_string()
	await dispatch_message(string)


@rpcs3Bot.command(pass_context=True)
async def filters(ctx, *args):
	message = "**Sorting directions (not used in top command)**\n"
	message += "Ascending\n```" + str(directions["a"]) + "```\n"
	message += "Descending\n```" + str(directions["d"]) + "```\n"
	message += "**Regions**\n"
	message += "Japan\n```" + str(regions["j"]) + "```\n"
	message += "US\n```" + str(regions["u"]) + "```\n"
	message += "EU\n```" + str(regions["e"]) + "```\n"
	message += "Asia\n```" + str(regions["a"]) + "```\n"
	message += "Korea\n```" + str(regions["h"]) + "```\n"
	message += "Hong-Kong\n```" + str(regions["k"]) + "```\n"
	message += "**Statuses**\n"
	message += "All\n```" + str(statuses["all"]) + "```\n"
	message += "Playable\n```" + "playable" + "```\n"
	message += "Ingame\n```" + "ingame" + "```\n"
	message += "Intro\n```" + "intro" + "```\n"
	message += "Loadable\n```" + "loadable" + "```\n"
	message += "Nothing\n```" + "nothing" + "```\n"
	message += "**Sort Types (not used in top command)**\n"
	message += "ID\n```" + "id" + "```\n"
	message += "Title\n```" + "title" + "```\n"
	message += "Status\n```" + "status" + "```\n"
	message += "Date\n```" + "date" + "```\n"
	message += "**Release Types**\n"
	message += "Blu-Ray\n```" + str(release_types["b"]) + "```\n"
	message += "PSN\n```" + str(release_types["n"]) + "```\n"
	await rpcs3Bot.send_message(ctx.message.author, message)


async def dispatch_message(message: str):
	"""
	Dispatches messages one by one divided by the separator defined in api.config
	:param message: message to dispatch
	"""
	for part in message.split(newline_separator):
		await rpcs3Bot.send_message(discord.Object(id=channel_id), part)


@rpcs3Bot.command(pass_context=True)
async def latest(ctx, *args):
	"""Get the latest RPCS3 build link"""
	appveyor_url = BeautifulSoup(requests.get("https://rpcs3.net/download").content, "lxml").find(
		"div",
		{"class": "div-download-left"}
	).parent['href']
	return await rpcs3Bot.send_message(ctx.message.author, appveyor_url)


async def get_code(code: str) -> object:
	"""
	Gets the game data for a certain game code or returns None
	:param code: code to get data for
	:return: data or None
	"""
	result = ApiRequest().set_search(code).set_amount(1).request()
	if len(result.results) == 1 and result.results[0].game_id == code:
		return "```" + result.results[0].to_string() + "```"
	return None


async def greet():
	"""
	Greets on boot!
	"""
	await rpcs3Bot.wait_until_ready()
	await rpcs3Bot.send_message(discord.Object(id=bot_spam_id), boot_up_message)


print(sys.argv[1])
rpcs3Bot.run(sys.argv[1])
asyncio.ensure_future(greet())