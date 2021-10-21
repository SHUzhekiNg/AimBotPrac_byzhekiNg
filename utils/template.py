import os
import cv2 as cv
class Template():
    def __init__(self):
        self.tpls = []
        self.modelpath = "./template_image/"
        self.roboclass = ['hero', 'infantry', 'engineering', 'sentry'] #, 'base'
        for name in self.roboclass:
            aClass = []
            imgs = os.listdir(self.modelpath + name)
            for i in range(len(imgs)):
                img = cv.imread(self.modelpath + name + '/' + imgs[i], 0)
                #print(self.modelpath + name + '/' + imgs[i])
                img = cv.resize(img, (50, 50))
                aClass.append(img)
            self.tpls.append(aClass)
    def __call__(self, *args, **kwargs):
        return self.tpls