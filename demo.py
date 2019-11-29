import os
import cv2
import numpy as np
from scipy import stats
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", '--input', type=str, help="Path to the input image")
args = vars(parser.parse_args())
IMAGE_PATH = args["input"]


class AngleMeasure:

    def __init__(self):

        self.isInputExist = False
        self.outputDirPath = './output'
        self.inputPath = IMAGE_PATH
        if os.path.exists(self.inputPath):
            self.img = cv2.imread(self.inputPath)
            self.gray = cv2.GaussianBlur(cv2.imread(self.inputPath, 0),
                                         (5, 5), 0)
            self.kernel = np.ones((3, 3), np.uint8)
            self.dilation = cv2.dilate(self.gray, self.kernel, iterations=1)
            self.canny = cv2.Canny(self.gray, 150, 250, apertureSize=3)
            self.cannyD = cv2.Canny(self.dilation, 150, 250, apertureSize=3)
            self.threshold = 900
            self.isInputExist = True
            self.flag = False
            self.angleList = None
            self.result = None
        else:
            print("input image is not exist")
            exit()

    def draw_lines(self, input_img, lines, a_l):

        for line in lines:
            rho, theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * a)
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * a)
            hough = cv2.line(input_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

            angle = int(theta / np.pi * 180)
            self.result_push(a_l, angle)

        return hough, a_l

    def draw_lines_p(self, input_image, lines, a_l):

        for line in lines:
            x1, y1, x2, y2 = line[0]
            hough = cv2.line(input_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
            if x2 == x1:
                angle = 90
            else:
                angle = int(np.arctan((y2 - y1) / (x2 - x1)) * 180)
            self.result_push(a_l, angle, axis=1)

        return hough, a_l

    def result_push(self, a_l, angle, axis=0):
        if axis:
            if angle >= 360:
                angle -= 360
            elif angle >= 180:
                angle -= 180
            elif angle <= -360:
                angle = -angle - 360
            elif angle <= -180:
                angle = -angle - 180
            elif angle <= 0:
                angle = -angle
        else:
            if 0 <= angle <= 90:
                angle = 90 - angle
            elif 90 < angle <= 270:
                angle = 270 - angle
            elif 270 < angle <= 360:
                angle = 450 - angle
        a_l.append(angle)

        return angle, a_l

    def result_process(self, a_l):
        
        for a in a_l:
            if a >= 90:
                a -= 90
        a_l = np.array(a_l)
        a_l_unique = np.unique(a_l)
        a_l_copy = []
        if len(a_l_unique) == 1:
            result = a_l[0]
        else:
            mode = stats.mode(a_l)[0][0]
            for i in a_l:
                if mode - 10 <= i <= mode + 10:
                    a_l_copy.append(i)
            result = np.mean(a_l_copy)

        return result

    def measure(self):

        self.angleList = []

        while self.threshold > 0 and self.flag is False:

            lines = cv2.HoughLines(self.canny, 1.0, np.pi / 180, self.threshold)

            if lines is not None:
                hough, self.angleList = self.draw_lines(self.img, lines, self.angleList)
                self.flag = True

            else:
                self.threshold -= 100

        if self.flag is False:

            lines_with_p = cv2.HoughLinesP(self.cannyD, 1.0, np.pi / 180, 100, max(x, y) / 10, 10)

            if lines_with_p is not None:
                hough, self.angleList = self.draw_lines_p(self.img, lines_with_p, self.angleList)

            else:
                hough = self.img

        self.result = self.result_process(self.angleList)
        print("result: " + str(int(self.result)))


if __name__ == "__main__":
    am = AngleMeasure()
    am.measure()
