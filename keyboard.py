from pynput.keyboard import Key, Listener
from djitellopy import tello

# Parameters for drone:-
me = tello.Tello()


def press(key):
    print(key)


def release(key):
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50

    # Movement velocity:-
    if key == Key.up:
        ud = speed
    if key == Key.down:
        ud = -speed
    if key == Key.left:
        yv = speed
    if key == Key.right:
        yv = -speed

    # Yaw velocity:-
    if key == Key.right:
        yv = -speed
    if key == Key.right:
        yv = -speed

    # Dis-able key-press
    if key == Key.esc:
        return False


with Listener(on_press=press, on_release=release) as listener:listener.join()