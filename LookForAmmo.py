def GetMostRecentlySeenAmmo(pickups :dict, Gameserver, player_x, player_y):
    lowest = None
    lowest_coords = None
    for key, pickup in pickups:
        if lowest == None: lowest =  pickup["TimeSeen"]
        if lowest_coords == None: lowest = key

        if pickup["Type"] == "Ammo":
            if pickup["TimeSeen"] < lowest:
                lowest = pickup["TimeSeen"]
                lowest_coords = key
    
    return lowest_coords