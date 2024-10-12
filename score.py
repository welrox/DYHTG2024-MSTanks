from utilities import *
import go
from time import sleep

def score(GameServer, my_position):
    closest_goal = None
    blue = (0, 100)
    orange = (0, -100)

    blue_dist = CalculateDistance(my_position[0], my_position[1], blue[0], blue[1])
    orange_dist = CalculateDistance(
        my_position[0], my_position[1], orange[0], orange[1]
    )

    if blue_dist < orange_dist:
        closest_goal = blue
    else:
        closest_goal = orange

    go.go(GameServer, my_position[0], my_position[1], closest_goal[0], closest_goal[1]*0.8)
    sleep((CalculateDistance(my_position[0], my_position[1], closest_goal[0], closest_goal[1])*0.8)/TANK_SPEED)
    go.go(GameServer, my_position[0], my_position[1], closest_goal[0], closest_goal[1]*1.5)
    

    # heading = GetHeading(
    #     my_position[0], my_position[1], closest_goal[0], closest_goal[1]
    # )
    # GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING, {"Amount": 360-heading})
    # GameServer.sendMessage(
    #     ServerMessageTypes.MOVEFORWARDDISTANCE, {"Amount": closest_dist}
    # )
