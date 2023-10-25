
from scan_module import scanModule
from server_sdp import ApiLocations

if __name__ == '__main__':
    # sdr connection
    sdr = ApiLocations(5678)
    # wait for client
    while sdr.location_details() == None:
        pass
    sdrRecv = sdr.location_details() 
    print(sdrRecv) 

    #socket to yolo_model
    #socker to sdr
    #socket to camera
    
    #target_coordinate= from sdr_socket
    scan = scanModule()
    target_coordinate = [sdrRecv["latitude"], sdrRecv["longitude"],sdrRecv["altitude"]]
    # scan.test_camera()

    scan.scan_alg(target_coordinate)