from utilities import *
import go
import random

def hunt(GameServer, player_x, player_y, heading):
    #if CalculateDistance(player_x, player_y, 0, 0) > 3:
    go.go(GameServer, player_x, player_y, 0, 0)
    GameServer.sendMessage(ServerMessageTypes.TURNTURRETTOHEADING, {'Amount': random.randint(0, 359)})