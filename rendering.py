from math import sin, cos, tan, radians, sinh
from math_functions import *

def make_gradient(alpha, string, invert_alpha = False):
    a = max(min((alpha if invert_alpha == False else alpha * -1 + 1), 1), 0)
    return string[round(a * (len(string) - 1))]



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
    zv = dot(forward, point) - dot(forward, eye)

    f = 1/tan(radians(fov)/2)

    xc = f/aspect * xv
    yc = f * yv
    zc = ((far+near)/(near-far) * zv + ((2*far*near)/(near-far)))
    wc = -zv

    if wc == 0: x_ndc, y_ndc, z_ndc = 0, 0, 0
    else: x_ndc, y_ndc, z_ndc = xc / wc, yc / wc, zc / wc
        
    W, H = width, height

    x_scr, y_scr, z = 0.0, 0.0, 0.0

    x_scr = round((0.5 + (x_ndc*aspect)) * W if wc != 0 else 0) 
    y_scr = round((0.5 - (y_ndc * -1)) * H if wc != 0 else 0)

    z = zv

    return x_scr, y_scr, z, wc

def ear_clipping(faces, verteces):
    reflex, convex, indeces = [], [], []

    for face in faces:

        n = len(face)

        triangle_v = [verteces[index] for index in face]

        nx = sum([(triangle_v[i][1] - triangle_v[(i+1) % n][1]) * (triangle_v[i][2] + triangle_v[(i+1) % n][2]) for i in range(n)])
        ny = sum([(triangle_v[i][2] - triangle_v[(i+1) % n][2]) * (triangle_v[i][0] + triangle_v[(i+1) % n][0]) for i in range(n)])
        nz = sum([(triangle_v[i][0] - triangle_v[(i+1) % n][0]) * (triangle_v[i][1] + triangle_v[(i+1) % n][1]) for i in range(n)])

        N = normalize((nx, ny, nz))
        active_indexes = face.copy()
        
        i = 0
        
        while len(active_indexes) > 3:
            n = len(active_indexes)
            i %= n

            curr = active_indexes[i]
            prev = active_indexes[(i - 1) % n]
            next = active_indexes[(i + 1) % n]

            curr_p = verteces[curr]
            prev_p = verteces[prev]
            next_p = verteces[next]

            av = minusV(curr_p, prev_p)
            bv = minusV(next_p, curr_p)

            D = dot(cross(av, bv), N)
            
            if D > 0: 
                convex.append(curr) 
            else:
                reflex.append(curr)
                break

            A, B, C, is_ear = prev_p, curr_p, next_p, True

            for P in reflex:
                d1 = dot(cross(minusV(B, A),  minusV(P, A)), N)
                d2 = dot(cross(minusV(C, B),  minusV(P, B)), N)
                d3 = dot(cross(minusV(A, C),  minusV(P, C)), N)

                if d1 >= 0 and d2 >= 0 and d3 >= 0: 
                    is_ear = False
                    break

            if is_ear:
                active_indexes.pop(i)
                indeces.append([prev, curr, next])
                i -= 1
            else:
                i += 1
                
        indeces.append(active_indexes)
        
    return indeces

def scanline(triangles, verteces, zbuffer, canvas, width, height, symbols, zblackout, camera_pos, camera_rot, fov, aspect):
    window_size = width*height
    for triangle in triangles:
        verteces_2D = [to_viewport(camera_pos, camera_rot, verteces[index], fov, aspect, 10, 100, width, height) 
                    for index in triangle]
        
        triangle_3D = [verteces[index] for index in triangle]

        normal = triangle_normal(triangle_3D)

        if dot(unit_direction(triangle_3D[0], camera_pos), normal) >= 0:
        
            if verteces_2D[0][3] > 0 or verteces_2D[1][3] > 0 or verteces_2D[2][3] > 0: continue
            
            points = sorted([p for p in verteces_2D], key = lambda x: x[1])

            p0, p1, p2 = points

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
                if fb_y >= height or fb_y <= 0: continue

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
                    if fb_x <= 0 or fb_x >= width: continue

                    right_left_x_ratio = (rx - lx)
                    h = ((fb_x - lx) / right_left_x_ratio) if right_left_x_ratio != 0 else 0
                    Z_pixel = lz + h * (rz - lz)

                    scr_coords = fb_y * width + fb_x

                    if Z_pixel < zbuffer[scr_coords]:
                        zbuffer[scr_coords] = Z_pixel
                        canvas[scr_coords] = make_gradient(Z_pixel / zblackout, symbols)

            y_start = right_base[1]
            y_end = p2[1]

            for ft_y in range(y_start, y_end):
                if ft_y >= height or ft_y <= 0: continue

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
                    if ft_x <= 0 or ft_x >= width: continue

                    right_left_x_ratio = (rx - lx)
                    h = ((ft_x - lx) / right_left_x_ratio) if right_left_x_ratio != 0 else 0
                    Z_pixel = lz + h * (rz - lz)
                    
                    scr_coords = ft_y * width + ft_x

                    if ft_x > 0 and ft_x < window_size:
                        if Z_pixel < zbuffer[scr_coords]:
                            zbuffer[scr_coords] = Z_pixel
                            canvas[scr_coords] = make_gradient(Z_pixel / zblackout, symbols)