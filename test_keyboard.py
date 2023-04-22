import keyboard


def key_press():
    if keyboard.Key.up:
        print("You pressed 'a'.")


if __name__ == '__main__':
    key_press()