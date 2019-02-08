# -*- coding: utf-8 -*-
'''
Script:
    tlg_exportchat.py
Description:
    Python script that use the Telegram Client API to get all chat messages and export them to a 
	file.
Author:
    Jose Rios Rubio
Creation date:
    04/02/2018
Last modified date:
    01/07/2018
Version:
    1.2.0
'''

####################################################################################################

### Libraries/Modules ###

import json
from telethon import TelegramClient, sync
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from collections import OrderedDict
from os import path, stat, remove, makedirs
from sys import exit

####################################################################################################

### Constants ###

# Client parameters
API_ID   = NNNNNN
API_HASH = 'ffffffffffffffffffffffffffffffff'
PHONE_NUM = '+NNNNNNNNNNN'

####################################################################################################

### Telegram basic functions ###

# Connect and Log-in/Sign-in to telegram API
def tlg_connect(api_id, api_hash, phone_number):
	'''Connect and Log-in/Sign-in to Telegram API. Request Sign-in code for first execution'''
	print('Trying to connect to Telegram...')
	client = TelegramClient("Session", api_id, api_hash)
	if not client.start():
		print('Could not connect to Telegram servers.')
		return None
	else:
		if not client.is_user_authorized():
			print('Session file not found. This is the first run, sending code request...')
			client.sign_in(phone_number)
			self_user = None
			while self_user is None:
				code = input('Enter the code you just received: ')
				try:
					self_user = client.sign_in(code=code)
				except SessionPasswordNeededError:
					pw = getpass('Two step verification is enabled. Please enter your password: ')
					self_user = client.sign_in(password=pw)
					if self_user is None:
						print('Error: Can\'t sign in to Telegram.\n')
						return None
			print('Sign in to Telegram success.\n')
		else:
			print('Log in to Telegram success.\n')
	return client


def tlg_get_basic_info(client, chat):
	'''Get basic information (id, title, name, num_users, num_messages) from a group/channel/chat'''
	# Get the corresponding chat entity
	try:
		chat_entity = client.get_entity(chat)
	except ValueError:
		print("Can't find the provided chat.")
		exit(1)
	# Get the number of users in the chat
	try:
		num_members = client.get_participants(chat_entity)
	except Exception:
		print("Can't get number of members in the chat (Chat Admin privileges required).")
		num_members = "Chat Admin privileges required"
	# Get messages data from the chat and extract the usefull data related to chat
	msgs = client.get_messages(chat_entity, limit=1)
	basic_info = OrderedDict \
		([ \
			("id", msgs[0].chat_id), \
			("title", msgs[0].chat.title), \
			("username", msgs[0].chat.username), \
			("num_members", num_members), \
			("num_messages", msgs.total), \
			("supergroup", msgs[0].chat.megagroup) \
		])
	# Return basic info dict
	return basic_info


# Get all members data from a chat
def tlg_get_all_members(client, chat):
	'''Get all members information from a group/channel/chat'''
	# Get the corresponding chat entity
	chat_entity = client.get_entity(chat)
	# Get and save all users data in a single list
	i = 0
	members = []
	users = []
	try:
		num_members = client.get_participants(chat_entity)
	except Exception:
		print("Can't get number of members in the chat (Chat Admin privileges required).")
		exit(1)
	while True:
		participants_i = client(GetParticipantsRequest(channel=chat_entity, \
			filter=ChannelParticipantsSearch(''), offset=i, limit=num_members, hash=0))
		if not participants_i.users:
			break
		users.extend(participants_i.users)
		i = i + len(participants_i.users)
	# Build our messages data structures and add them to the list
	for usr in users:
		usr_last_connection = ""
		if hasattr(usr.status, "was_online"):
			usr_last_connection = "{}/{}/{} - {}:{}:{}".format(usr.status.was_online.day, \
				usr.status.was_online.month, usr.status.was_online.year, \
				usr.status.was_online.hour, usr.status.was_online.minute, \
				usr.status.was_online.second)
		else:
			usr_last_connection = "The user does not share this information"
		usr_data = OrderedDict \
			([ \
				("id", usr.id), \
				("username", usr.username), \
				("first_name", usr.first_name), \
				("last_name", usr.last_name), \
				("last_connection", usr_last_connection) \
			])
		members.append(usr_data)
	# Return members list
	return members


