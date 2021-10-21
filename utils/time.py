import cv2 as cv

# def count_time(fn):
#     def cv_count_time(*args,**kw):
#         start = cv.getTickCount()
#         pred_center = fn(*args,**kw)
#         end = cv.getTickCount()
#         during= (end - start) / cv.getTickFrequency()
#         print("time spend: {:.2f} ms".format(during * 1000))
#         return pred_center
#     return cv_count_time()

def count_time(aClass):
    class Timer():
        def __init__(self, mode_chooser):
            self.wrapped = aClass(mode_chooser)

        def armor_stable(self,frame):
            start = cv.getTickCount()
            target, time_delay = self.wrapped.armor_stable(frame)
            end = cv.getTickCount()
            during= (end - start) / cv.getTickFrequency()
            print("time spend: {:.2f} ms".format(during * 1000))
            return target, time_delay

        def armor_rotate(self, frame):
            start = cv.getTickCount()
            target, time_delay = self.wrapped.armor_stable(frame)
            end = cv.getTickCount()
            during = (end - start) / cv.getTickFrequency()
            print("time spend: {:.2f} ms".format(during * 1000))
            return target, time_delay
    return Timer