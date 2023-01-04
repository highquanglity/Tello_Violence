from djitellopy import tello
import cv2 as cv

me=tello.Tello()
me.connect()
print(me.get_battery())

me.streamon()
while True:
    img=me.get_frame_read().frame
    cv.imshow("Tello", img)
    cv.waitKey(1)