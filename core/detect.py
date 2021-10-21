#from core.lights import Lights
from core.armor_stable import ArmorStable
from core.armor_rotate import ArmorRotate
from core.filter import KalmanFilter
from core.mode_chooser import ModeChooser
from utils.time import count_time
from utils.options import debug_mode
#from utils.debug import Debug
import cv2 as cv
import numpy as np

#@count_time
@debug_mode
class Detect():
    def __init__(self,mode_chooser):
        self.color = mode_chooser.current_color
        self.mode = mode_chooser.current_mode

        self.is_lastframe_lost=True
        #自瞄
        self.armorstable = ArmorStable()
        #小陀螺
        self.armorrotate = ArmorRotate()
        #卡尔曼滤波器
        self.kalman = KalmanFilter()

    #@count_time
    def armor_stable(self,frame):
        #roi切割原图
        frame_crop = self.armorstable.roi_crop(frame)
        cv.imshow("frame_crop", frame_crop)
        #二值化、膨胀腐蚀二值化
        binary = self.armorstable.pre(frame_crop,self.color)
        #检测灯条
        lights = self.armorstable.lights_filter(binary)
        #检测装甲板
        result,height,width = self.armorstable.aim_detect(frame_crop,lights)
        if result is not None:
            #将装甲板坐标映射回原图、更新roi
            target = self.armorstable.roi_update(result,width,height)
            cv.rectangle(frame, (int(target[0] - 0.5 * width), int(target[1] - 0.5 * height)),
                         (int(target[0] + 0.5 * width), int(target[1] + 0.5 * height)), (0, 125, 0), thickness=2)

            #kalman
            # if self.is_lastframe_lost == True:
            #     self.kalman.correct([320,target[1]])
            # else:
            #     self.kalman.correct(target)
            self.kalman.correct(target)
            target = self.kalman.predict()
            self.is_lastframe_lost = False
            cv.circle(frame,(int(target[0] ), int(target[1] )),5,(0,0,255),-1)
            #cv.imshow("target", frame)
            #弹道补偿
            target = self.armorstable.trajectory_correction(target)
        else:
            self.is_lastframe_lost = True
            target = None
            self.kalman.correct([320,240])
            self.armorstable.roi_reset()
        return target,0

    #@count_time
    def armor_rotate(self,frame):
        '''使用自瞄的函数'''
        frame_crop = self.armorstable.roi_crop(frame)
        binary = self.armorstable.pre(frame_crop, self.color)
        lights = self.armorstable.lights_filter(binary)
        result,height,width = self.armorstable.aim_detect(frame_crop,lights)
        if result is not None:
            target = self.armorstable.roi_update(result,width,height)
            cv.rectangle(frame, (int(target[0]-0.5*width),int(target[1]-0.5*height)), (int(target[0]+0.5*width),int(target[1]+0.5*height)), (0,125,0), thickness=2)
            #cv.imshow("target",frame)
        else:
            target = None
            self.armorstable.roi_reset()

        '''小陀螺，设计思想：滤去丢失目标的帧，然后检测突变'''
        target,time_delay = self.armorrotate.aim_filter(target,width)

        if target is not None:
            cv.rectangle(frame, (int(target[0] - 0.5 * width), int(target[1] - 0.5 * height)),
                         (int(target[0] + 0.5 * width), int(target[1] + 0.5 * height)), (0, 0, 125), thickness=2)
            print(target,time_delay )
            cv.imshow("rotate target", frame)
            target = self.armorstable.trajectory_correction(target)
        return target,time_delay

