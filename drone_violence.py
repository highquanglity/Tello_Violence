import cv2 as cv

from djitellopy import Tello
from gestures.tello_keyboard_controller import TelloKeyboardController

from utils import CvFpsCalc
import threading



def main():
    global battery_status
    KEYBOARD_CONTROL=True
    in_flight= False

    tello=Tello()
    tello.connect()
    tello.streamon()
    cap= tello.get_frame_read()

    keyboard_controler=TelloKeyboardController(tello)
    def tello_control(key,keyboard_controler):
        keyboard_controler.control(key)
    def tello_battery(tello):
        global battery_status
        try:
            battery_status = tello.get_battery()[:-2]
        except:
            battery_status=-1

    cv_fps_calc=CvFpsCalc(buffer_len=10)
    battery_status=-1
    while True:
        fps=cv_fps_calc.get()
        key=cv.waitKey(1) & 0xff
        if key == 27: #ESC
            break
        elif key == 32: #Space
            if not in_flight:
                tello.takeoff()
                in_flight=True
            elif in_flight:
                tello.land()
                in_flight=False
        
        image=cap.frame
        threading.Thread(target=tello_control, args=(key,keyboard_controler,)).start()
        threading.Thread(target=tello_battery, args=(tello,)).start()
        cv.putText(image, "Battery: {}".format(battery_status), (5, 720 - 5),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv.putText(image, "FPS: {}".format(fps), (5, 100),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv.imshow('Tello',image)
    tello.land()
    tello.end()
    cv.waitKey(0)
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()