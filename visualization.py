import pygame as pg
#import sys


def transform_coordinate(scrx,scry,scale,x_input, y_input,camera_object) : #The origin will be at the middle of the base. So  (0,0) -> (screenx/2,screeny)
    return (int(x_input*scale + scrx//2)-camera_object.camx, int(scry-y_input*scale)-camera_object.camy) #this is world coordinate.
def node_position_list(sx,sy,sc,nodes,camera_object) : #ran out of names
    node_dictionary = {}
    for i in range(0,len(nodes)) : 
        node_dictionary[i] = transform_coordinate(sx,sy,sc,*nodes[i],camera_object)
    return node_dictionary

def hsv_to_rgb(h, s, v): #formula is available online
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return (r + m, g + m, b + m)

def bar_colour(stress_input_list,count_index,UTS) : 
    # stress or strain / cross section area -> compare with ultimate strength. For steel, stress is approximately equal to strain.
    stress = stress_input_list[count_index]
    r = abs(stress/UTS[count_index])
    if r >1.5 : r = 1.5
    t = r**2 #non-linear mapping
    if r <= 1.0:
            # xanh (220) → đỏ (0)
            h = 220 * (1 - t)
            # saturation tăng dần
            s = 0.7 + 0.3 * t
            # giữ sáng
            v = 1.0

    else:
        # fail → tím
        h = 280
        s = 1.0
        # fade out
        beta = 1.5
        v = max(0.3, 1.0 - beta * (r - 1.0))
    rgb = hsv_to_rgb(h,s,v)
    true_rgb = tuple(int(c * 255) for c in rgb)
    return true_rgb

def draw_structure(scr,dict, connect,stress,UTS) : 
    count = 0 
    for individual_connections in connect:
        #print(individual_connections[0], 'position : ',dict[individual_connections[0]] , individual_connections[1], 'position : ',dict[individual_connections[1]])
        pg.draw.line(scr, bar_colour(stress, count, UTS), dict[individual_connections[0]], dict[individual_connections[1]], 3)
        count += 1
    for individual_node in dict : 
        pg.draw.circle(scr,'red',dict[individual_node],5, width = 0) #pygame.draw.circle(surface, color, center, radius, width=0)

#note for visualization : đã có stress sẵn tương ứng với từng bar trong list.


    
#At idle spawning point, px = 300, py = 600
