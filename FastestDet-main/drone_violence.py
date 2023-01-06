import cv2 as cv

from djitellopy import Tello
from gestures.tello_keyboard_controller import TelloKeyboardController

from cvfpscalc import CvFpsCalc
import threading

import torch
from utils.tool import *
from module.detector import Detector
from playsound import playsound




def main():
    #set up model
    global alarm 
    alarm =False
    def sound():
        global alarm
        playsound("violence_sound_1.wav")
        alarm = False
    
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    thresh = 0.8
    cfg = LoadYaml("./mydata.yaml")    
    print(cfg) 
    
    weight='./best.pth'
    print("load weight from:%s"%weight)
    model = Detector(cfg.category_num, True).to(device)
    model.load_state_dict(torch.load(weight, map_location=device))
    #sets the module in eval node
    model.eval()


    #set up drone
    global battery_status
    KEYBOARD_CONTROL=True
    

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
            tello.land()
            break

        
        image=cap.frame
        res_img = cv.resize(image, (cfg.input_width, cfg.input_height), interpolation = cv.INTER_LINEAR) 
        img = res_img.reshape(1, cfg.input_height, cfg.input_width, 3)
        img = torch.from_numpy(img.transpose(0, 3, 1, 2))
        img = img.to(device).float() / 255.0
        
        preds =model(img)
        output=handle_preds(preds, device,thresh)
        LABEL_NAMES = ["violence", "non_violence"]
        H, W, _ = image.shape
        scale_h, scale_w = H / cfg.input_height, W / cfg.input_width
        
        
        for box in output[0]:
            box=box.tolist()
            obj_score = box[4]
            category = LABEL_NAMES[int(box[5])]
            if category==LABEL_NAMES[0]:
                if not alarm:
                    alarm = True
                    threading.Thread(target=sound).start()


            x1, y1 = int(box[0] * W), int(box[1] * H)
            x2, y2 = int(box[2] * W), int(box[3] * H)

            cv.rectangle(image, (x1, y1), (x2, y2), (255, 255, 0), 2)
            cv.putText(image, '%.2f' % obj_score, (x1, y1 - 5), 0, 0.7, (0, 255, 0), 2)	
            cv.putText(image, category, (x1, y1 - 25), 0, 0.7, (0, 255, 0), 2)
            
        
        tello_control(key,keyboard_controler)
        tello_battery(tello)
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
