from utils.template import Template
import cv2 as cv
import numpy as np

class ArmorStable():
    def __init__(self):
        #红蓝二值化阈值
        self.blue_threshold = 100
        self.red_threshold = 80
        #roi区域和扩展宽度
        self.roi_left = 0
        self.roi_top = 0
        self.roi_right = 640
        self.roi_bottom = 480
        self.roi_brim_x = 30
        self.roi_brim_y = 20
        #模板匹配素材
        self.template = Template()
        self.tpls = self.template()

    def roi_crop(self, frame):
        frame_croped = frame[int(self.roi_top):int(self.roi_bottom), int(self.roi_left):int(self.roi_right)]
        return frame_croped

    def roi_update(self,result,width,height):
        target=[result[0]+self.roi_left,result[1]+self.roi_top]
        self.roi_brim_x = 0.75 * width
        #self.roi_brim_y = height
        self.roi_left = max(int(target[0]-0.5*width-self.roi_brim_x),0)
        self.roi_top = max(int(target[1]-0.5*height-self.roi_brim_y),0)
        self.roi_right = min(int(target[0]+0.5*width+self.roi_brim_x),640)
        self.roi_bottom = min(int(target[1]+0.5*height+self.roi_brim_y),480)
        return target

    def roi_reset(self):
        self.roi_left = 0
        self.roi_top = 0
        self.roi_right = 640
        self.roi_bottom = 480
        self.roi_brim_x = 50
        self.roi_brim_y = 30

    def pre(self,frame,color):
        r = frame[:, :, 2]
        b = frame[:, :, 0]
        if color == "red":
            binary = cv.subtract(r, b)
            ret, binary = cv.threshold(binary, self.red_threshold, 255, cv.THRESH_BINARY)
        else:
            binary = cv.subtract(b, r)
            ret, binary = cv.threshold(binary, self.blue_threshold, 255, cv.THRESH_BINARY)
        element = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
        binary = cv.dilate(binary, element, iterations=1)
        binary = cv.erode(binary, element, iterations=1)
        # binary = cv.GaussianBlur(binary,(3,3),0)
        #_, contours, _ = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        return binary

    def trajectory_correction(self,target):
        target[0]=target[0]-65
        target[1]=target[0]-127
        return target

    def lights_filter(self,binary):
        try:
            contours,_= cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        except Exception as e:
            _, contours,_= cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)            
        out_lights = [[0, 0, 0, 0, 0, 0, 0]]
        if not len(contours):
            return out_lights

        for contour in contours:
            area = cv.contourArea(contour)
            #
            if area < 10:  #
                # print("light area:{}".format(area))
                continue
            box = cv.minAreaRect(contour)
            (x, y), (w, h), theta = box
            # theta [-90,0]
            if w < h:
                theta = theta - 90
                w, h = h, w
            if -150 < theta < -30:  #

                if w / h < 1.2:  #
                    out_lights.append([0, 0, 0, 0, 0, 0, 0])
                    # print("theta:{}".format(w/h))
                    continue
                points = cv.boxPoints(box=box)
                out_lights.append([x, y, w, h, theta, area, contour])
            else:
                out_lights.append([0, 0, 0, 0, 0, 0, 0])
                # print("theta:{}".format(theta))
        out_lights.sort(key=lambda x:
        x[5], reverse=True)
        # out_lights.sort(key = lambda x: cv.contourArea(x[0]))
        # x,y sort
        # if have_old_target:
        # out_lights = out_lights[::-1][:3]
        return out_lights

    def aim_detect(self,frame,lights):
        lights = np.array(lights,dtype=object)
        lx = lights[:, 0]
        ly = lights[:, 1]
        lw = lights[:, 2]
        lh = lights[:, 3]
        ltheta = lights[:, 4]
        larea = lights[:, 5]
        contours = lights[:, 6]
        n = len(lx)
        for i in range(0, n):
            if lx[i] == 0:
                continue
            for j in range(i + 1, n):
                if lx[j] == 0:
                    continue
                if abs(ltheta[i] - ltheta[j]) > 20 and abs(ltheta[i] - ltheta[j]) != 90:
                    print("rejected by theta", abs(ltheta[i] - ltheta[j]), ltheta)
                    continue
                pair_h = max(lw[i], lw[j])
                pair_w = abs(lx[i] - lx[j])

                if pair_h and pair_w / pair_h <= 3:
                    print("infantry")
                    dey = abs(ly[i] - ly[j])
                    dex = abs(lx[i] - lx[j])
                    if dey > 80 or dex == 0:
                        print("rejected by infantry's dey")
                        continue
                    if dey / dex > 0.25:
                        print("rejected by infantry's dey/dex")
                        continue
                    else:
                        rect_i = cv.minAreaRect(contours[i])
                        points_i = cv.boxPoints(rect_i)
                        bbox_i = cv.boundingRect(points_i)
                        rect_j = cv.minAreaRect(contours[j])
                        points_j = cv.boxPoints(rect_j)
                        bbox_j = cv.boundingRect(points_j)

                        num_img = frame[int(max(min(bbox_i[1], bbox_j[1]) - 0.5 * min(lw[i], lw[j]), 0)):int(
                            min(max(bbox_i[1] + bbox_i[3], bbox_j[1] + bbox_j[3]) + 0.5 * max(lw[i], lw[j]), 480)),
                                  int(max(min(lx[i], lx[j]) + max(lh[i], lh[j]) + lh[i], 0)):int(
                                      min(max(lx[i], lx[j]) - min(lh[i], lh[j]) - 0.5 * lh[i], 640))]

                        try:
                            num_img = cv.cvtColor(num_img, cv.COLOR_BGR2GRAY)
                            ret, num_img_binary = cv.threshold(num_img, 0, 255, cv.THRESH_OTSU)
                            if ret >= 90:  # lazer
                                center = [(lx[i] + lx[j]) / 2., (ly[i] + ly[j]) / 2.]
                                width = max(lx[i], lx[j]) - min(lx[i], lx[j])
                                height = max(lw[i], lw[j])
                                print("passed by infantry's lazer")
                                return center, height, width
                                # ret,num_img_binary = cv.threshold(num_img,5, 255, cv.THRESH_BINARY)
                            num_img = cv.resize(num_img_binary, (50, 50))
                        except:
                            print("infantry's num_img error")
                            continue

                        cv.imshow("edge_number", num_img)
                        #cv.imwrite('00000.jpg', num_img)
                        #cv.waitKey(1)

                        for ii in range(len(self.tpls)):
                            if self.tpls[ii] == []:
                                continue
                            for jj in range(len(self.tpls[ii])):
                                result = cv.matchTemplate(num_img, self.tpls[ii][jj], cv.TM_CCOEFF_NORMED)[0][0]
                                if result > 0.4:
                                    center = [(lx[i] + lx[j]) / 2., (ly[i] + ly[j]) / 2.]
                                    width = max(lx[i], lx[j]) - min(lx[i], lx[j])
                                    height = max(lw[i], lw[j])
                                    # center[0] = center[0]
                                    print("passed by infantry's model")
                                    self.tpls[0], self.tpls[ii] = self.tpls[ii], self.tpls[0]
                                    return center, height, width

                elif pair_h and pair_w / pair_h <= 5.5:
                    print('hero')
                    dey = abs(ly[i] - ly[j])
                    dex = abs(lx[i] - lx[j])
                    if dey > 70 or dex == 0:
                        print("rejected by hero's dey")
                        continue
                    if dey / dex > 0.25:
                        print("rejected by hero's dey/dex")
                        continue
                    else:
                        try:
                            contours[i] = contours[i].astype(np.int64)
                            contours[j] = contours[j].astype(np.int64)
                        except:
                            print(contours[j])
                        rect_i = cv.minAreaRect(contours[i])
                        points_i = cv.boxPoints(rect_i)
                        bbox_i = cv.boundingRect(points_i)
                        rect_j = cv.minAreaRect(contours[j])
                        points_j = cv.boxPoints(rect_j)
                        bbox_j = cv.boundingRect(points_j)

                        # print(abs(ltheta[i] - ltheta[j]))

                        num_img = frame[int(max(min(bbox_i[1], bbox_j[1]) - 0.5 * min(lw[i], lw[j]), 0)):int(
                            min(max(bbox_i[1] + bbox_i[3], bbox_j[1] + bbox_j[3]) + 0.5 * max(lw[i], lw[j]), 480)),
                                  int(max(min(lx[i], lx[j]) + 2 * max(lh[i], lh[j]) + lh[i], 0)):int(
                                      min(max(lx[i], lx[j]) - 2 * min(lh[i], lh[j]) - 0.5 * lh[i], 640))]

                        try:
                            # num_img[:,:,2] = 0
                            num_img = cv.cvtColor(num_img, cv.COLOR_BGR2GRAY)
                            # ret,num_img_binary = cv.threshold(num_img,2,255,cv.THRESH_BINARY)
                            ret, num_img_binary = cv.threshold(num_img, 0, 255, cv.THRESH_OTSU)
                            if ret > 7:
                                ret, num_img_binary = cv.threshold(num_img, 5, 255, cv.THRESH_BINARY)
                            '''
                            print("ret:",ret)
                            if ret>=90:                                                            #lazer
                                center = [(lx[i]+lx[j])/2.,(ly[i]+ly[j])/2.]
                                width =  max(lx[i],lx[j])-min(lx[i],lx[j])
                                height = max(lw[i],lw[j])
                                print("passed by hero's lazer")                  
                                return center,height,width
                            '''
                            num_img = cv.resize(num_img_binary, (50, 50))
                        except:
                            continue
                        cv.imshow("edge_number", num_img)
                        #cv.imwrite('24.jpg', num_img)
                        #cv.waitKey(1)


                        for ii in range(len(self.tpls)):
                            if self.tpls[ii] == []:
                                continue
                            for jj in range(len(self.tpls[ii])):
                                result = cv.matchTemplate(num_img, self.tpls[ii][jj], cv.TM_CCOEFF_NORMED)[0][0]
                                if result > 0.35:
                                    center = [(lx[i] + lx[j]) / 2., (ly[i] + ly[j]) / 2.]
                                    width = max(lx[i], lx[j]) - min(lx[i], lx[j])
                                    height = max(lw[i], lw[j])
                                    # center[0] = center[0]
                                    print("passed by hero's model ", result)
                                    self.tpls[0], self.tpls[ii] = self.tpls[ii], self.tpls[0]
                                    return center, height, width
                                else:
                                    print("rejected by hero's model ", result)

                elif pair_h and pair_w / pair_h > 5.5:
                    print("rejected by pair_w/pair_h")

        return None, None, None