# Get all messages data from a chat
def tlg_get_all_messages(client, chat_id):
	'''Get all messages information from a group/channel/chat'''
	# Set the result list
	messages = []
	# Get the corresponding chat entity
	chat_entity = client.get_entity(chat_id)
	# Get and save all messages data in a single list
	num_msg = client.get_messages(chat_entity, limit=1).total
	msgs = client.get_messages(chat_entity, limit=num_msg)
	# Build our messages data structures and add them to the list
	for msg in reversed(msgs):
		msg_sender = ""
		if hasattr(msg.sender, "first_name"):
			msg_sender = msg.sender.first_name
			if hasattr(msg.sender, "last_name"):
				if msg.sender.last_name:
					msg_sender = "{} {}".format(msg_sender, msg.sender.last_name)
		if hasattr(msg.sender, "username"):
			if msg.sender.username:
				if msg_sender != "":
					msg_sender = "{} (@{})".format(msg_sender, msg.sender.username)
				else:
					msg_sender = "@{}".format(msg.sender.username)
		msg_sent_date = "{}/{}/{}".format(msg.date.day, msg.date.month, msg.date.year)
		msg_sent_time = "{}:{}:{}".format(msg.date.hour, msg.date.minute, msg.date.second)
		msg_data = OrderedDict \
			([ \
				("id", msg.id), ("text", msg.message), ("sent_time", msg_sent_time), \
				("sent_date", msg_sent_date), ("sender_user", msg_sender), \
				("sender_user_id", msg.sender.id), ("reply_to", msg.reply_to_msg_id) \
			])
		messages.append(msg_data)
	# Return the messages data list
	return messages


def tlg_get_all_messages_from_user(client, user_id, chat_link):
	''' Get all the messages from an specified user of a group/channel/chat'''
	# Set the result list
	messages = []
	# Get the corresponding chat and user entities
	chat_entity = client.get_entity(chat_link)
	user_entity = client.get_entity(int(user_id))
	# Get and save all messages data in a single list
	num_msg = client.get_messages(chat_entity, from_user=user_entity, limit=1).total
	msgs = client.get_messages(chat_entity, from_user=user_entity, limit=num_msg)
	# Build our messages data structures and add them to the list
	for msg in reversed(msgs):
		msg_sender = msg.sender.first_name
		if msg.sender.last_name:
			msg_sender = "{} {}".format(msg_sender, msg.sender.last_name)
		if msg.sender.username:
			msg_sender = "{} (@{})".format(msg_sender, msg.sender.username)
		msg_sent_date = "{}/{}/{}".format(msg.date.day, msg.date.month, msg.date.year)
		msg_sent_time = "{}:{}:{}".format(msg.date.hour, msg.date.minute, msg.date.second)
		msg_data = OrderedDict \
			([ \
				("id", msg.id), ("text", msg.message), ("sent_time", msg_sent_time), \
				("sent_date", msg_sent_date), ("sender_user", msg_sender), \
				("sender_user_id", msg.sender.id), ("reply_to", msg.reply_to_msg_id) \
			])
		messages.append(msg_data)
	# Return the messages data list
	return messages


####################################################################################################

### Export chat messages history to file function ###

