import os.path
import threading
import time

from kivymd.app import MDApp
from djitellopy import tello
from kivy.core.audio import SoundLoader
from kivy.core.image import Texture
from kivy import Config
from kivy.graphics.texture import Texture

from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.button import ButtonBehavior

from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.camera import Camera
from kivy.uix.popup import Popup
import cv2 as cv
from kivy.uix.screenmanager import ScreenManager, Screen

from Detector import Detector

# Setting screen size and position:-

Config.set('kivy', 'exit_on_escape', 0)

from kivy.core.window import Window

Window.size = (830, 800)
Window.borderless = True
Window.top = 500

## Drone-parameters ##
me = tello.Tello()
me.connect()
print(me.get_battery())
battery = me.get_battery()
me.streamon()
##


# Flight-controls pop-up
class flight_popUp(Popup):
    pass


# Detection pop-up
class detect_pop_Up(Popup):
    pass


# Drone-feed pop-up
class cam_pop_Up(Popup):
    pass


class Recon_Bird(App):
    # return the Window having the background template.
    def build(self):
        print("Initialising software...")
        # Building screens
        wm = ScreenManager()
        wm.add_widget(Authentication_Window(name='Authenticate'))
        wm.add_widget(Background(name='Main_Window'))
        wm.add_widget(exit_page1(name='exitPage1'))
        wm.add_widget(exit_page2(name='exitPage2'))
        return wm


# First window to provide security for the software and to present animation,
class Authentication_Window(Screen, MDApp):

    # Setting the password-key for allowing user entry into the software,
    password = 'password'

    def __init__(self, **kwargs):
        super(Authentication_Window, self).__init__(**kwargs)
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Gray'

    # Verify the password
    def validate(self):
        if self.ids.text_field.text == self.password:
            self.ids.label.text = '[color=#43EA21]Access Granted[/color]'

            # Rotating the lock animation if entered password is correct:-
            self.ids.gif.anim_delay = 0.05
            self.ids.gif._coreimage.anim_reset(True)

            # Playing the sound effect of unlocking::
            sound = SoundLoader.load('unlocking.wav')
            if sound:
                # Playing while landing.
                sound.play()

            # making thread to have a gap before loading next screen
            myThread = threading.Thread(target=self.load_screen)
            myThread.start()

        else:
            self.ids.label.text = '[color=#EA2121]Access Denied[/color]'
            # Sound effect if wrong password is entered!
            sound = SoundLoader.load('wrong_pass.mp3')
            if sound:
                # Playing while landing.
                sound.play()

    def load_screen(self):
        timing = time.time()
        while timing + 2.5 > time.time():  # 3 seconds
            time.sleep(1)

        # After loading moving on to next screen:
        self.manager.current = 'Main_Window'

    # Exit-page:
    def open_exit_page(self):
        self.manager.current = 'exitPage1'
        self.manager.transition.direction = 'left'


# Exit-page when accessed from 'Authentication-Window'
class exit_page1(Screen, MDApp):
    # Closing the window
    def win_button_yes(self):
        Window.close()

    # Transitioning the window to previous if exit made window.
    def win_button_no(self):
        self.manager.current = 'Authenticate'


# Exit-page when accessed from 'Main-Window'
class exit_page2(Screen, MDApp):
    # Closing the window
    def win_button_yes(self):
        Window.close()

    # Transitioning the window to previous if exit made window.
    def win_button_no(self):
        self.manager.current = 'Main_Window'


