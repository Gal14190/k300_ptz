import sys
from time import sleep
from cameraDriver import moveCameraDriver
from server_sdp import ApiLocations

if __name__ == '__main__' :
    argv = sys.argv
    argc = len(argv)

    pen = 0
    tilt = 0
    zoom = 0
    if argc > 3:
        pen = int(argv[1])
        tilt = int(argv[2])
        zoom = int(argv[3])

    camera = moveCameraDriver()


    # camera.move(pen, tilt)
    # sleep(2)
    #camera.set_zoom(zoom)
    # camera.step_zoom(-2)

    # print(camera.get_status())
    # camera.set_zoom(-0.7)
    # sleep(5)
    # # camera.get_zoom()
    # print(f"zoom : {camera.control.get_zoom()}")

    # for i in range(-1,1,20):
    #     x = camera.get_zoom()
    #     sleep(1)
    #     camera.set_zoom(i/20)
    #     sleep(5)
    #     # camera.get_zoom()
    #     print(f"zoom : {camera.control.get_zoom()}")

    # print(f'tilt: {camera.get_angleTilt()}, Pan: {camera.get_anglePan()}')