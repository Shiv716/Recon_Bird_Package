import cv2 as cv
import numpy as np
import math

# x1, y1 , x2, y2 : Points for bar co-ordinates
################## TESTING/IMPORTANT PARAMETERS:-
num = input("Enter a number: ")

# Initialising the camera:-
cap = cv.VideoCapture(0)
# Setting the dimensions for the cam:
width = cap.set(3, 1280)
height = cap.set(4, 720)
##################


# FORMULAS THAT CAN BE USED:-


def ellipse_peri(r1, r2):
    peri = 2 * math.pi * math.sqrt((r1*r1 + r2*r2)/2)
    return int(peri)


def rotated_ellipse(r1, r2, x, y):
    eq1 = math.pow(r1,2) + math.pow(y,2)
    eq2 = math.pow(r2,2) + math.pow(x,2)
    eq3 = math.pow(r1,2) * math.pow(r2,2)

    return r1, r2


# Gives the mid-point of a given line:-
def midPoint(x1, y1, x2, y2):
    x3 = (x1 + x2) / 2
    y3 = (y1 + y2) / 2

    return x3, y3


def bar(img, x1, y1, x2, y2):
    # First line (Outer) ##
    cv.line(img, (x1, y1), (x2, y2), (0, 0, 0), 2)
    # Drawing the circle at the mid-point of lines:
    Ax, Ay = midPoint(x1, y1, x2, y2)
    cv.circle(img, (int(Ax), int(Ay)), 2, (0, 0, 185), 5)

    # Second line (Outer) ##
    cv.line(img, (x1 - 10, y1 + 20), (x2 - 10, y2 + 20), (0, 0, 0), 2)
    Bx, By = midPoint(x1 - 10, y1 + 20, x2 - 10, y2 + 20)
    cv.circle(img, (int(Bx), int(By)), 2, (0, 0, 185), 5)

    # Third line (Joining left side)
    cv.line(img, (x1, y1), (x1 - 10, y1 + 20), (0, 0, 0), 2)
    Cx, Cy = midPoint(x1, y1, x1 - 10, y1 + 20)
    cv.circle(img, (int(Cx), int(Cy)), 2, (0, 0, 185), 5)

    # Fourth line (Joining right side)
    cv.line(img, (x2, y2), (x2 - 10, y2 + 20), (0, 0, 0), 2)
    Dx, Dy = midPoint(x2, y2, x2 - 10, y2 + 20)
    cv.circle(img, (int(Dx), int(Dy)), 2, (0, 0, 185), 5)


# For stacking bars according to need given by desired constant:-
def load_bars(img, y, num, x1, x2, basePoint1, topPoint1, basePoint2, topPoint2):
    array = [1, 2, 3, 4, 5, 6, 7, 8]
    if num != 0:
        try:
            for i in range(len(array)):
                y -= 30
                if i == array[int(num)-1]:
                    break
                else:
                    bar(img, x1, y, x2, y)
                    # Increasing side-bars:
                    if y == 260:
                        cv.line(img, basePoint1, topPoint1, (0, 0, 170), 4)
                        cv.line(img, basePoint2, topPoint2, (0, 0, 170), 4)
                        break
                    else:
                        # Side 1 :
                        cv.line(img, basePoint1, (x1-28, y), (0, 0, 170), 4)
                        # Side 2:
                        cv.line(img, basePoint2, (x2+19, y), (0, 0, 170), 4)

        except IndexError:
            print("Array finished!")


def nav_arrow(img):
    # draw a triangle
    xPoint = 680
    yPoint = 180
    xDev = 155
    yDev = 45
    vertices = np.array([[xPoint, yPoint], [xPoint-xDev, yPoint+yDev], [xPoint+xDev, yPoint+yDev]], np.int32)
    pts = vertices.reshape((-1, 1, 2))
    cv.polylines(img, [pts], isClosed=True, color=(0, 0, 0), thickness=4)

    # fill it
    cv.fillPoly(img, [pts], color=(0, 0, 160))


def lane(img):
    # Points for left side
    xPoint1 = 290
    yPoint1 = 640

    # Points for right side
    xPoint2 = 390
    yPoint2 = 640
    # Left side lane, first half:-
    cv.line(img, (xPoint1+15, yPoint1), (xPoint1+160, yPoint1-200), (0, 0, 0), 2)
    # Right side lane, first half:-
    cv.line(img, (xPoint2+650, yPoint2-10), (xPoint2+520, yPoint2-200), (0, 0, 0), 2)
    # Drawing the marks after first half of both sides:-
    # LEFT SIDE:-
    cv.line(img, (xPoint1+160, yPoint1-200), (xPoint1+195, yPoint1-200), (0, 0, 0), 3)
    # RIGHT SIDE:-
    cv.line(img, (xPoint2+485, yPoint2-200), (xPoint2+520, yPoint2-200), (0, 0, 0), 3)

    # Further drawing the lanes - second half:-
    # Left lane:-
    cv.line(img, (xPoint1+162, yPoint1-202), (xPoint1+292, yPoint1-390), (0, 0, 0), 2)
    # Right side:-
    cv.line(img, (xPoint2+518, yPoint2-202), (xPoint2+397, yPoint2-390), (0, 0, 0), 2)


