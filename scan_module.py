from time import sleep
import math
import pyproj
import json

from cameraDriver import moveCameraDriver 

class scanModule:
    def __init__(self):
        self.camera = moveCameraDriver()

    def parse_json(self, json_file):
        """load a json file"""
        with open(json_file, 'r') as file:
            data = json.load(file)
        return data
        

    def calc_camera_to_target_rotation_by_gps(self, camera_coord,target_coord):
        """"move camera to focus on target location"""
        geodesic = pyproj.Geod(ellps='WGS84')
        pan,_,distance = geodesic.inv(camera_coord[1], camera_coord[0], target_coord[1], target_coord[0])
        tilt = math.degrees(math.atan2(target_coord[2]-camera_coord[2],distance))
        return pan,tilt  

            
    def auto_zoom(self, x_min, y_min, x_max, y_max, w, h, thresh):
        bbx_area = (x_max-x_min)*(y_max-y_min)
        image_area = w*h
        bbx_area_ratio = bbx_area/image_area
        eps=0.1
        while abs(bbx_area_ratio - thresh)>eps:
            if bbx_area_ratio > thresh: #zoom  out
                zoom_factor=thresh-bbx_area_ratio
            else: #zoom in
                zoom_factor=bbx_area_ratio-thresh

            self.camera.step_zoom(zoom_factor)
            #get json_ai
            #get x_min, y_min, x_max, y_max
            #re calculate bbx from new json data
            x_min    = image_cord["x_min"]
            center_y    = image_cord["y_min"]
            h           = image_cord["x_max"]
            w           = image_cord["y_max"]
            bbx_area = (x_min, y_min, x_max, y_max)
            bbx_area_ratio = bbx_area / image_area


    def locking_on_target(self, center_x, center_y, h, w):
        MINIMAL_MOVE=5
        eps=2
        cross_x,cross_y = w/2, h/2
        pix_w,pix_h= cross_x-center_x, cross_y-center_y
        prev_x,prev_y=center_x, center_y
        ##get json_ai .put timeout 
        # center_x, center_y= json.data[0,1]

        pixels_per_angle_x, pixels_per_angle_y=5,5
        while abs(center_x-cross_x)>eps or abs((center_y-cross_y)>eps):
            print(center_x,center_y)
            print(pixels_per_angle_x, pixels_per_angle_y)
            pix_w,pix_h=cross_x-center_x, cross_y-center_y
            print("move_x",pix_w,"move_y",pix_h)
            prev_x,prev_y=center_x, center_y
            if(pix_w <=10 and pix_h<=10):
                break
            if (abs(pix_w) >10):
                pan = self.camera.get_anglePan() + (-pix_w/pix_w)*pixels_per_angle_x
                center_x -= 5
                dif_x=center_x-prev_x
                if dif_x!=0:
                    pixels_per_angle_x=dif_x/pixels_per_angle_x
            else:
                pan=self.camera.get_anglePan()
            if (abs(pix_h) >10):
                tilt = self.camera.get_angleTilt() + (pix_h/pix_h)*pixels_per_angle_y
                center_y += 5
                dif_y=center_y-prev_y
                if dif_y!=0:
                    pixels_per_angle_y=dif_y/pixels_per_angle_y
            else:
                tilt=self.camera.get_angleTilt()
                
            self.camera.move(pan, tilt)
            #get json_ai... if not get-exit and re-scan
            # center_x, center_y= json.data[0,1]
            print(center_x-prev_x,center_y-prev_y)



    def scan_alg(self, target_coord):
        """ drone scanning algorithm
        1) get gps location from sdr
        2) calculate camera rotation and move camera
        3) zoom in continuously until yolo model detect object
            3.1 lock on target iteratively
        Args:
            target_coord : gps coordinates of target object (from sdr)
        """

        camera_coord = [32.158901, 34.802920, 0.0]
        pan,tilt=self.calc_camera_to_target_rotation_by_gps(camera_coord,target_coord)
        self.camera.move(pan,tilt)

        print(f"pan: {pan} tilt: {tilt}")
        #set zoom to zero4
        self.camera.set_zoom(0)


        while True:
            print(self.camera.get_zoom())
            while self.camera.get_zoom() < 1:
                self.camera.step_zoom(0.1)
                sleep(5)
                ##try to get json_ai
                # center_x    = image_cord["center_x"]
                # center_y    = image_cord["center_y"]
                # h           = image_cord["height"]
                # w           = image_cord["width"]

                # center_x, center_y, h, w=[400,200,500,500]
                ##if get_json_ai succeeded go to locking
                # self.locking_on_target(center_x, center_y, h, w)
            self.camera.set_zoom(0)

    # pan: 82.46763098664051 tilt: 0.9530980278179486
    def test_camera(self):
        self.camera.move(82.46763098664051,0.9530980278179486)
        