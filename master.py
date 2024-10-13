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
import attack

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

if not ':' in args.name:
	raise RuntimeError("You forgot to provide the team name followed by a ':' before the bot's name")
my_team = args.name.split(':')[0]

# Main loop - read game messages, ignore them and randomly perform actions
current_time = 0
enemy_id = None
enemy_position = None
enemy_last_seen_time = -1000
my_health = 1
my_ammo = 1
my_position = (0,0)
my_heading = 0
my_turret_heading = 0
snitch_picked_up = {'flag': False, 'holder': None}

should_i_score = False

visible_pickups = {}
while True:
	################## do message handling here
	message = GameServer.readMessage()
 
	match message["messageType"]:
		case ServerMessageTypes.OBJECTUPDATE:
			if message["Type"] == "Tank":
			#print(message)
				if message["Name"] != args.name and my_team not in message['Name']:
					enemy_id = message['Id']
					enemy_position = (message["X"], message["Y"])
					enemy_last_seen_time = current_time
				elif message["Name"] == args.name:
					my_position = (message["X"], message["Y"])
					my_health = message['Health']
					my_ammo = message['Ammo']
					my_heading = message['Heading']
					my_turret_heading = message['TurretHeading']
			else:
				pickup = {'Type': message['Type'], 'X': message['X'], 'Y': message['Y'], 'TimeSeen': current_time}
				pickup_position = (message['X'], message['Y'])
				visible_pickups[pickup_position] = pickup
		case ServerMessageTypes.KILL:
			should_i_score = True
			score.score(GameServer, my_position)
		case ServerMessageTypes.ENTEREDGOAL | ServerMessageTypes.DESTROYED:
			should_i_score = False
			hunt.hunt(GameServer, my_position[0], my_position[1], my_turret_heading)
		case ServerMessageTypes.SNITCHPICKUP:
			snitch_picked_up["flag"] = True
			snitch_picked_up["holder"] = message["Id"]
			
	
	if my_position and enemy_position and current_time - enemy_last_seen_time < 10 and my_ammo > 0 and my_health > 1:
		if should_i_score:
			attack.attack_but_dont_strafe(GameServer, my_position, enemy_position, enemy_id, my_turret_heading, current_time)
		else:
			attack.attack(GameServer, my_position, enemy_position, enemy_id, my_turret_heading, current_time)
   
	elif my_health == 1 and not should_i_score:
		recent_health = GetClosestPickup(visible_pickups, my_position[0], my_position[1], "HealthPickup")
		logging.info(recent_health)
		if recent_health:
			go.go_and_look(GameServer, my_position[0], my_position[1], recent_health[0], recent_health[1])
		else:
			go.go_and_look(GameServer, my_position[0], my_position[1], 0, 0)
   
	elif my_ammo == 0 and not should_i_score:
		recent_ammo = GetClosestPickup(visible_pickups, my_position[0], my_position[1], "AmmoPickup")
		logging.info(recent_ammo)
		if recent_ammo:
			go.go_and_look(GameServer, my_position[0], my_position[1], recent_ammo[0], recent_ammo[1])
		else:
			go.go_and_look(GameServer, my_position[0], my_position[1], 0, 0)

	elif not should_i_score:
		hunt.hunt(GameServer, my_position[0], my_position[1], my_turret_heading)

	
	# remove any pickups that we haven't seen in a while
	visible_pickups = {position:pickup for position,pickup in visible_pickups.items() if current_time - pickup['TimeSeen'] < 5}

	print(f"health: {my_health}, ammo: {my_ammo}")

	# pp = pprint.PrettyPrinter()
	# print("visible pickups")
	# pp.pprint(visible_pickups)

	
	
	current_time += 1
