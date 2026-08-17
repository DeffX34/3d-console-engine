from math import sin, cos, tan, radians
from math_functions import *

def to_viewport(eye, camera_rot, point, fov, aspect, near, far, width, height):
    worldUp = (0, 0, 1)
    radians_rot = rad_rotation(camera_rot)

    yaw, pitch = radians_rot[1], radians_rot[2]
    
    rx = cos(pitch) * cos(yaw)
    ry = cos(pitch) * sin(yaw)
    rz = sin(pitch)
    
    forward = normalize((rx, ry, rz))
    right = normalize(cross(forward, worldUp))
    up = normalize(cross(right, forward))

    xv = dot(right, point) - dot(right, eye)
    yv = dot(up, point) - dot(up, eye)
    zv = dot((forward[0], forward[1], forward[2]), point) - dot(forward, eye)

    f = 1/tan(radians(fov)/2)

    xc = f/aspect * xv
    yc = f * yv
    zc = ((far+near)/(near-far) * zv + ((2*far*near)/(near-far)))
    wc = -zv

    if wc == 0: x_ndc, y_ndc, z_ndc = 0, 0, 0
    else: x_ndc, y_ndc, z_ndc = xc / wc, yc / wc, zc / wc
        
    W, H = width*aspect, height

    x_scr, y_scr, z = 0.0, 0.0, 0.0

    x_scr = round((0.5/aspect + x_ndc) * W if wc != 0 else 0) 
    y_scr = round((0.5 - y_ndc) * H if wc != 0 else 0)

    z = zv

    return x_scr, y_scr, z, wc

def ear_clipping(faces):
    reflex, convex, indeces = [], [], []

    for face in faces:
        n = len(face)

        nx = sum([(face[i][1] - face[(i+1) % n][1]) * (face[i][2] + face[(i+1) % n][2]) for i in range(n)])
        ny = sum([(face[i][2] - face[(i+1) % n][2]) * (face[i][0] + face[(i+1) % n][0]) for i in range(n)])
        nz = sum([(face[i][0] - face[(i+1) % n][0]) * (face[i][1] + face[(i+1) % n][1]) for i in range(n)])

        N = normalize((nx, ny, nz))

        active_indexes = face.copy()

        for k in range(n):
            if len(active_indexes) > 3:

                curr = active_indexes[k]
                prev = active_indexes[(k - 1) % n]
                next = active_indexes[(k + 1) % n]

                av = minusV(curr, prev)
                bv = minusV(next, curr)

                C = cross(av, bv)
                D = dot(C, N)
                
                if D > 0: 
                    convex.append(curr) 
                
                else: 
                    reflex.append(curr)
                    break

                A = prev
                B = curr
                C = next

                is_ear = True

                if reflex:
                    for P in reflex:
                        c1 = cross(minusV(B, A),  minusV(P, A))
                        c2 = cross(minusV(C, B),  minusV(P, B))
                        c3 = cross(minusV(A, C),  minusV(P, C))

                        k1 = dot(c1, N)
                        k2 = dot(c2, N)
                        k3 = dot(c3, N)

                        if k1 >= 0 and k2 >= 0 and k3 >= 0: is_ear = False

                if is_ear: 

                    active_indexes.remove(curr)
                    indeces.append([prev, curr, next])
                    
            else: 

                indeces.append(active_indexes)
                break

    return indeces

def scanline(triangles, zbuffer, canvas, width, height, symbols, zblackout):
    window_size = len(canvas)
    for triangle in triangles:
        if triangle[0][3] >= 0 or triangle[1][3] >= 0 or triangle[2][3] >= 0: continue
        
        p0 = min(triangle, key=lambda x: x[1])
        p2 = max(triangle, key=lambda x: x[1])

        for p in triangle:
            if p != p0 and p != p2:
                p1 = p
                break

        top_bottom_diff = p2[1] - p0[1]

        t = ((p1[1] - p0[1]) / (top_bottom_diff)) if top_bottom_diff != 0 else 0

        DX = p0[0] + t * (p2[0] - p0[0])
        DY = p1[1]
        DZ = p0[2] + t * (p2[2] - p0[2])

        left_base = p1[0]
        right_base = DX

        if DX > p1[0]:
            left_base = p1[0], p1[1], p1[2]
            right_base = DX, DY, DZ
        else:
            left_base = DX, DY, DZ
            right_base = p1[0], p1[1], p1[2]

        y_start = p0[1]
        y_end = right_base[1]

        for fb_y in range(y_start, y_end):
            if fb_y < 0 or fb_y > height: continue

            middle_top_diff = p1[1] - p0[1]
            flat_bottom_t = ((fb_y - p0[1]) / middle_top_diff) if middle_top_diff != 0 else 0

            lx = round(p0[0] + flat_bottom_t * (left_base[0] - p0[0]))
            rx = round(p0[0] + flat_bottom_t * (right_base[0] - p0[0]))
        
            lz = p0[2] + flat_bottom_t * (left_base[2] - p0[2])
            rz = p0[2] + flat_bottom_t * (right_base[2] - p0[2])

            if lx > rx:
                x_start = rx
                x_end = lx
            else:
                x_start = lx
                x_end = rx

            for fb_x in range(x_start, x_end):
                right_left_x_ratio = (rx - lx)
                h = ((fb_x - lx) / right_left_x_ratio) if right_left_x_ratio != 0 else 0
                Z_pixel = lz + h * (rz - lz)

                scr_coords = fb_y * width + fb_x

                if fb_x > 0 and fb_x < width and scr_coords < window_size and scr_coords > 0 and Z_pixel < zbuffer[scr_coords]:

                    zbuffer[scr_coords] = Z_pixel
                    canvas[scr_coords] = symbols[round((min(max(Z_pixel/zblackout, 0), 1))*(len(symbols)-1))]

        y_start = right_base[1]
        y_end = p2[1]

        for ft_y in range(y_start, y_end):

            if ft_y < 0 or ft_y > height: continue

            middle_bottom_diff = p2[1] - p1[1]

            flat_top_t = ((ft_y - p1[1]) / middle_bottom_diff) if middle_bottom_diff != 0 else 0

            lx = round(left_base[0] + flat_top_t * (p2[0] - left_base[0]))
            rx = round(right_base[0] + flat_top_t * (p2[0] - right_base[0]))

            lz = left_base[2] + flat_top_t * (p2[2] - left_base[2])
            rz = right_base[2] + flat_top_t * (p2[2] - right_base[2])

            if lx > rx:
                x_start = rx
                x_end = lx
            else:
                x_start = lx
                x_end = rx

            for ft_x in range(x_start, x_end):
                right_left_x_ratio = (rx - lx)
                h = ((ft_x - lx) / right_left_x_ratio) if right_left_x_ratio != 0 else 0
                Z_pixel = lz + h * (rz - lz)

                scr_coords = ft_y * width + ft_x

                if ft_x > 0 and ft_x < width and scr_coords < window_size and scr_coords > 0 and Z_pixel < zbuffer[scr_coords]:
                    zbuffer[scr_coords] = Z_pixel
                    canvas[scr_coords] = symbols[round((min(max(Z_pixel/zblackout, 0), 1))*(len(symbols)-1))]