from math_functions import *
from math import cos, sin, pi
from rendering import *
import colorama
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
        self.vc = []
        self.screenV = []
        self.vCoords = []
        self.faces = []
        self.triangles = []

    def draw(self, canvas, zbuffer, camera_pos, camera_rot, width, height, fov, aspect, symbols, near, far, is_rotate=True, phase = 0):
        if is_rotate:
            self.rot = sin(phase)*180, cos(phase+4)*180, cos(phase)*180
            self.vc = np.array([[plusV(quat_rotation(self.rot, vertex), self.pos) for vertex in triangle] for triangle in self.triangles])
        else:
            self.vc = np.array([[plusV(quat_rotation(self.rot, vertex), self.pos) for vertex in triangle] for triangle in self.triangles])

        screen_triangles = []
        for triangle_3d in self.vc:
            screen_triangles.append([to_viewport(camera_pos, camera_rot, point, fov, aspect, near, far, width, height) 
                                    for point in triangle_3d])

        # for triangle in screen_triangles:
        #     for point in triangle:
        #         if point[0] > 0 and point[1] > 0 and point[0] < width and point[1] < height and point[2] > 0:
        #             coords = point[1] * width + point[0]
        #             canvas[coords] = symbols[0]

        scanline(screen_triangles, zbuffer, canvas, width, height, symbols, 50)
            
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

        self.faces = [
                [self.v[0], self.v[1], self.v[2], self.v[3]],
                [self.v[4], self.v[7], self.v[6], self.v[5]],
                [self.v[0], self.v[4], self.v[7], self.v[3]],
                [self.v[1], self.v[5], self.v[6], self.v[2]],
                [self.v[3], self.v[2], self.v[6], self.v[7]],
                [self.v[0], self.v[1], self.v[5], self.v[4]]
                ]
        self.triangles = ear_clipping(self.faces)

class Pyramide(shape):
    def __init__(self, rotation, position, scale):
        super().__init__(rotation, position, scale)
        self.v = [[-self.scale, -self.scale, -self.scale],
                [self.scale, -self.scale, -self.scale],
                [self.scale, self.scale, -self.scale],
                [-self.scale, self.scale, -self.scale],
                [0, 0, self.scale]
                ]

        self.faces = [
            # Основание пирамиды (теперь обход по часовой стрелке)
            [self.v[0], self.v[1], self.v[2], self.v[3]],
            
            # 4 боковые грани (теперь обход по часовой стрелке)
            [self.v[1], self.v[0], self.v[4]],  # Передняя грань
            [self.v[2], self.v[1], self.v[4]],  # Правая грань
            [self.v[3], self.v[2], self.v[4]],  # Задняя грань
            [self.v[0], self.v[3], self.v[4]]   # Левая грань
        ]


        self.triangles = ear_clipping(self.faces)