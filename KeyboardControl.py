from djitellopy import tello
import KeyboardModule as kp

########IMPORTANT PARAMETERS######
me = tello.Tello()
me.connect()
##################################


def getkeyInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50

    if kp.getKey('a'): lr = -speed
    elif kp.getKey('d'): lr = speed

    if kp.getKey('w'): fb = speed
    elif kp.getKey('s'): fb = -speed

    if kp.getKey('UP'): ud = speed
    elif kp.getKey('DOWN'): ud = -speed

    if kp.getKey('LEFT'): yv = speed
    elif kp.getKey('RIGHT'): yv = -speed

    if kp.getKey('t'): me.takeoff()
    elif kp.getKey('y'): me.land()

    return [lr, fb, ud, yv]


while True:
    vals = getkeyInput()
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])