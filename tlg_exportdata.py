# -*- coding: utf-8 -*-
'''
Script:
    tlg_exportchat.py
Description:
    Python script that use the Telegram Client API to get all chat messages and export them to a \
	file.
Author:
    Jose Rios Rubio
Creation date:
    04/02/2018
Last modified date:
    04/02/2018
Version:
    1.0.0
'''

####################################################################################################

### Libraries/Modules ###

from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

from collections import OrderedDict
from os import path, stat, remove, makedirs

import json

####################################################################################################

### Constants ###

# Client parameters
API_ID   = NNNNNN
API_HASH = 'ffffffffffffffffffffffffffffffff'
PHONE_NUM    = '+NNNNNNNNNNN'
LOGIN_CODE = "NNNNN"

# Chat to inspect
CHAT_LINK  = "https://t.me/GroupName"

####################################################################################################

### Telegram basic functions ###

# Get basic info from a chat
def tlg_get_basic_info(client, chat):
	'''Get basic information (id, title, name, num_users, num_messages) from a group/channel/chat'''
	# Get the corresponding chat entity
	chat_entity = client.get_entity(chat)
	# Get the number of users in the chat
	num_members_offset = client(GetParticipantsRequest(channel=chat_entity, \
		filter=ChannelParticipantsSearch(''), offset=0, limit=0, hash=0)).count
	num_members = client(GetParticipantsRequest(channel=chat_entity, \
		filter=ChannelParticipantsSearch(''), offset=num_members_offset, limit=0, hash=0)).count
	# Get messages data from the chat and extract the usefull data related to chat
	msgs = client.get_message_history(chat_entity, limit=1)
	basic_info = OrderedDict \
		([ \
			("id", msgs.data[0].to.id), \
			("title", msgs.data[0].to.title), \
			("username", msgs.data[0].to.username), \
			("num_members", num_members), \
			("num_messages", msgs.total), \
			("supergroup", msgs.data[0].to.megagroup) \
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
	num_members = client(GetParticipantsRequest(channel=chat_entity, \
		filter=ChannelParticipantsSearch(''), offset=0, limit=0, hash=0)).count
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
def tlg_get_all_messages(client, chat):
	'''Get all members information from a group/channel/chat'''
	# Set the result list
	messages = []
	# Get the corresponding chat entity
	chat_entity = client.get_entity(chat)
	# Get and save all messages data in a single list
	num_msg = client.get_message_history(chat_entity, limit=1).total
	msgs = client.get_message_history(chat_entity, limit=num_msg)
	# Build our messages data structures and add them to the list
	for msg in reversed(msgs.data):
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
				if msg_text == "None":
					msg_text = "[Image/Audio/Video/File/...]"
				if msg['reply_to']:
					msg_to_Write = "\n[MSG ID - {}]\n{}\n{}:\n[In reply to {}] - {}\n\n" \
						.format(msg['id'], sent_moment, msg['sender_user'], msg['reply_to'], \
						msg['text'])
				else:
					msg_to_Write = "\n[MSG ID - {}]\n{}\n{}:\n{}\n\n" \
						.format(msg['id'], sent_moment, msg['sender_user'],	msg['text'])
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
	# Create the client and connect
	client = TelegramClient("Session", API_ID, API_HASH)
	client.connect()

	# Check and login the client if needed
	if not client.is_user_authorized():
		client.sign_in(PHONE_NUM, LOGIN_CODE)
	else:
    	# Get chat basic info to determine chat name
		chat_info = tlg_get_basic_info(client, CHAT_LINK)
		if chat_info["username"]:
			chat_name = chat_info["username"]
		else:
			chat_name = chat_info["title"]

		# Get all messages data from the chat
		messages = tlg_get_all_messages(client, CHAT_LINK)

		# Write to the file all the messages history
		file_write_history(chat_name, messages)
		

####################################################################################################

### Execute the main function if the file is not an imported module ###
if __name__ == "__main__":
	main()