def steering_angle(img):
    point1 = 675
    point2 = 490

    # cv.ellipse(img, center, axes, angle, startAngle, endAngle, (0, 0, 170), 3)
    # Center signal:
    cv.circle(img, (point1, point2), 13, (0, 0, 0), 4)

    # Left Signal:
    cv.circle(img, (point1-50, point2+3), 13, (0, 0, 0), 4)
    cv.circle(img, (point1-100, point2+12), 13, (0, 0, 0), 4)
    cv.circle(img, (point1-150, point2+30), 13, (0, 0, 0), 4)

    # Right Signal :
    cv.circle(img, (point1 + 50, point2+3), 13, (0, 0, 0), 4)
    cv.circle(img, (point1 + 100, point2+12), 13, (0, 0, 0), 4)
    cv.circle(img, (point1 + 150, point2+30), 13, (0, 0, 0), 4)

    # Colour filling circle:-
    cv.circle(img, (point1, 490), 4, (0, 0, 160), 13)


def steering_wheel(img, speed):
    # Ellipse parameters
    radius = 67
    point1 = 675
    point2 = 600
    center = (point1, point2)
    axes = (radius, radius)
    angle = 0
    startAngle = 0
    endAngle = 360
    cv.ellipse(img, center, axes, angle, startAngle, endAngle, (0, 0, 150), 5)

    # Super-imposed Ellipse:-
    extAngle_start1 = 345
    angle_ext1 = 195

    # Upper Center:-
    cv.ellipse(img, center, axes, angle, extAngle_start1, angle_ext1, (0, 0, 0), 5)

    # Lower right:-
    extAngle_start2 = 10
    angle_ext2 = 80
    cv.ellipse(img, center, axes, angle, extAngle_start2, angle_ext2, (0, 0, 0), 5)

    # Lower Left:-
    extAngle_start3 = 100
    angle_ext3 = 170
    cv.ellipse(img, center, axes, angle, extAngle_start3, angle_ext3, (0, 0, 0), 5)

    # Interior design of the steering wheel:-
    # X-AXIS DESIGN WHEEL 1
    center2 = (point1-33, point2)
    axes2 = (radius-37, radius-60)
    cv.ellipse(img, center2, axes2, angle, startAngle, endAngle, (0, 0, 160), 3)

    # X-AXIS DESIGN WHEEL 2
    center3 = (point1+33, point2)
    cv.ellipse(img, center3, axes2, angle, startAngle, endAngle, (0, 0, 160), 3)

    # Y-AXIS DESIGN WHEEL
    axes3 = (radius-60, radius-35)
    # center4 = (point1, point2+33)
    center4 = (point1, point2+33)
    cv.ellipse(img, center4, axes3, angle, startAngle, endAngle, (0, 0, 160), 3)

    # Middle circle:
    cv.circle(img, center, 4, (0, 0, 0), 2)
    cv.circle(img, center, 10, (0, 0, 0), 3)

    # Printing Speed:-
    cv.putText(img, speed, (653, 572), cv.FONT_HERSHEY_COMPLEX, 1, (0, 0, 100), 2)

    # Further drawing around steering wheel (Dashboard design):-
    axes4 = (radius+120, radius+20)
    axes5 = (radius+60, radius+25)
    center2 = (point1, point2 + 20)
    cv.ellipse(img, center, axes4, angle, 180, 360, (0, 0, 0), 3)
    cv.line(img, (545, 620), (0, 720), (0, 0, 0), 3)
    cv.line(img, (805, 620), (1280, 720), (0, 0, 0), 3)
    cv.ellipse(img, center2, axes5, angle, 0, 180, (0, 0, 0), 3)


def mainFunc():

    while True:
        success, img = cap.read()

        # Putting the text:-
        cv.putText(img, f'Speed m/s', (50, 225), cv.FONT_HERSHEY_DUPLEX, 1, (0, 0, 100), 2)

        # BASE BAR:-
        y = 500
        x1 = 100
        x2 = 125
        bar(img, x1, y, x2, y)
        # LOADING more bars accordingly:
        # Mega-Bar to store the individual bars:-
        cv.rectangle(img, (x1 - 25, y - 255), (x2 + 15, y + 35), (0, 0, 0), 2)
        # Exterior design:
        cv.rectangle(img, (x1 - 32, y - 262), (x2 + 22, y + 42), (0, 0, 0), 2)
        # Joining the base line:
        cv.line(img, (x1 - 29, y + 38), (x2 + 19, y + 38), (0, 0, 170), 4)

        # Base and Top points of bar-lines at the sides of the bar:-
        basePoint1 = (x1 - 28, y + 38)
        basePoint2 = (x2 + 19, y + 38)
        topPoint1 = (x1 - 28, y - 259)
        topPoint2 = (x2 + 19, y - 259)

        # Joining the top line:-
        cv.line(img, (x1 - 29, y - 259), (x2 + 20, y - 259), (0, 0, 170), 4)

        # JOIN THE TOP LINE WHEN BAR IS FULL:

        load_bars(img, y, num, x1, x2, basePoint1, topPoint1, basePoint2, topPoint2)

        speed = '60'
        # Drawing the steering wheel:-
        steering_wheel(img, speed)

        # NAVIGATION ARROW:-
        nav_arrow(img)

        # Loading the steering angle:
        steering_angle(img)

        # Drawing the following lane:-
        lane(img)

        cv.imshow('Footage', img)
        cv.waitKey(1)


if __name__ == '__main__':
    print("Initialising software..")
    mainFunc()