from djitellopy import Tello

class TelloKeyboardController:
    def __init__(self, tello: Tello):
        self.tello = tello
        self.in_flight= False

    def control(self, key):
        if key == ord('w'):
            self.tello.move_forward(30)
        elif key == ord('s'):
            self.tello.move_back(30)
        elif key == ord('a'):
            self.tello.move_left(30)
        elif key == ord('d'):
            self.tello.move_right(30)
        elif key == ord('e'):
            self.tello.rotate_clockwise(30)
        elif key == ord('q'):
            self.tello.rotate_counter_clockwise(30)
        elif key == ord('r'):
            self.tello.move_up(30)
        elif key == ord('f'):
            self.tello.move_down(30)
        elif key == ord('u'):
            self.tello.emergency()
        elif key == 32: #Space
            if not self.in_flight:
                self.tello.takeoff()
                self.in_flight=True
            elif self.in_flight:
                self.tello.land()
                self.in_flight=False



