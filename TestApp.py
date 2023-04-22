import kivy.core.text
import cv2
from kivy.app import App
from kivy.base import EventLoop
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget

from Detector import *


from kivymd.app import MDApp


class KivyCamera(Image):

    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = None

    def start(self, capture, fps=30):
        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)

    def stop(self):
        Clock.unschedule_interval(self.update)
        self.capture = None

    def update(self, dt):
        return_value, frame = self.capture.read()
        if return_value:
            texture = self.texture
            w, h = frame.shape[1], frame.shape[0]
            if not texture or texture.width != w or texture.height != h:
                self.texture = texture = Texture.create(size=(w, h))
                texture.flip_vertical()
            texture.blit_buffer(frame.tobytes(), colorfmt='bgr')
            self.canvas.ask_update()


capture = None


class QrtestHome(BoxLayout):

    def init_qrtest(self):
        pass

    def dostart(self, *largs):
        global capture
        capture = cv2.VideoCapture(0)
        self.ids.qrcam.start(capture)

    def doexit(self):
        global capture
        if capture != None:
            capture.release()
            capture = None
        EventLoop.close()


class qrtestApp(App):

    def build(self):
        Window.clearcolor = (.4,.4,.4,1)
        Window.size = (800, 800)
        homeWin = QrtestHome()
        homeWin.init_qrtest()
        return homeWin

    def on_stop(self):
        global capture
        if capture:
            capture.release()
            capture = None


class CamApp(App):
    def build(self):
        self.img1 = Image()
        layout = BoxLayout()
        layout.add_widget(self.img1)
        # opencv2 stuffs
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 33.0)
        return layout

    def update(self, dt):
        # display image from cam in opencv window
        ret, frame = self.capture.read()
        cv2.putText(frame, "Hello, this is the test", (90, 90), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 2)

        # convert it to texture
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        # if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer.
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.img1.texture = texture1

class MyWidget(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        index = keycode[0]
        #print(keycode)
        if index == 119:
            print("move forward")
        if index == 115:
            print('move back')
        if index == 100:
            print('go right')
        if index == 97:
            print('go left')

        if index == 273:
            print('hover up')
        if index == 274:
            print('hover down')
        if index == 276:
            print('yaw left')
        if index == 275:
            print('yaw right')


class testClass(Screen):
    def def_button(self):
        pass

    def open_exit_page(self):
        self.manager.current = 'exitPage'
        self.manager.transition.direction = 'left'


class testApp(App):
    def build(self):
        wm = ScreenManager()
        wm.add_widget(testClass(name='main_window'))
        wm.add_widget(newClass(name='second_window'))
        wm.add_widget(exit_page(name='exitPage'))
        return wm


class newClass(Screen):
    pass


class exit_page(Screen,MDApp):
    # Closing the window
    def win_button_yes(self):
        Window.close()

    # Transitioning the window to previous
    def win_button_no(self):
        self.manager.current = 'main_window'


#qrtestApp().run()
if __name__ == '__main__':
    testApp().run()