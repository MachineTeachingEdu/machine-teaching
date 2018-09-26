def robot_position(steps_list):
    import math
    pos = [0,0]

    for movement in steps_list:
        direction = movement[0]
        steps = int(movement[1])
        if direction=="UP":
            pos[0]+=steps
        elif direction=="DOWN":
            pos[0]-=steps
        elif direction=="LEFT":
            pos[1]-=steps
        elif direction=="RIGHT":
            pos[1]+=steps
        else:
            pass

    return round(math.sqrt(pos[1]**2+pos[0]**2))
