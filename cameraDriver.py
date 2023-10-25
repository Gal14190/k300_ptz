from ptz_control import ptzControl
from time import sleep

class moveCameraDriver :
    def __init__(self):
        self.control = ptzControl()
        self.direction=1

    def mapFromTo(self, x,a,b,c,d):
        y=(x-a)/(b-a)*(d-c)+c
        return y
    
    def move(self, angle_pen, angle_tilt):
        if (angle_tilt>90) and self.direction == 1:
            self.direction = -1
            angle_pen = (self.get_anglePan() + 180) % 360
        elif (angle_tilt<=90) and self.direction == -1:
            self.direction = 1

        if(self.direction < 0):
            position_tilt = self.mapFromTo(angle_tilt, 90, 180, -1, 1)
        else:
            position_tilt = self.mapFromTo(angle_tilt, 0, 90, 1, -1)

        position_pen = self.mapFromTo(angle_pen, 0, 360, 1, -1)
        self.control.move_abspantilt(position_pen, position_tilt, 1)

        self.delay(angle_pen, angle_tilt)

    ###
    # set_zoom
    #   z : set zoom [0:1] 0 - max zoom out, 1 - max zoom in
    ###
    def set_zoom(self, z):
        position = z
        # position = self.mapFromTo(z, 0, 1, -1, 1)
        # print(z,position)
        self.control.zoom_relative(position, 1)

        self.delay(1,1)

    def step_zoom(self, z):
        _position = self.mapFromTo(self.control.get_zoom(), -1, 1, 0, 1)
        _position += z 
        if(_position < -1):
            _position = -1
        elif (_position > 1):
            _position = 1

        self.set_zoom(_position)

        self.delay(1,1)
        
    def get_angleTilt(self):
        return self.mapFromTo(self.control.get_position().y, 1, -1, 0, 90)
    
    def get_anglePan(self):
        return self.mapFromTo(self.control.get_position().x, 1, -1, 0, 360)
    
    def get_zoom(self):
        # print(f"zoom : {self.control.get_zoom()}")
        # return self.mapFromTo(self.control.get_zoom(), 0, 1, -1, 1)
        return self.control.get_zoom()
    
    def delay(self, pen, tilt):
        s = 0
        m = max(abs(self.get_anglePan() - pen), abs(self.get_angleTilt() - tilt))

        if(m <= 180):
            s = self.mapFromTo(m, 0, 180, 0, 2)
        elif(m > 180):
            s = self.mapFromTo(m - 180, 0, 180, 0, 2)

        sleep(s)

    def get_status(self):
        return self.control.get_status()
        
    
