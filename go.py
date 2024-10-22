from utilities import GetHeading, ServerMessageTypes
from attack import attack_but_dont_strafe
import math

def go(GameServer, player_x, player_y, target_x, target_y):
    """
    Move the tank from (player_x, player_y) to (target_x, target_y)
    """

    # Step 1: Calculate heading to the target location
    heading = GetHeading(player_x, player_y, target_x, target_y)
    
    # Step 2: Rotate the tank towards the target
    heading = 360 - heading  # Adjust heading as per the original logic
    GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING, {'Amount': heading})
    
    # Step 3: Move the tank forward
    # Assuming that the tank moves a fixed distance towards the target.
    distance = math.sqrt((target_x - player_x)**2 + (target_y - player_y)**2)
    GameServer.sendMessage(ServerMessageTypes.MOVEFORWARDDISTANCE, {'Amount': distance})

def go_and_look(GameServer, player_x, player_y, target_x, target_y):
    """
    Move the tank from (player_x, player_y) to (target_x, target_y)
    oh and also look at the target
    """

    # Step 1: Calculate heading to the target location
    heading = GetHeading(player_x, player_y, target_x, target_y)
    
    # Step 2: Rotate the tank towards the target
    heading = 360 - heading  # Adjust heading as per the original logic
    GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING, {'Amount': heading})

    # Step 2.5: Rotate the tank turret towards the target
    GameServer.sendMessage(ServerMessageTypes.TURNTURRETTOHEADING, {'Amount': heading})

    
    # Step 3: Move the tank forward
    # Assuming that the tank moves a fixed distance towards the target.
    distance = math.sqrt((target_x - player_x)**2 + (target_y - player_y)**2)
    GameServer.sendMessage(ServerMessageTypes.MOVEFORWARDDISTANCE, {'Amount': distance})

def go_and_look_attack(GameServer, player_position, target_x, target_y, enemy_position, enemy_id, my_turret_heading, current_time):
    """
    Move the tank from (player_x, player_y) to (target_x, target_y)
    oh and also attack a target if in line of sight
    """
    
    # Step 1: Calculate heading to the target location
    heading = GetHeading(player_position[0], player_position[1], target_x, target_y)
    
    # Step 2: Rotate the tank towards the target
    heading = 360 - heading  # Adjust heading as per the original logic
    GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING, {'Amount': heading})

    # Step 2.5: 
    attack_but_dont_strafe(GameServer, player_position, enemy_position, enemy_id, my_turret_heading, current_time)
    
    # Step 3: Move the tank forward
    # Assuming that the tank moves a fixed distance towards the target.
    distance = math.sqrt((target_x - player_position[0])**2 + (target_y - player_position[1])**2)
    GameServer.sendMessage(ServerMessageTypes.MOVEFORWARDDISTANCE, {'Amount': distance})
    