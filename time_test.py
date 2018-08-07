from kivy.app import runTouchApp
from kivy.uix.widget import Widget
from kivy.clock import Clock
from time import clock
from kivy.config import Config
Config.set('graphics', 'maxfps', '150')
Config.write()

class Events(Widget):

    trigger = None
    t = clock()
    f = []
    last_t = t

    def __init__(self, **kwargs):
        super(Events, self).__init__(**kwargs)
        self.f = []
        self.trigger = Clock.create_trigger(
            self.callback, timeout=0.001)
        self.trigger()

    def callback(self, *l):
        t = clock()
        self.f.append(1 / (t - self.t))
        if t - self.last_t >= 1.0:
            print('fps', sum(self.f) / max(1, len(self.f)))
            self.f = []
            self.last_t = t
        self.t = t
        self.trigger()

runTouchApp(Events())