from math_functions import *
from math import cos, sin, pi
from rendering import *
import colorama
import numpy as np
from colorama import Style
Style.__init__()

class shape():
    def __init__(self, rotation, position, scale):
        self.rot = rotation
        self.x = position[0]
        self.y = position[1]
        self.z = position[2]
        self.pos = self.x, self.y, self.z
        self.scale = scale
        self.v = []
        self.vc = np.array
        self.screenV = []
        self.vCoords = []
        self.faces = []
        self.triangles = []

    def draw(self, canvas, zbuffer, camera_pos, camera_rot, width, height, fov, aspect, symbols, near, far, is_rotate=True, phase = 0, view_mode = ""):

        if is_rotate:
            self.rot = sin(phase)*180, cos(phase+4)*180, cos(phase)*180
            self.vc = np.array([plusV(quat_rotation(self.rot, vertex), self.pos) for vertex in self.v], dtype = np.float32)
        else:
            self.vc = np.array([plusV(quat_rotation(self.rot, vertex), self.pos) for vertex in self.v], dtype = np.float32)

        scanline(self.triangles, self.vc, zbuffer, canvas, width, height, symbols, 150, camera_pos, camera_rot, fov, aspect)

        # if view_mode.lower() == "d":
        #     for i in self.vc:
        #         coord = to_viewport(camera_pos, camera_rot, i, fov, aspect, 10, 100, width, height)
        #         canvas[coord[1] * width + coord[0]] = "@"

class Cube(shape):
    def __init__(self, rotation, position, scale):
        super().__init__(rotation, position, scale)
        self.v = [[-self.scale, -self.scale, -self.scale],
                [self.scale, -self.scale, -self.scale],
                [self.scale, self.scale, -self.scale],
                [-self.scale, self.scale, -self.scale],
                [-self.scale, -self.scale, self.scale],
                [self.scale, -self.scale, self.scale],
                [self.scale, self.scale, self.scale],
                [-self.scale, self.scale, self.scale]]

        self.faces = [[0, 1, 2, 3],
                    [4, 7, 6, 5],
                    [0, 3, 7, 4],
                    [1, 5, 6, 2],
                    [3, 2, 6, 7],
                    [0, 4, 5, 1]]

        self.triangles = ear_clipping(self.faces, self.v)

class Pyramide(shape):
    def __init__(self, rotation, position, scale):
        super().__init__(rotation, position, scale)
        self.v = [[-self.scale, -self.scale, -self.scale],
                [self.scale, -self.scale, -self.scale],
                [self.scale, self.scale, -self.scale],
                [-self.scale, self.scale, -self.scale],
                [0, 0, self.scale]]

        self.faces = [[0, 1, 2, 3],
                    [1, 0, 4],
                    [2, 1, 4],
                    [3, 2, 4],
                    [0, 3, 4]]


        self.triangles = ear_clipping(self.faces, self.v)

class Sphere(shape):
    def __init__(self, rotation, position, scale, segments):
        super().__init__(rotation, position, scale)
        self.stacks = segments
        self.faces = []

        self.v = []

        for theta in range(self.stacks):
            for phi in range(self.stacks):
                self.v.append([scale * (sin(pi * (theta / (self.stacks-1))) * cos((2 * pi) * (phi / (self.stacks-1)))),
                        scale * (sin(pi * (theta / (self.stacks-1))) * sin((2 * pi) * (phi / (self.stacks-1)))),
                        scale * cos(pi * (theta / (self.stacks-1)))])

        for i in range(1, self.stacks):
            for j in range(self.stacks):
                stack = i * self.stacks
                prev_stack = (i - 1) * self.stacks
                prev_j = (j - 1) % self.stacks

                self.faces.append([stack + j, 
                                   stack + prev_j, 
                                   prev_stack + prev_j, 
                                   prev_stack + j])


        self.triangles = ear_clipping(self.faces, self.v)

class Cylinder(shape):
    def __init__(self, rotation, position, scale, segments):
        super().__init__(rotation, position, scale)
        self.stacks = segments
        self.faces = []
        self.v = []

        for height_multiplier in range(-1, 3, 2):
            for phi in range(self.stacks):
                self.v.append([scale/2 * sin(pi * 2 * (phi / (self.stacks-1))),
                        scale/2 * cos(pi * 2 * (phi / (self.stacks-1))),
                        scale * height_multiplier])

        for i in range(0, 2):
            if i == 0: self.faces.append([j for j in range(self.stacks-1, 0, -1)])
            else: self.faces.append([self.stacks + j for j in range(0, self.stacks-1)])

        for j in range(self.stacks):
            self.faces.append([(j-1) % self.stacks,
                                j,
                                j + self.stacks,
                                (j-1) % self.stacks + self.stacks
                                ])

        print(len(self.faces[0]))

        self.triangles = ear_clipping(self.faces, self.v)