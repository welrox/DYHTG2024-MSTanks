from utilities import GetHeading, ServerMessageTypes
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

# Now you can call this function with the player's current position and the target position:
# Example usage:
# go(my_position[0], my_position[1], enemy_position[0], enemy_position[1])
