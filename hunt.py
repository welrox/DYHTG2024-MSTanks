from utilities import *
import go

def hunt(GameServer, player_x, player_y):
    go.go(GameServer, player_x, player_y, 0, 0)
    heading = GetHeading(player_x, player_y, 0, 0)
    if math.fabs(heading) < 1:
        print("looking at 180")
        GameServer.sendMessage(ServerMessageTypes.TURNTURRETTOHEADING, {'Amount': 180})
    elif math.fabs(heading) > 170:
        print("looking at 0")
        GameServer.sendMessage(ServerMessageTypes.TURNTURRETTOHEADING, {'Amount': 0})