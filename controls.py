import keyboard, mouse
from math import sin, cos, radians
from math_functions import rad_rotation, get_camera_rots, multVscalar, plusV, minusV

def controls_initialize(cam_position, camera_rotation, forward_rot, right_rot, delta_seconds, cam_speed, sensivity, past_mouse = []):
    new_pos = cam_position
    new_rot = camera_rotation
    if len(past_mouse) > 1: past_mouse.pop(0)
    forward_move = multVscalar(multVscalar(forward_rot, -1), cam_speed*delta_seconds)
    right_move = multVscalar(multVscalar(right_rot, -1), cam_speed*delta_seconds)
    
    # Keyboard controls
    if keyboard.is_pressed("q"):
        new_pos = cam_position[0], cam_position[1], cam_position[2] - cam_speed * delta_seconds
    if keyboard.is_pressed("e"):
        new_pos = cam_position[0], cam_position[1], cam_position[2] + cam_speed * delta_seconds 
    if keyboard.is_pressed("w"):
        new_pos = plusV(cam_position, forward_rot)
    if keyboard.is_pressed("s"):
        new_pos = minusV(cam_position, forward_rot)
    if keyboard.is_pressed("a"):
        new_pos = plusV(cam_position, right_rot)
    if keyboard.is_pressed("d"):
        new_pos = minusV(cam_position, right_rot)

    past_mouse.append(mouse.get_position())
    if len(past_mouse) > 1: 
        
        dxm = ((past_mouse[-1][0] - past_mouse[0][0]) * delta_seconds * sensivity)
        dym = ((past_mouse[-1][1] - past_mouse[0][1]) * delta_seconds * sensivity) * -1

        new_rot = (0, new_rot[1] + dxm, min(max(new_rot[2] + dym, -89), 89))

    return new_pos, new_rot