def file_write_history(chat_name, messages):
	'''Write chat messages history to file'''
	# Lets try to do it
	file_name = "./output/{}.txt".format(chat_name)
	try:
		# Create the directories of the file path if them does not exists
		directory = path.dirname(file_name)
		if not path.exists(directory):
			makedirs(directory)
		# Open the file to write (Overwrite if exists)
		with open(file_name, 'w', encoding="utf-8") as f:
			# Get export date from last messages of the chat
			export_moment = "{} - {}".format(messages[len(messages)-1]['sent_date'], \
				messages[len(messages)-1]['sent_time'])
			# Write the file header
			f.write("Exported History of \"{}\" until {}:\n" \
				"--------------------------------------------------------\n" \
				.format(chat_name, export_moment))
			# For each message, write to file
			for msg in messages:
				sent_moment = "{} - {}".format(msg['sent_date'], msg['sent_time'])
				msg_text = msg['text']
				if (msg_text is None) or (msg_text is ""):
					msg_text = "[Image/Audio/Video/File/...]"
				if msg['reply_to']:
					msg_to_Write = "\n[MSG ID - {}]\n{}\n{}:\n[In reply to {}] - {}\n\n" \
						.format(msg['id'], sent_moment, msg['sender_user'], msg['reply_to'], \
						msg_text)
				else:
					msg_to_Write = "\n[MSG ID - {}]\n{}\n{}:\n{}\n\n" \
						.format(msg['id'], sent_moment, msg['sender_user'],	msg_text)
				# Write the actual message to the file
				f.write(msg_to_Write)
	# Catch and handle errors
	except IOError as e:
		print("    I/O error({0}): {1}".format(e.errno, e.strerror))
	except ValueError:
		print("    Error: Can't convert data value to write in the file")
	except MemoryError:
		print("    Error: You are trying to write too much data")

####################################################################################################

### Main function ###
def main():
	'''Main Function'''
	print()
	# Create the client and connect
	error = False
	client = tlg_connect(API_ID, API_HASH, PHONE_NUM)
	if client is not None:
    	# Get chat link to export
		chat_link = input('\nLink of the Chat that you want to export: ')
		# Get chat basic info to determine chat name
		chat_info = tlg_get_basic_info(client, chat_link)
		chat_name = "unknown"
		if chat_info["username"]:
			chat_name = chat_info["username"]
		else:
			chat_name = chat_info["title"]
		# Show and wait for user export option selection
		print('\nExport options for {}:\n--------------------------------------------\n' \
			'  1. Export all\n' \
			'  2. Export from user\n\n'.format(chat_link))
		export_option = input('Option [1 or 2]: ')
		while (export_option != '1') and (export_option != '2'):
			print("Invalid option.\n")
			export_option = input('Option [1 or 2]: ')
		if export_option == '1':
			# Get all messages data from the chat
			print('The duration of the export process goes from minutes to hours ' \
				'depending on the number of messages that the chat has.')
			print('Exporting messages, please wait...')
			messages = tlg_get_all_messages(client, chat_link)
			# Write to the file all the messages history
			if messages:
				file_write_history(chat_name, messages)
			else:
				print('\n  Error - Can\'t access to chat messages information')
				error = True
		elif export_option == '2':
			# Get all messages data from user
			print('Getting chat members (users) info...')
			members = tlg_get_all_members(client, chat_link)
			if members:
				print('\nList of users:')
				print('---------------')
				for usr in members:
					if usr['username']:
						print('- {} [{}]'.format(usr['username'], usr['id']))
					else:
						print('- {} {} [{}]'.format(usr['first_name'], usr['last_name'], usr['id']))
				user_id = input('\nUser to export (ID): ')
				print('\nThe duration of the export process goes from minutes to hours ' \
					'depending on the number of messages that the chat has.')
				print('Exporting messages, please wait...')
				messages = tlg_get_all_messages_from_user(client, user_id, chat_link)
				# Write to the file all the messages history
				if messages:
					file_write_history(chat_name, messages)
				else:
					print('\n  Error - That user has never speak in this chat.')
					error = True
			else:
				print('\n  Error - Can\'t access to chat members information')
				error = True
		if not error:
			print("\nChat succesfully exported in output directory\n")
		
####################################################################################################

### Execute the main function if the file is not an imported module ###
if __name__ == "__main__":
	main()