# Getting the feed from the drone to display in the main-window:-
class TelloCamera(Camera):

    def __init__(self, **kwargs):
        super(TelloCamera, self).__init__(**kwargs)

        # Set the resolution of the camera
        self.resolution = (640, 480)

        # Setting the callback function to process the video frames
        Clock.schedule_interval(self.process_frame, 1.0 / 30.0)

    def process_frame(self, dt):
        # Getting the video stream from the drone
        frame = me.get_frame_read().frame

        # Converting the video stream to a format which can be displayed by Kivy GUI
        img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        img = cv.flip(img, 0)

        # Update the image in the Kivy GUI
        texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='rgb')
        texture.blit_buffer(img.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
        self.texture = texture
        # returning the texture-image so that it can be saved and processed through a widget.
        return self.texture


# MainWindow for GUI use: create a background class which uses the boxlayout
class Background(Screen, ButtonBehavior):
    click_disabled = BooleanProperty(True)
    power_button_enabled = BooleanProperty(True)

    drone_blink_rate = BooleanProperty(True)

    # For dis-abling exit button when drone is flying
    exit_bool = BooleanProperty(False)

    # Battery-label : Angle-adjustment (Initially after screen begins..):-
    label_angle = battery * 3.6
    label_angle = round(label_angle)

    # Loading the model to cast detection on the most recent image captured.
    # BACKUP MODEL:-
    #modelURL = 'http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_320x320_coco17_tpu-8.tar.gz'

    # MODEL TO BE USED :-
    modelURL = 'http://download.tensorflow.org/models/object_detection/tf2/20200711/faster_rcnn_resnet101_v1_640x640_coco17_tpu-8.tar.gz'
    classFile = 'coco.names'
    detector = Detector()
    detector.readClasses(classFile)
    detector.downloadModel(modelURL)
    detector.loadModel()

    def capture(self):
        # capturing the image from the camera (KIVY)
        global image
        # labelling the image
        timestr = time.strftime("%Y%m%d_%H%M%S")
        # saving the image in Specified folder
        path = '/Users/shivangchaudhary/PycharmProjects/Recon_Bird_Package/CapturedImages'

        # Obtaining image from the drone.
        image = TelloCamera().process_frame(dt='ubyte')

        # Saving the image is the designated folder
        image.save(os.path.join(path, "Captured_image_{}.png".format(timestr)))

        # storing the address of the most recent image
        image = os.path.join(path, "Captured_image_{}.png".format(timestr))
        print("Captured")

        # Enabling the detection-button:
        self.click_disabled = False

    def display(self):
        # Using the stored address of the most recent image to perform object-detection:-
        self.detector.predictImage(image)

    # Adding the blinking effect to buttons
    def blink_button(self, widget):
        anim = Animation(animated_color=(0, 0.7, 0, 0), blink_size=350)
        anim.bind(on_complete=self.reset)
        anim.start(widget)

    def reset(self, *args):
        widget = args[1]
        widget.animated_color = (0, 0.7, 0, 1)
        widget.blink_size = 0

    # Take-off then enabling drone-controls:-
    # This function is attached to switch_button in-order to enable key-press for controlling drone flight -
    # - as soon as the drone takes-off.
    def control_enable(self):
        # enabling drone-movements:-
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        index = keycode[0]
        # Index will represent the actual keycode of each key-presses so as to use them for sending right kind of -
        # - signals to the drone for successful movements. [It is because keycode as a whole is an 'array' of 2 values]

        # For controlling and making movement of drone in every angle bit smoother, 2 threads are introduced in the -
        # - following function, one before and one after every key-press for every movement.

        if index == 119:
            print("move forward")
            timing1 = time.time()
            while timing1 + 0.1 > time.time():  # ~0 second
                time.sleep(1)
            # Step by step movement,
            me.send_rc_control(0, +20, 0, 0)

            # For controlling the sending velocity
            while timing1 + 0.2 > time.time():  # ~0 second
                time.sleep(1)

            me.send_rc_control(0, 0, 0, 0)

        if index == 115:
            print('move backward')
            timing2 = time.time()
            while timing2 + 0.1 > time.time():  # ~0 second
                time.sleep(1)
            # Step by step movement,
            me.send_rc_control(0, -20, 0, 0)
            while timing2 + 0.2 > time.time():  # ~0 second
                time.sleep(1)
            me.send_rc_control(0, 0, 0, 0)

        if index == 100:
            print('yaw right')
            timing3 = time.time()
            while timing3 + 0.1 > time.time():  # ~0 second
                time.sleep(1)
            # Step by step movement,
            me.send_rc_control(+20, 0, 0, 0)
            while timing3 + 0.2 > time.time():  # ~0 second
                time.sleep(1)
            me.send_rc_control(0, 0, 0, 0)

        if index == 97:
            print('yaw left')
            timing4 = time.time()
            while timing4 + 0.1 > time.time():  # ~0 second
                time.sleep(1)
            # Step by step movement,
            me.send_rc_control(-20, 0, 0, 0)
            while timing4 + 0.2 > time.time():  # ~0 second
                time.sleep(1)
            me.send_rc_control(0, 0, 0, 0)

        if index == 273:
            print('hover up')
            timing5 = time.time()
            while timing5 + 0.1 > time.time():  # ~0 second
                time.sleep(1)
            # Step by step movement,
            me.send_rc_control(0, 0, +20, 0)
            while timing5 + 0.2 > time.time():  # ~0 second
                time.sleep(1)
            me.send_rc_control(0, 0, 0, 0)

        if index == 274:
            print('hover down')

            timing6 = time.time()
            while timing6 + 0.1 > time.time():  # ~0 second
                time.sleep(1)
            # Step by step movement,
            me.send_rc_control(0, 0, -20, 0)
            while timing6 + 0.2 > time.time():  # ~0 second
                time.sleep(1)
            me.send_rc_control(0, 0, 0, 0)

        if index == 276:
            print('turn left')

            timing7 = time.time()
            # Step by step movement,
            me.send_rc_control(0, 0, 0, -30)

            while timing7 + 0.2 > time.time():  # ~0 second
                time.sleep(1)
            me.send_rc_control(0, 0, 0, 0)

        if index == 275:
            print('turn right')

            timing8 = time.time()
            # Step by step movement,
            me.send_rc_control(0, 0, 0, +30)

            while timing8 + 0.2 > time.time():  # ~0 second
                time.sleep(1)
            me.send_rc_control(0, 0, 0, 0)

    # Drone sound
    def drone_sound(self):
        sound = SoundLoader.load('drone_sound.mp3')
        if sound:
            # Playing while takeoff.
            sound.play()

        # Dis-abling exit:-
        self.exit_bool = True

        # Changing a property for drone-widget animation:-

        # disabling the on-button:
        self.power_button_enabled = False

        # Enabling drone-blinking
        self.drone_blink_rate = True

        # Battery-label : Angle-adjustment (On-button click):-
        self.label_angle = battery * 3.6
        self.label_angle = round(self.label_angle)

        # Using a thread to simulate take-off
        myThread = threading.Thread(target=self.take_off)
        myThread.start()

    # Take-off drone:-
    def take_off(self):
        # Take-off drone:-
        timing = time.time()
        while timing + 2 > time.time():  # 2 seconds
            time.sleep(1)

        # take-off in few secs
        me.takeoff()

    # Drone sound while landing.
    def drone_power_down(self):
        sound = SoundLoader.load('power_down.wav')
        if sound:
            # Playing while landing.
            sound.play()

        # Using a thread to simulate landing
        myThread = threading.Thread(target=self.land_drone)
        myThread.start()

    # drone-landing function:-
    def land_drone(self):
        # Landing the drone
        timing = time.time()
        while timing + 3 > time.time():  # 3 seconds
            time.sleep(1)

        # land in a few secs
        me.land()

    # Capture sound:
    def capture_sound(self):
        sound = SoundLoader.load('camera-shutter.mp3')
        if sound:
            # Playing while image-capture.
            sound.play()

        # Battery-label : Angle-adjustment (On-button click):-
        self.label_angle = battery * 3.6
        self.label_angle = round(self.label_angle)

    # Sound when switch is clicked
    def switch_sound(self):
        sound2 = SoundLoader.load('button-click.wav')
        if sound2:
            # Playing while image-capture.
            sound2.play()

    # Drone-blinking function:
    def drone_animate(self, *args):
        if self.drone_blink_rate:
            Clock.schedule_once(self.drone_animate, timeout=2)
            widget = self.ids.drone_button
            anim = Animation(animated_color=(0, 1, 0, 0), blink_size=350)
            anim.bind(on_complete=self.reset)
            anim.start(widget)

    # Detect-icon enable border-colour:
    def detect_animate(self):
        widget = self.ids.detect_button
        anim = Animation(animated_color=(0, 1, 0, 0), blink_size=350)
        anim.bind(on_complete=self.reset)
        anim.start(widget)

    # Dummy func for drone
    def drone_func(self):
        # enabling the on-button:
        self.power_button_enabled = True
        self.drone_blink_rate = False

        # Enabling exit:-
        self.exit_bool = False

        # Battery-label : Angle-adjustment (On-button click):-
        self.label_angle = battery * 3.6
        self.label_angle = round(self.label_angle)

    # Default button func for control keys
    def button_def(self):
        pass

    # For getting final border blue.
    def blue_border(self, *args):
        widget = args[1]
        widget.animated_color = (0, 0, 1, 1)
        widget.blink_size = 0

    # For getting final border red
    def red_border(self, *args):
        widget = args[1]
        widget.animated_color = (0.6, 0, 0, 1)
        widget.blink_size = 0

    # For getting final border green
    def green_border(self, *args):
        widget = args[1]
        widget.animated_color = (0, 1, 0, 1)
        widget.blink_size = 0

    # For animating drone-button while disabling or landing
    def drone_button_disable(self, widget):
        anim = Animation(animated_color=(0, 0, 1, 0), blink_size=350)
        anim.bind(on_complete=self.blue_border)
        anim.start(widget)

    # For diabling-animation of power button after take-off
    def power_button_disable(self):

        widget = self.ids.power_button
        anim = Animation(animated_color=(0.5, 0, 0, 0), blink_size=350)
        anim.bind(on_complete=self.red_border)
        anim.start(widget)

    # For enabling power-button after landing
    def power_button_enable(self):
        widget = self.ids.power_button
        anim = Animation(animated_color=(0, 1, 0, 0), blink_size=200)
        anim.bind(on_complete=self.green_border)
        anim.start(widget)

    # Pop-up [flight-controls]
    def flight_popup(self):
        the_popup = flight_popUp()
        the_popup.open()

        # Battery-label : Angle-adjustment (On-button click):-
        self.label_angle = battery * 3.6
        self.label_angle = round(self.label_angle)

    # Remote-icon animation:-
    def control_button(self, widget):
        anim = Animation(animated_color=(0, 0, 1, 0), blink_size=350)
        anim.bind(on_complete=self.blue_border)
        anim.start(widget)

    # Sound animation for control button:-
    def control_sound(self):
        sound = SoundLoader.load('control_sound.wav')
        if sound:
            # Playing while landing.
            sound.play()

    # Detection pop-up:
    def detect_popUp(self):
        self.popUp = detect_pop_Up()
        self.popUp.open()

    # Putting detection:POP-UP IN AUTO DISMISS
    def process_button_click(self):
        # Open the pop up
        self.detect_popUp()

        # Using a thread to simulate this
        mythread = threading.Thread(target=self.func_3_secs)
        mythread.start()

    def func_3_secs(self):
        thistime = time.time()
        while thistime + 3 > time.time():  # 3 seconds
            time.sleep(1)

        # Once the long running task is done, close the pop up.
        self.popUp.dismiss()

    # Drone-feed waiting pop-up:
    def cam_feed(self):
        self.popUp2 = cam_pop_Up()
        self.popUp2.open()

    # Putting drone_feed:POP-UP IN AUTO DISMISS
    def process_button_click2(self):
        # Open the pop up
        self.cam_feed()

        # Using a thread to simulate this
        mythread = threading.Thread(target=self.func_few_secs)
        mythread.start()

    def func_few_secs(self):
        thistime = time.time()
        while thistime + 2 > time.time():  # 2 seconds
            time.sleep(1)

        # Once the long running task is done, closing the pop up.
        self.popUp2.dismiss()

    # Exit-page:
    def open_exit_page(self):
        self.manager.current = 'exitPage2'
        self.manager.transition.direction = 'left'


# running the main method.
if __name__ == '__main__':
    Recon_Bird().run()
