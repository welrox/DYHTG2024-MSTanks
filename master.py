#!/usr/bin/python

import json
import socket
import logging
import binascii
import struct
import argparse
import random
import math
import pprint
import random

# import bot functions here
import score
import go
from LookForAmmo import *
import hunt

def RadianToDegree(angle):
	return angle * (180.0 / math.pi)

def GetHeading(x1,y1,x2,y2):
	heading = math.atan2(y2 - y1, x2 - x1)
	heading = RadianToDegree(heading)
	print(heading)
	heading = (heading - 360) % 360
	print(heading)
	return math.fabs(heading)



class ServerMessageTypes(object):
	TEST = 0
	CREATETANK = 1
	DESPAWNTANK = 2
	FIRE = 3
	TOGGLEFORWARD = 4
	TOGGLEREVERSE = 5
	TOGGLELEFT = 6
	TOGGLERIGHT = 7
	TOGGLETURRETLEFT = 8
	TOGGLETURRETRIGHT = 9
	TURNTURRETTOHEADING = 10
	TURNTOHEADING = 11
	MOVEFORWARDDISTANCE = 12
	MOVEBACKWARSDISTANCE = 13
	STOPALL = 14
	STOPTURN = 15
	STOPMOVE = 16
	STOPTURRET = 17
	OBJECTUPDATE = 18
	HEALTHPICKUP = 19
	AMMOPICKUP = 20
	SNITCHPICKUP = 21
	DESTROYED = 22
	ENTEREDGOAL = 23
	KILL = 24
	SNITCHAPPEARED = 25
	GAMETIMEUPDATE = 26
	HITDETECTED = 27
	SUCCESSFULLHIT = 28
    
	strings = {
		TEST: "TEST",
		CREATETANK: "CREATETANK",
		DESPAWNTANK: "DESPAWNTANK",
		FIRE: "FIRE",
		TOGGLEFORWARD: "TOGGLEFORWARD",
		TOGGLEREVERSE: "TOGGLEREVERSE",
		TOGGLELEFT: "TOGGLELEFT",
		TOGGLERIGHT: "TOGGLERIGHT",
		TOGGLETURRETLEFT: "TOGGLETURRETLEFT",
		TOGGLETURRETRIGHT: "TOGGLETURRENTRIGHT",
		TURNTURRETTOHEADING: "TURNTURRETTOHEADING",
		TURNTOHEADING: "TURNTOHEADING",
		MOVEFORWARDDISTANCE: "MOVEFORWARDDISTANCE",
		MOVEBACKWARSDISTANCE: "MOVEBACKWARDSDISTANCE",
		STOPALL: "STOPALL",
		STOPTURN: "STOPTURN",
		STOPMOVE: "STOPMOVE",
		STOPTURRET: "STOPTURRET",
		OBJECTUPDATE: "OBJECTUPDATE",
		HEALTHPICKUP: "HEALTHPICKUP",
		AMMOPICKUP: "AMMOPICKUP",
		SNITCHPICKUP: "SNITCHPICKUP",
		DESTROYED: "DESTROYED",
		ENTEREDGOAL: "ENTEREDGOAL",
		KILL: "KILL",
		SNITCHAPPEARED: "SNITCHAPPEARED",
		GAMETIMEUPDATE: "GAMETIMEUPDATE",
		HITDETECTED: "HITDETECTED",
		SUCCESSFULLHIT: "SUCCESSFULLHIT"
	}
    
	def toString(self, id):
		if id in self.strings.keys():
			return self.strings[id]
		else:
			return "??UNKNOWN??"


class ServerComms(object):
	'''
	TCP comms handler
	
	Server protocol is simple:
	
	* 1st byte is the message type - see ServerMessageTypes
	* 2nd byte is the length in bytes of the payload (so max 255 byte payload)
	* 3rd byte onwards is the payload encoded in JSON
	'''
	ServerSocket = None
	MessageTypes = ServerMessageTypes()
	
	
	def __init__(self, hostname, port):
		self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ServerSocket.connect((hostname, port))

	def readTolength(self, length):
		messageData = self.ServerSocket.recv(length)
		while len(messageData) < length:
			buffData = self.ServerSocket.recv(length - len(messageData))
			if buffData:
				messageData += buffData
		return messageData

	def readMessage(self):
		'''
		Read a message from the server
		'''
		messageTypeRaw = self.ServerSocket.recv(1)
		messageLenRaw = self.ServerSocket.recv(1)
		messageType = struct.unpack('>B', messageTypeRaw)[0]
		messageLen = struct.unpack('>B', messageLenRaw)[0]
		
		if messageLen == 0:
			messageData = bytearray()
			messagePayload = {'messageType': messageType}
		else:
			messageData = self.readTolength(messageLen)
			logging.debug("*** {}".format(messageData))
			messagePayload = json.loads(messageData.decode('utf-8'))
			messagePayload['messageType'] = messageType
			
		logging.debug('Turned message {} into type {} payload {}'.format(
			binascii.hexlify(messageData),
			self.MessageTypes.toString(messageType),
			messagePayload))
		return messagePayload
		
	def sendMessage(self, messageType=None, messagePayload=None):
		'''
		Send a message to the server
		'''
		message = bytearray()
		
		if messageType is not None:
			message.append(messageType)
		else:
			message.append(0)
		
		if messagePayload is not None:
			messageString = json.dumps(messagePayload)
			message.append(len(messageString))
			message.extend(str.encode(messageString))
			    
		else:
			message.append(0)
		
		logging.debug('Turned message type {} payload {} into {}'.format(
			self.MessageTypes.toString(messageType),
			messagePayload,
			binascii.hexlify(message)))
		return self.ServerSocket.send(message)


