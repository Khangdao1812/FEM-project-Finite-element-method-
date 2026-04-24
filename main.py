import numpy as np
import pygame as pg
import copy as cp
from solver import solve_truss
from visualization import draw_structure, node_position_list,bar_colour
from camera import Camera_class
import time
#connections = [(index node1, index node 2, A,E)]


#############################
A1,E1 = 1e-4,200e9 #m^2, Pa
# ===============================
nodes = [(-1,0),(0,0),(1,0), (-1,2),(0,2),(1,2), (-1,4),(0,4),(1,4), (-1,6),(0,6),(1,6)]
connections = [(0,3,A1,E1,4e8),(3,6,A1,E1,4e8),(6,9,A1,E1,4e8),(1,4,A1,E1,4e8),(4,7,A1,E1,4e8),(7,10,A1,E1,4e8),(2,5,A1,E1,4e8),(5,8,A1,E1,4e8),(8,11,A1,E1,4e8),(0,1,A1,E1,4e8),(1,2,A1,E1,4e8),(3,4,A1,E1,4e8),(4,5,A1,E1,4e8),(6,7,A1,E1,4e8),(7,8,A1,E1,4e8),(9,10,A1,E1,4e8),(10,11,A1,E1,4e8),(0,4,A1,E1,4e8),(4,2,A1,E1,4e8),(3,7,A1,E1,4e8),(7,5,A1,E1,4e8),(6,10,A1,E1,4e8),(10,8,A1,E1,4e8)]
free_nodes = [(-1,2),(0,2),(1,2), (-1,4),(0,4),(1,4), (-1,6),(0,6),(1,6)]
F_raw = [(0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0)]
F = np.array(F_raw)
F = F.flatten()
speed = 0.1
#=================================

#u_global,reaction,axial_list,stress,UTS = solve_truss(nodes, free_nodes,connections,np.array([(0,0) for _ in range(len(nodes))])) ###exports raw data

def compute_scale(nodes, u):
    nodes = np.array(nodes) #turns array -> vectors, preserve the structure
    U = u.reshape(len(nodes), 2) #reshape into a list length n, 2 columns
    max_disp = np.max(np.linalg.norm(U, axis=1)) #.norm calculates the length of vector, axis =1 means do it for each row [x,y]
    xmin, ymin = nodes.min(axis=0) #axis = 0 means working vertically each time, and it also does this for very column.
    xmax, ymax = nodes.max(axis=0)
    L = max(xmax - xmin, ymax - ymin)
    #scale = 1.0
    render_position = nodes + U #vector operation
    return [tuple(pos) for pos in render_position], max_disp/L #[tuple(pos) for pos in render_position]

def find_failure(bars,stress,UTS) : 
    failed = False
    for k in range(len(stress)-1,-1,-1) : 
        if abs(stress[k])>1.06*UTS[k] : 
            #print('failed at ', k)
            bars.pop(k)
            failed = True
    return failed


def draw_structure_debug(scr, dict, connect, stress, UTS):
    count = 0 
    for individual_connections in connect:
        print(individual_connections[0], 'position : ', dict[individual_connections[0]],
              individual_connections[1], 'position : ', dict[individual_connections[1]])
        count += 1
        if not (individual_connections[0] == 2 and individual_connections[1]==5 ): 
            pg.draw.line(scr,'blue',dict[individual_connections[0]],dict[individual_connections[1]],3)
        else : 
            pg.draw.line(scr,'red',dict[individual_connections[0]],dict[individual_connections[1]],3)
        # 👇 THÊM 2 DÒNG NÀY
        pg.display.update()
        time.sleep(0.5)   # chỉnh số này (0.05 → nhanh, 0.3 → chậm)

    for individual_node in dict:
        pg.draw.circle(scr, 'red', dict[individual_node], 5, width=0)

    # 👇 update lần cuối để hiện node
    pg.display.update()


def simulate(nodes,free_nodes,truss,force,playback_speed,camera_object):
    pg.init()
    screenx, screeny = 800, 600
    clock = pg.time.Clock()
    screen = pg.display.set_mode((screenx, screeny))
    pg.display.set_caption("Truss game")
    scale = 50
    running = True

    timer = 0
    fixed_dt = 1/20
    force_scale = 0

    u_global, reaction, axial_list, stress, UTS = solve_truss(nodes, free_nodes, truss, force*0)
    real_displaced_position,displacement_ratio = compute_scale(nodes, u_global)
    position_dictionary_real = node_position_list(screenx, screeny, scale, real_displaced_position,camera_object) #convert world -> screen)

    collapsed = False

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    collapsed = False
                    truss = cp.deepcopy(connections)
                    u_global, reaction, axial_list, stress, UTS = solve_truss(nodes, free_nodes, truss, force*0)
                    real_displaced_position, displacement_ratio = compute_scale(nodes, u_global)
                    position_dictionary_real = node_position_list(screenx, screeny, scale, real_displaced_position,camera_object)
                    timer = 0
                    force_scale = 0
            camera_object.handle_clicking(event)
        camera_object.update_camera()
        screen.fill((0, 0, 0))

        if not collapsed:
            prev_truss = cp.deepcopy(truss)
            prev_real_displaced_position = real_displaced_position.copy()
            prev_stress = stress.copy()
            prev_UTS = UTS
            timer += 0.0125
            force_scale += playback_speed * 0.0167
            force_scale = min(1, force_scale)
            if timer > fixed_dt:
                timer = 0
                F_t = force * force_scale

                while True:
                    try:
                        u_global, reaction, axial_list, stress, UTS = solve_truss(nodes, free_nodes, truss, F_t)
                    except:
                        print("STRUCTURE HAS COLLAPSED")
                        collapsed = True
                        break
                    if not find_failure(truss, stress, UTS):
                        break

                if not collapsed:
                    real_displaced_position,displacement_ratio = compute_scale(nodes, u_global)
                    if displacement_ratio>0.2 :
                        print("STRUCTURE HAS COLLAPSED")
                        collapsed = True
                        # Additional checking

        #----------------------------- Always draw------------------
        if not collapsed : 
            position_dictionary_real = node_position_list(screenx, screeny, scale, real_displaced_position,camera_object)
            draw_structure(screen, position_dictionary_real, truss, stress, UTS)
        else : 
            position_dictionary_real = node_position_list(screenx, screeny, scale, prev_real_displaced_position,camera_object)
            #The only thing changing in the line above is the camera object. prev_real_displaced_position remains the same as it is
            # in the fixed reference system. We are only moving the camera. So always reuse the data from the fixed reference system +
            # modify position on screen by camera object.
            draw_structure(screen,position_dictionary_real,prev_truss,prev_stress,prev_UTS)
            #since position dictionary reflects the coordinate on screen, we have to update it. truss, stress, UTS, displaced_position
            #belongs to the fixed reference frame.
        #print(real_displaced_position)
        #print(player.camx,player.camy)
        print(truss)
        print('--------------------------')
        print(connections)
        print('#########################################')
        pg.display.flip()
        clock.tick(60)

    pg.quit()

player = Camera_class(90.73999999999961,-57.42000000000023,1)
simulate(cp.deepcopy(nodes),cp.deepcopy(free_nodes),cp.deepcopy(connections),cp.deepcopy(F),speed,player)
# k : N/m, displacement : m, stress = Pa, internal force : N, strain has no unit, x,y : m.