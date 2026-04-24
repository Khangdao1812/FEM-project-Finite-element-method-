import pygame as pg #Nếu gọi get event twice là bị bug do event.type.get() consume toàn bộ event queue

class Camera_class() :
    def __init__(self,camx,camy,zoom) : 
        self.camx = camx
        self.camy = camy
        self.zoom = zoom
        self.dragging = False

    def handle_clicking(self,event) :  #fix để gán biến trực tiếp từ pg trong main
        #print('handling clicking')
        if event.type == pg.MOUSEBUTTONDOWN : 
            if event.button ==1 : 
                self.dragging = True
                self.last_mouse = pg.mouse.get_pos()   
        if event.type == pg.MOUSEBUTTONUP :
            if event.button ==1 : 
                self.dragging = False

    def update_camera(self) :
        if self.dragging :
            self.current_mouse = pg.mouse.get_pos()
            dx = self.current_mouse[0] - self.last_mouse[0]
            dy = self.current_mouse[1] - self.last_mouse[1]
            self.camx -= dx/(self.zoom*50)
            self.camy -= dy/(self.zoom*50)
            self.camy = min(0,self.camy)






#At idle spawning point, px = 300, py = 600