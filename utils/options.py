from core.mode_chooser import ModeChooser
import cv2 as cv
import time
from utils.time import count_time
# class Options():
#     def __init__(self,mode_chooser):
#         self.mode_chooser = mode_chooser
#         self.windowname = "options"
#         cv.namedWindow(self.windowname,cv.WINDOW_AUTOSIZE)
#         cv.createTrackbar('IsBlue', self.windowname, 1, 1, self.trackbar_change)
#
#         self.change_flag = False
#
#     def __call__(self, *args, **kwargs):
#         return self.change_flag
#     def trackbar_change(self):
#         if cv.getTrackbarPos('IsBlue',"options") == 0:
#             self.change_flag = True
#             self.mode_chooser= ModeChooser(color='red')
#             self.mode_chooser.mode_set(mode='armor_stable')


def debug_mode(aClass):
    class Options():
        def __init__(self,mode_chooser):
            self.debug_mode = mode_chooser.current_mode
            self.wrapped = aClass(mode_chooser)
            self.windowname = "options"
            '''原始值'''
            self.blue_threshold = self.wrapped.armorstable.blue_threshold
            self.red_threshold = self.wrapped.armorstable.red_threshold
            self.color = mode_chooser.current_color

            cv.namedWindow(self.windowname,cv.WINDOW_AUTOSIZE)
            cv.createTrackbar('IsDebug', self.windowname, 0, 1, self.debug_change)
            cv.createTrackbar('IsBlue', self.windowname, 1, 1, self.color_change)
            cv.createTrackbar('IsStable', self.windowname, 1, 1, self.mode_change)
            cv.createTrackbar('binary', self.windowname, 100, 255, self.binary_threshold_change)

        def debug_change(self,*args):
            self.color_change()
            self.mode_change()
            self.binary_threshold_change()

        def color_change(self,*args):
            if cv.getTrackbarPos('IsDebug', "options") == 1:
                if cv.getTrackbarPos('IsBlue',"options") == 0:
                    self.wrapped.color = 'red'
                    print("**********swtich red mode**********")
                    time.sleep(3)
                else:
                    self.wrapped.color = 'blue'
                    print("**********swtich blue mode**********")
                    time.sleep(3)
            else:
                self.wrapped.color = self.color

        def mode_change(self,*args):
            if cv.getTrackbarPos('IsStable',"options") == 0:
                self.debug_mode = 'armor_rotate'
                print("**********swtich armor_rotate mode**********")
                time.sleep(3)
            else:
                self.debug_mode = 'armor_stable'
                print("**********swtich armor_stable mode**********")
                time.sleep(3)

        def binary_threshold_change(self,*args):
            if cv.getTrackbarPos('IsDebug', "options") == 1:
                self.wrapped.armorstable.blue_threshold = cv.getTrackbarPos('binary' , "options")
                self.wrapped.armorstable.red_threshold = cv.getTrackbarPos('binary', "options")
            else:
                self.wrapped.armorstable.blue_threshold = self.blue_threshold
                self.wrapped.armorstable.red_threshold = self.red_threshold


        def armor_stable(self,frame):
            if cv.getTrackbarPos('IsDebug', "options") == 1:
                if self.debug_mode == 'armor_stable':
                    target,time_delay=self.wrapped.armor_stable(frame)
                elif self.debug_mode == 'armor_rotate':
                    target,time_delay=self.wrapped.armor_rotate(frame)
            else:
                target, time_delay = self.wrapped.armor_stable(frame)
            return target, time_delay

        def armor_rotate(self,frame):
            if cv.getTrackbarPos('IsDebug', "options") == 1:
                if self.debug_mode == 'armor_stable':
                    target, time_delay = self.wrapped.armor_stable(frame)
                elif self.debug_mode == 'armor_rotate':
                    target, time_delay = self.wrapped.armor_rotate(frame)
            else:
                target, time_delay = self.wrapped.armor_rotate(frame)
            return target, time_delay
    return Options
