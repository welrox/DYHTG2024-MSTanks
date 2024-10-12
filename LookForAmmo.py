from utilities import *

def GetMostRecentlySeenAmmo(pickups :dict, Gameserver, player_x, player_y):
    lowest = None
    lowest_coords = None
    for key, pickup in pickups.items():
        if lowest == None: lowest =  pickup["TimeSeen"]
        if lowest_coords == None: lowest_coords = key

        if pickup["Type"] == "AmmoPickup":
            dist = CalculateDistance(player_x, player_y, key[0], key[1])
            if dist < lowest:
                lowest = dist
                lowest_coords = key
    
    return lowest_coords