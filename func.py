import os
import cv2
import numpy as np
from scipy import stats


def draw_lines(input_img, file, lines, a_l):

    file.write(i + ':')
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
        angle = result_push(a_l, angle)

        file.write(str(angle) + ',')

    return hough


def draw_lines_P(input_image, file, lines, a_l):

    file.write(i + ':')
    for line in lines:
        x1, y1, x2, y2 = line[0]
        hough = cv2.line(input_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
        if x2 == x1:
            angle = 90
        else:
            angle = int(np.arctan((y2 - y1) / (x2 - x1)) * 180)
        angle = result_push(a_l, angle, axis=1)
        file.write(str(angle) + ',')

    return hough


def result_process(a_l):

    a_l = np.array(a_l)
    a_l_unique = np.unique(a_l)
    a_l_copy = []
    if len(a_l_unique) == 1:
        result = a_l[0]
    elif len(a_l_unique) > 1:
        if len(a_l_unique) > 3:
            mode = stats.mode(a_l)[0][0]
            for i in a_l:
                if mode - 10 <= i <= mode + 10:
                    a_l_copy.append(i)
        result = np.mean(a_l_copy)

    return result


def result_push(a_l, angle, axis=0):
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
    return angle


path = 'data'

list = os.listdir(path)
f = open('output.txt', 'w+')

for i in list:

    img_path = path + '/' + i
    angle_list = []
    img = cv2.imread(img_path)
    x = img.shape[0]
    y = img.shape[1]
    gray = cv2.imread(img_path, 0)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    kernel = np.ones((3, 3), np.uint8)
    dilation = cv2.dilate(gray, kernel, iterations=1)
    # closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    canny = cv2.Canny(gray, 150, 250, apertureSize=3)

    cv2.imwrite('canny/' + i.strip('.jpg') + '_c.jpg', canny)
    threshold = 900
    flag = False
    while threshold > 0 and flag is False:

        lines = cv2.HoughLines(canny, 1.0, np.pi / 180, threshold)

        if lines is not None:
            hough = draw_lines(img, f, lines, angle_list)
            flag = True

        else:
            threshold -= 100

    if flag is False:
        canny_d = cv2.Canny(dilation, 150, 250, apertureSize=3)
        lines_with_p = cv2.HoughLinesP(canny_d, 1.0, np.pi/180, 100, max(x, y) / 10, 10)

        if lines_with_p is not None:
            draw_lines_P()

        else:
            print(i + "!!!!!!!!!!!!!!!!!!!!")
            hough = img

    f.write('\n')
    result = result_process(angle_list)
    cv2.imwrite('hough/' + i.strip('.jpg') + '_h.jpg', hough)
    print("procession of " + i + " finish")
    print(result)
f.close()
