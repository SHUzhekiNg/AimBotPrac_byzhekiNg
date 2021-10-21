from utils.template import Template
import cv2 as cv
import numpy as np
import time

class ArmorRotate():
    def __init__(self):
        self.last_target=None
        '''us'''
        self.time_1=None
        self.time_2=None
        self.delta_time=None

        '''ms'''
        self.time_delay=None

    def timer_reset(self):
        self.time_1 = None
        self.time_2 = None

    def aim_filter(self,target,width):
        '''skip'''
        if target == None:
            return None,None
        '''first frame'''
        if self.last_target == None:
            self.last_target = target
            return None,None

        '''timing1 & timing2'''
        if abs(target[0]-self.last_target[0])>width and self.time_1==None:
            self.time_1=time.time()
            self.last_target=target
            return None,None
        elif abs(target[0]-self.last_target[0])>width and self.time_1!=None and self.time_2==None:
            self.time_2=time.time()
            self.delta_time = self.time_2-self.time_1
            self.time_delay = self.delta_time/2*10**3
            self.timer_reset()
            return [int(0.5*(target[0]+self.last_target[0])),int(0.5*(target[1]+self.last_target[1]))],self.time_delay
        else:
            self.last_target=target
            return None,None
