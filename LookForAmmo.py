from utilities import *

def GetClosestPickup(pickups :dict, player_x, player_y, pickup_type):
    lowest = None
    lowest_coords = None
    for key, pickup in pickups.items():
        if pickup["Type"] == pickup_type:
            if lowest == None: lowest =  pickup["TimeSeen"]
            if lowest_coords == None: lowest_coords = key
            dist = CalculateDistance(player_x, player_y, key[0], key[1])
            if dist < lowest:
                lowest = dist
                lowest_coords = key
    
    return lowest_coords