
from scan_module import scanModule
from server_sdp import ApiLocations
import time


if __name__ == '__main__':
    
    sdr=False
    # servers initialization
    # sdr_server = ApiLocations(5678)
    # print("hi")
    yolo_server= ApiLocations(9876)    

    if sdr: ## get from sdr target location
        sdrRecv = yolo_server.getSDR_data() 
        target_long,target_lat,target_alt =  sdrRecv["longitude"],sdrRecv["latitude"],sdrRecv["altitude"]
    else:# mock a target location
        target_long,target_lat,target_alt=34.835130,31.963857,30

    cam_long,cam_lat,cam_alt=34.8357706,31.9639699,0
    scan = scanModule(yolo_server,cam_long,cam_lat,cam_alt)
    while True:
        time.sleep(0.5)
        print(scan.get_msg())
    
    
    # scan.scan_alg(target_long,target_lat,target_alt)
    
