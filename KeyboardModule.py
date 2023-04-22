import pygame as py
import pygame.image
import cv2 as cv


def init():
    py.init()
    screen = py.display.set_mode((386, 258))


    #For icon-image
    #bg = pygame.image.load('digitalMap.png')
    icon = pygame.image.load('drone.png')
    #pygame.display.set_icon(icon)
    #pygame.display.set_caption("Map")
    #screen.blit(bg, (0, 0))
    # Putting drone image in the map image
    #screen.blit(icon, (100, 100))


def getKey(keyName):
    ans = False
    for eve in py.event.get():
        pass
    keyInput = py.key.get_pressed()
    myKey = getattr(py, 'K_{}'.format(keyName))
    if keyInput[myKey]:
        ans = True
    py.display.update()
    return ans


def main():
    # create conditions for keys pressed here
    if getKey('LEFT'):
        print("Left key pressed")
    if getKey('RIGHT'):
        print("Right key pressed")


if __name__ == '__main__':
    init()
    while True:
        getKey("a")
        main()