# Parse command line args
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
parser.add_argument('-H', '--hostname', default='127.0.0.1', help='Hostname to connect to')
parser.add_argument('-p', '--port', default=8052, type=int, help='Port to connect to')
parser.add_argument('-n', '--name', default='TeamA:RandomBot', help='Name of bot')
args = parser.parse_args()

# Set up console logging
if args.debug:
	logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.DEBUG)
else:
	logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.INFO)


# Connect to game server
GameServer = ServerComms(args.hostname, args.port)

# Spawn our tank
logging.info("Creating tank with name '{}'".format(args.name))
GameServer.sendMessage(ServerMessageTypes.CREATETANK, {'Name': args.name})

# Main loop - read game messages, ignore them and randomly perform actions
current_time = 0
enemy_position = None
enemy_last_seen_time = -1000
my_health = 1
my_ammo = 1
my_position = None
my_heading = None
my_turret_heading = None
snitch_picked_up = {'flag': False, 'holder': None}

should_i_score = False

visible_pickups = {}
while True:
	################## do message handling here
	message = GameServer.readMessage()
	if message["messageType"] == ServerMessageTypes.OBJECTUPDATE:
		if message["Type"] == "Tank":
			#print(message)
			if message["Name"] != args.name:
				enemy_position = (message["X"], message["Y"])
				enemy_last_seen_time = current_time
			else:
				my_position = (message["X"], message["Y"])
				my_health = message['Health']
				my_ammo = message['Ammo']
				my_heading = message['Heading']
				my_turret_heading = message['TurretHeading']
		else:
			pickup = {'Type': message['Type'], 'X': message['X'], 'Y': message['Y'], 'TimeSeen': current_time}
			pickup_position = (message['X'], message['Y'])
			visible_pickups[pickup_position] = pickup

	elif message["messageType"] == ServerMessageTypes.KILL:
		should_i_score = True
		score.score(GameServer, my_position)
	elif message['messageType'] == ServerMessageTypes.ENTEREDGOAL:
		should_i_score = False
	
	elif message["messageType"] == ServerMessageTypes.SNITCHPICKUP:
		snitch_picked_up["flag"] = True
		snitch_picked_up["holder"] = message["id"]

	if my_position and enemy_position and current_time - enemy_last_seen_time < 3 and my_ammo > 0 and not should_i_score:
		GameServer.sendMessage(ServerMessageTypes.STOPALL)
		heading = 360 - GetHeading(my_position[0], my_position[1], enemy_position[0], enemy_position[1])
		GameServer.sendMessage(ServerMessageTypes.TURNTURRETTOHEADING, {"Amount": heading})
		GameServer.sendMessage(ServerMessageTypes.FIRE)
  
		new_x, new_y = random.randint(int(my_position[0]) - 10, int(my_position[0]) + 10), random.randint(int(my_position[1]) - 10, int(my_position[1]) + 10)
		go.go(GameServer, my_position[0], my_position[1], new_x, new_y)
		logging.info(f"Turning to heading {heading}")
	elif my_ammo == 0 and not should_i_score:
		recent_ammo = GetMostRecentlySeenAmmo(visible_pickups, GameServer, my_position[0], my_position[1])
		logging.info(recent_ammo)
		if recent_ammo:
			go.go_and_look(GameServer, my_position[0], my_position[1], recent_ammo[0], recent_ammo[1])
		else:
			go.go_and_look(GameServer, my_position[0], my_position[1], 0, 0)
	else:
		hunt.hunt(GameServer, my_position[0], my_position[1])
	
	# remove any pickups that we haven't seen in a while
	visible_pickups = {position:pickup for position,pickup in visible_pickups.items() if current_time - pickup['TimeSeen'] < 5}

	print(f"health: {my_health}, ammo: {my_ammo}")

	# pp = pprint.PrettyPrinter()
	# print("visible pickups")
	# pp.pprint(visible_pickups)

	
	
	current_time += 1
