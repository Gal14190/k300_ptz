from time import sleep
import math
import pyproj
import json

from cameraDriver import moveCameraDriver


class scanModule:
    def __init__(self,server_yolo ,camera_cord_long,camera_cord_lat, camera_altitude):
        # self.camera = moveCameraDriver()
        self.server_yolo=server_yolo
        self.camera_cord_lat = camera_cord_lat
        self.camera_cord_long = camera_cord_long 
        self.camera_altitude = camera_altitude
        # self.camera.move(0,0)
        sleep(3)
        
    def get_coords(img):
        x_min = img["x_min"]
        y_min = img["y_min"]
        x_max = img["x_max"]
        y_max = img["y_max"]
        return x_min,y_min,x_max,y_max
    
    def get_center_object(image_cord):
        return image_cord['center_x'],image_cord['center_y']

    def calc_camera_to_target_rotation_by_gps(self, target_long, target_lat, target_alt):
        """"move camera to focus on target location"""
        geodesic = pyproj.Geod(ellps='WGS84')
        pan,_,distance = geodesic.inv( self.camera_cord_long, self.camera_cord_lat,target_long, target_lat)
        tilt = math.degrees(math.atan2(target_alt-self.camera_altitude,distance))

        if pan < 0:
            pan += 360
        print("rotate camera to:",pan, tilt)
        return pan,tilt  

    def auto_zoom(self, x_min, y_min, x_max, y_max, w, h, thresh):
        bbx_area = (x_max - x_min) * (y_max - y_min)
        image_area = w * h
        bbx_area_ratio = bbx_area / image_area
        eps = 0.1
        while abs(bbx_area_ratio - thresh) > eps:
            if bbx_area_ratio > thresh:  # zoom  out
                zoom_factor = thresh - bbx_area_ratio
            else:  # zoom in
                zoom_factor = bbx_area_ratio - thresh

            self.camera.step_zoom(zoom_factor)
            sleep(1)
            image_cord = self.get_detection()
            if image_cord is None:
                return True ## reset scanning
            x_min,y_min,x_max,y_max=self.get_coords(image_cord)

            bbx_area = (x_min, y_min, x_max, y_max)
            bbx_area_ratio = bbx_area / image_area
            

    def get_detection(self):
        image_cord=self.server_yolo.getYOLO_data()
        count_not_found=0
        while image_cord["yolo_detection"] == False:
            image_cord=self.server_yolo.getYOLO_data()
            count_not_found+=1
        ## object detection not found for some duration -> zoom out & start again. 
            if count_not_found==10:
                return None
        return image_cord

    def locking_on_target(self, center_x, center_y, h, w):
        reset=False
        eps = 10
        cross_x, cross_y = w / 2, h / 2

        angle_per_pixel_x, angle_per_pixel_y = (
            1 / 40,
            1 / 40,
        )  # move 1 degree for each 40 pixels
        while not reset:
            pix_w, pix_h = center_x - cross_x, cross_y - center_y
            print("object location:", center_x, center_y)
            print("move_x", pix_w, "move_y", pix_h)
            print("camera pan tilt move:", angle_per_pixel_x, angle_per_pixel_x)

            if abs(pix_w) > eps:
                pan = self.camera.get_anglePan() + (pix_w * angle_per_pixel_x)
            else:
                pan = self.camera.get_anglePan()

            if abs(pix_h) > eps:
                tilt = self.camera.get_angleTilt() + (pix_h * angle_per_pixel_y)
            else:
                tilt = self.camera.get_angleTilt()

            self.camera.move(pan, tilt)
            ## save current object position
            prev_x, prev_y = center_x, center_y
            ## get new frame detection
            
            image_cord = self.get_detection()
            if image_cord is None:
                return True ## reset scanning
                    
            center_x,center_y=self.get_center_object(image_cord)
            
            ##calculate difference movement between 2 frames
            dif_x, dif_y = (
                prev_x - center_x,
                prev_y - center_y,
            ) 
            ##calculate how much pixels moved by pixels_per_angle_y angles
            if dif_x != 0:
                angle_per_pixel_x = (pix_w * angle_per_pixel_x) / dif_x
            else:
                angle_per_pixel_x *= 4
            if dif_y != 0:
                angle_per_pixel_y = (pix_h * angle_per_pixel_y) / dif_y
            else:
                angle_per_pixel_y *= 4
            ## calculate distance between target and cross
            pix_w, pix_h = center_x - cross_x, cross_y - center_y
        

    def scan_alg(self,target_long, target_lat, target_alt):
        """drone scanning algorithm
        1) get gps location from sdr
        2) calculate camera rotation and move camera
        3) zoom in continuously until yolo model detect object
            3.1 lock on target iteratively
        Args:
            target_coord : gps coordinates of target object (from sdr)
        """
        print("Scanning")
        ## rotate camera according sdr coordinates detection
        pan, tilt = self.calc_camera_to_target_rotation_by_gps(target_long, target_lat, target_alt)
        self.camera.move(pan, tilt)
        print(f"pan: {pan} tilt: {tilt}")
        TARGE_SCREEN_RATIO=1/3
        while True:
            self.camera.set_zoom(0)
            print("start zooming in, zoom=",self.camera.get_zoom())
            while self.camera.get_zoom() < 1:
                self.camera.step_zoom(0.1)
                print("zoon: ",self.camera.get_zoom())
                sleep(1)
                print("try get detection")
                image_cord=self.server_yolo.getYOLO_data()
                if image_cord["yolo_detection"] == False: ## object not found -> zoom in
                    continue
                #object found -> start locking on it
                x_min,y_min,x_max,y_max=self.get_coords(image_cord)
                h,w=image_cord["height"],image_cord["width"]
                reset_scanning=self.auto_zoom(x_min,y_min,x_max,y_max,w,h,TARGE_SCREEN_RATIO)
                ## zoom out and start again
                if reset_scanning==True:
                    break
                center_x, center_y=self.get_center_object(image_cord)
                reset_scanning=self.locking_on_target(center_x, center_y, h, w)
                ## zoom out and start again
                if reset_scanning==True:
                    break
                
                
    def get_msg(self):
        return self.server_yolo.getYOLO_data()