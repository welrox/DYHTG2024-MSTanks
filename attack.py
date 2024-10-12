from utilities import *
import go
import random

is_strafing = False
strafe_target = (100,100)
last_enemy_position = {}
actual_enemy_velocity = {}
started_strafing_at_time = -1000

def attack(GameServer, my_position, enemy_position, enemy_id, my_turret_heading, current_time):
    global is_strafing
    global strafe_target
    global started_strafing_at_time
    global last_enemy_position
    global actual_enemy_velocity

    if not is_strafing:
        # here, we aren't strafing but instead we're trying to aim at target and fire

        if enemy_id not in last_enemy_position:
            # setup global dicts if we have just encountered the enemy
            actual_enemy_velocity[enemy_id] = (0,0)
            last_enemy_position[enemy_id] = enemy_position

        enemy_velocity = (enemy_position[0] - last_enemy_position[enemy_id][0], enemy_position[1] - last_enemy_position[enemy_id][1])
        if actual_enemy_velocity[enemy_id] != enemy_velocity and CalculateDistance(enemy_velocity[0], enemy_velocity[1], 0, 0) > 0.001:
            # enemy's velocity has changed, let's update actual_enemy_velocity
            print(f"set {actual_enemy_velocity}")
            actual_enemy_velocity[enemy_id] = enemy_velocity
        
        print(f"{actual_enemy_velocity=}")
        heading = 360 - GetHeading(my_position[0], my_position[1], enemy_position[0] + actual_enemy_velocity[enemy_id][0], enemy_position[1] + actual_enemy_velocity[enemy_id][1])
        if math.fabs(my_turret_heading - heading) < 3:
            # we are aiming close enough, let's shoot and begin strafing
            GameServer.sendMessage(ServerMessageTypes.FIRE)
            print("Took the shot, now Strafing!")
            print(f"    (shot enemy when their velocity was {actual_enemy_velocity[enemy_id]})")
            is_strafing = True
            del last_enemy_position[enemy_id]
            del actual_enemy_velocity[enemy_id]
            started_strafing_at_time = current_time
            strafe_target = random.randint(int(my_position[0]) - 10, int(my_position[0]) + 10), random.randint(int(my_position[1]) - 10, int(my_position[1]) + 10)
            go.go(GameServer, my_position[0], my_position[1], strafe_target[0], strafe_target[1])
        else:
            # our aim is not on point, let's keep aiming
            GameServer.sendMessage(ServerMessageTypes.TURNTURRETTOHEADING, {"Amount": heading})
            last_enemy_position[enemy_id] = enemy_position
    else:
        # we are strafing here
        if CalculateDistance(my_position[0], my_position[1], strafe_target[0], strafe_target[1]) < 3 or current_time - started_strafing_at_time > 10:
            print("Stopped strafing!")
            is_strafing = False
        else:
            # look at enemy position while strafing so we don't forget that they exist
            heading = 360 - GetHeading(my_position[0], my_position[1], enemy_position[0], enemy_position[1])
            GameServer.sendMessage(ServerMessageTypes.TURNTURRETTOHEADING, {"Amount": heading})
            go.go(GameServer, my_position[0], my_position[1], strafe_target[0], strafe_target[1])

    