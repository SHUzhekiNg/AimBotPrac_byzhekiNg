'''
本例程中，可以将Detect视为所有功能算法的集合；
在Detect.__init__中创建自瞄、小陀螺、能量机关等模式的实例；
因而Detect下每一个模式，条理清晰、可读性强；
动态roi、卡尔曼滤波为实例的一项属性，可以根据不同功能的需求灵活调整；

保留了键位扫描的多线程的优点；

还未加入串口的代码，在keyboard_serial_task下手动设定模式进行测试
ubuntu下请将tkinter和threading相关代码均注释掉
'''


import tkinter
import tkinter.messagebox
import tkinter.filedialog
import argparse
import cv2 as cv
import threading
import platform
import time
from core.mode_chooser import ModeChooser
from config.cap_configs import CapConfig

from core.detect import Detect

def keyboard_serial_task(mode_chooser):
    while True:
        if cv.waitKey(1)=="r":
            mode_chooser.mode_set(mode='armor_rotate')
        else:
            mode_chooser.mode_set(mode='armor_stable')
            #mode_chooser.mode_set(mode='armor_rotate')

        '''
        word = serial.read()
        if len(word):
            if word[0] == 10:
                mode_chooser.set_mode("armor_stable")
                print("*"*10,"stable")
            elif word[0] == 20:
                mode_chooser.set_mode("armor_rotating")
                print("*"*10,"rotating")
            elif word[0] == 30:
                mode_chooser.set_mode("energy_stable")
                print("*"*10,"stable")
            elif word[0] == 40:
                mode_chooser.set_mode("energy_rotating")
                print("*"*10,"rotating")
        '''

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d","--debug",default = False,help="debug mode",action = "store_true")
    parser.add_argument("-r","--red",default = False,help="red mode",action = "store_true")
    parser.add_argument("-b","--blue",default = False,help="blue mode",action = "store_true")
    parser.add_argument("-s","--serial",default = True,help="need serial",action = "store_true")

    args = parser.parse_args()

    system_name = platform.system()
    print(system_name)

    if system_name == "Windows":
        import tkinter
        import tkinter.messagebox
        import tkinter.filedialog
        time.sleep(1)

        '''if you forget choose color'''
        if args.red == False and args.blue == False:
            IsBlue = tkinter.messagebox.askquestion(title='选择红蓝方', message='目标是否为蓝色？')
            print(IsBlue)
            if IsBlue == 'yes':
                args.blue = True
            else:
                args.red = True

        if tkinter.messagebox.askquestion(title='选择视频', message='未插摄像头，是否运行视频？'):
            video_path = './video/Video_20210109195619776.avi'
            print(video_path)
            cap = cv.VideoCapture(video_path)

    elif system_name == "Linux":
        if args.red == False and args.blue == False:
            args.blue = True

        from device.caps import CapManager
        cfg_reader = CapConfig()
        cfg = cfg_reader.merge_from_file("./config/BaseConfig.yaml")
        cap = CapManager(cfg=cfg, camera_number=0, debug=False)

    '''init moder_chooser'''
    if args.blue == True:
        mode_chooser = ModeChooser(color='blue',debug = args.debug)
    else:
        mode_chooser = ModeChooser(color='red',debug = args.debug)

    '''capture
    try:
        cfg_reader = CapConfig()
        cfg = cfg_reader.merge_from_file("./config/BaseConfig.yaml")
        cap = CapManager(cfg=cfg, camera_number=0, debug=False)
    except:
        if tkinter.messagebox.askquestion(title='选择视频', message='未插摄像头，是否运行视频？'):
            video_path = './video/Video_20210109195619776.avi'
            print(video_path)
            cap = cv.VideoCapture(video_path)
    '''

    '''threading for scanning keyboard triggers'''
    if args.serial:
        t1 = threading.Thread(target = keyboard_serial_task,args = (mode_chooser,))
        t1.setDaemon(True)
        t1.start()

    detect = Detect(mode_chooser)
    while True:
        start = cv.getTickCount()
        #读帧
        ret,frame = cap.read()
        #备份原图
        show = frame
        #根据模式选择
        if mode_chooser.current_mode=='armor_stable':
            print("***************  armor_stable  ***************")
            target,time_delay = detect.armor_stable(frame)
        elif mode_chooser.current_mode=='armor_rotate':
            print("***************  armor_rotate  ***************")
            target,time_delay = detect.armor_rotate(frame)

        end = cv.getTickCount()
        during = (end - start) / cv.getTickFrequency()
        print("time spend: {:.2f} ms".format(during * 1000))

        cv.imshow("frame",frame)
        cv.waitKey(1)