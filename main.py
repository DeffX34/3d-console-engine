from time import time, sleep
import numpy as np
from math import sin, cos
import os
from controls import controls_initialize
import keyboard, mouse
os.system("cls" if os.name == "nt" else "clear")
from math_functions import get_camera_rots
from shapes import *

FPS = 60
WIDTH, HEIGHT = 60, 30
WINDOW_SIZE = WIDTH*HEIGHT
near, far = 0, 200

aspect, focal = WIDTH/HEIGHT, 120
start_time = time()
cube = Cube((0, 0, 0), (0, 20, 0), 5)
pyramide = Pyramide((0, 180, 0), (20, 20, 0), 5)

cam_position, cam_rotation = (0, 0, 0), (0, 90, 0)
delta_seconds = 0
symbols_1 = "█▓▒░▫"
symbols_2 = "@$%&*"

while True:
    t = (time() - start_time) * 0.45
    current_time = time()

    zbuffer = np.full(WINDOW_SIZE, 9999999, dtype=np.float32)
    canvas = np.full(WINDOW_SIZE, ".")
    
    cam_speed = 60
    sensivity = 25

    rotations = get_camera_rots(cam_rotation)
    
    forward_rot = rotations[0]
    right_rot = rotations[1]

    cam_position, cam_rotation = controls_initialize(cam_position, cam_rotation, forward_rot, right_rot, delta_seconds, cam_speed, sensivity)

    cube.draw(canvas, zbuffer, cam_position, cam_rotation, WIDTH, HEIGHT, focal, aspect, symbols_1, near, far, 0, t)

    pyramide.draw(canvas, zbuffer, cam_position, cam_rotation, WIDTH, HEIGHT, focal, aspect, symbols_2, near, far, 0, t)

    rows = "\n".join(["".join([canvas[y * WIDTH + x] for x in range(WIDTH)]) for y in range(HEIGHT)])

    print("\033[H" + rows, end="", flush=True)

    # print(" " * 40 + f"zbuffer bytes size:{zbuffer.nbytes}\n", " " * 40 * 2 + f"window size: {WIDTH} * {HEIGHT} = {WINDOW_SIZE}")

    sleep(1/FPS)
    delta_seconds = time() - current_time