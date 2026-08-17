from math import sin, cos, tan, atan, atan2, pi, radians, degrees, sqrt
import numpy as np

def dot(a, b): return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def rad_rotation(rotation):return radians(rotation[0]), radians(rotation[1]), radians(rotation[2])

def normalize(a):
    length = abs(sqrt(a[0]*a[0] + a[1]*a[1] + a[2]*a[2]))
    return (a[0]/length, a[1]/length, a[2]/length) if length != 0 else (0, 0, 0)

def distance(a, b): return sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2 + (b[2] - a[2])**2)

def cross(a, b): return (a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0])

def plusV(a, b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])

def minusV(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def multV(a, b): return a[0] * b[0], a[1] * b[1], a[2] * b[2]

def divideV(a, b): return a[0] / b[0], a[1] / b[1], a[2] / b[2]

def plusVscalar(a, scalar): return a[0] + scalar, a[1] + scalar, a[2] + scalar

def multVscalar(a, scalar): return a[0]*scalar, a[1]*scalar, a[2]*scalar

def minusV2D(a, b): return a[0]-b[0], a[1]-b[1]

def quat_rotation(xyzAxis, p):
    sx, cx = sin(radians(xyzAxis[0]/2)), cos(radians(xyzAxis[0]/2))
    sy, cy = sin(radians(xyzAxis[1]/2)), cos(radians(xyzAxis[1]/2))
    sz, cz = sin(radians(xyzAxis[2]/2)), cos(radians(xyzAxis[2]/2))

    w = cz*cy*cx + sz*sy*sx
    x = cz*cy*sx - sz*sy*cx
    y = cz*sy*cx + sz*cy*sx
    z = sz*cy*cx - cz*sy*sx

    q = (w, x, y, z)
    v = q[1], q[2], q[3]
    vp = cross(v, p)

    pn = plusV(plusV(p, multVscalar(vp, 2*w)), multVscalar(cross(v, vp), 2))
    return pn

def get_camera_rots(camera_rot):
    worldUp = (0, 0, 1)
    radians_rot = rad_rotation(camera_rot)

    rx = cos(radians_rot[2]) * cos(radians_rot[1])
    ry = cos(radians_rot[2]) * sin(radians_rot[1])
    rz = sin(radians_rot[2])

    forward = normalize((rx, ry, rz))
    right = normalize(cross(forward, worldUp))

    return forward, right