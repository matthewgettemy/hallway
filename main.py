
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ListProperty

import os
import shelve
import random

Config.set('graphics', 'maxfps', '150')
Config.write()

if platform == 'android':
    Window.fullscreen = True
else:
    Window.size = (450,800)

WIDTH_IN_BLOCKS = 18
BLOCK_SIZE_PIXELS = Window.width / WIDTH_IN_BLOCKS
HEIGHT_IN_BLOCKS = int(Window.height/BLOCK_SIZE_PIXELS)

class Background(Widget):

    v = ListProperty([])

    def __init__(self):
        super(Background, self).__init__()
        self.v = [.4,.4,.4]
        self.bind(v=self.update_background_color)
        with self.canvas:
            Color(self.v[0], self.v[1], self.v[2])
            #Rectangle(source=self.image,
            #          size=(Window.width, Window.height))
            Rectangle(size=(Window.width, Window.height))

    def update_background_color(self, instance, value):
        canvas_after = self.canvas.after
        canvas_after.clear()
        with canvas_after:
            Color(value[0], value[1], value[2])
            Rectangle(size=(Window.width, Window.height))

class HallwayWall(Widget):
    def __init__(self, size, pos):
        super(HallwayWall, self).__init__()
        self.size = size
        self.pos = pos
        with self.canvas:
            Color(0,.2,1)
            self.rect = Rectangle(size=self.size,
                                  pos=self.pos)
            self.bind(pos=self.update_rectangle)

    def update_rectangle(self, instance, value):
        self.rect.pos = value


class HallwayController(Widget):
    def __init__(self):
        super(HallwayController, self).__init__()
        self.right_walls = []
        self.left_walls = []

    def setup_opening(self, hallway_width_blocks):
        self.remove_walls(all=True)
        self.right_walls = []
        self.left_walls = []
        size = ((Window.width/2) - (hallway_width_blocks*BLOCK_SIZE_PIXELS/2),
                BLOCK_SIZE_PIXELS)

        for row in range(HEIGHT_IN_BLOCKS + 1):
            left_pos = (0, row * BLOCK_SIZE_PIXELS)
            right_pos = ((Window.width/2) + (hallway_width_blocks*BLOCK_SIZE_PIXELS/2),
                        row * BLOCK_SIZE_PIXELS)
            self.add_right_wall(size, right_pos)
            self.add_left_wall(size, left_pos)

    def add_right_wall(self, size, pos):
        wall = HallwayWall(size=size, pos=pos)
        self.right_walls.append(wall)
        self.add_widget(wall)

    def add_left_wall(self, size, pos):
        #if self.left_walls[-1].y < Window.height:
        wall = HallwayWall(size=size, pos=pos)
        self.left_walls.append(wall)
        self.add_widget(wall)

    def remove_walls(self, all=False):
        if all:
            for wall in self.right_walls + self.left_walls:
                self.remove_widget(wall)
        elif self.right_walls[0].y < 0:
            self.remove_widget(self.right_walls.pop(0))
            self.remove_widget(self.left_walls.pop(0))


    def move_walls(self, move_y):
        for right_wall, left_wall in zip(self.right_walls, self.left_walls):
            right_wall.y = right_wall.y - move_y
            left_wall.y = left_wall.y - move_y

    def check_collision(self, widget):
        for wall in self.right_walls + self.left_walls:
            if wall.collide_widget(widget):
                return True, wall
        return False, None


class Hero(Widget):
    health_remaining = NumericProperty()
    def __init__(self):
        super(Hero, self).__init__()
        self.pos = (Window.width/2 - BLOCK_SIZE_PIXELS/2, Window.height/8)
        self.size = (BLOCK_SIZE_PIXELS, BLOCK_SIZE_PIXELS)
        self.health_remaining = Window.width / 2
        with self.canvas:
            Color(1,1,1,1)
            #self.opacity = 0.5
            self.rect = Rectangle(source='./racecar.png',
                                  size=self.size,
                                  pos=self.pos)
            Color(0, .5, 0)
            self.progress_bar = Rectangle(pos=(BLOCK_SIZE_PIXELS * 2, Window.height - (BLOCK_SIZE_PIXELS * 2)),
                                          size=(self.health_remaining, BLOCK_SIZE_PIXELS))
            self.bind(pos=self.update_graphics_pos)
            self.bind(health_remaining=self.update_progress_bar)

    def on_touch_move(self, touch):
        self.pos = (touch.x - self.size[0]/2,
                    touch.y - self.size[1]/2 + BLOCK_SIZE_PIXELS*2)

    def move(self, move):
        self.x += move*BLOCK_SIZE_PIXELS
        self.pos = (self.x, self.y)

    def update_graphics_pos(self, instance, value):
        self.rect.pos = value

    def update_progress_bar(self, instance, delta):
        self.progress_bar.size = (self.health_remaining, BLOCK_SIZE_PIXELS)

    def refill_health(self):
        self.health_remaining = Window.width/2

    def dead(self):
        state = False
        if self.health_remaining <= 0:
            state = True
        return state

class Score(Widget):

    def __init__(self, starting_score):
        super(Score, self).__init__()
        self.current_score = starting_score
        with self.canvas:
            self.score_label = Label(text='{}'.format(str(self.current_score).zfill(6)), font_size='35sp',
                                     font_name='./fonts/jackinput.ttf',
                                     size=(BLOCK_SIZE_PIXELS, BLOCK_SIZE_PIXELS),
                                     pos=((BLOCK_SIZE_PIXELS * 4), Window.height - (BLOCK_SIZE_PIXELS * 3.5)),
                                     halign="left", valign="bottom")
            #self.score_label.pos = (Window.width / 10, Window.height - (BLOCK_SIZE_PIXELS * 2))
            #self.score_label.x = Window.width - (self.score_label.width * 3)
            #self.score_label.y = Window.height - (self.score_label.height * 1.2)

            #pos = (Window.width / 10, Window.height - BLOCK_SIZE_PIXELS * 2),
            #size = (self.health_remaining, BLOCK_SIZE_PIXELS)

    def increment_score(self, increment):
        self.current_score += increment
        self.update_label()

    def set_score(self, num):
        self.current_score = num
        self.update_label()

    def update_label(self):
        self.score_label.text = str(self.current_score).zfill(6)

class ScoreTracker:

    def __init__(self, data_storage):
        self.number_scores_to_save = 5
        self.score_file_path = os.path.join(data_storage, 'highscores')
        self.score_file = shelve.open(self.score_file_path)

    def write_score(self, score_achieved):
        scores = self.read_scores()
        print(scores)
        scores.append(score_achieved)
        print(scores)
        scores.sort()
        print(scores)
        scores.pop(0)
        print('highscores: {}'.format(scores))
        self.score_file['scores'] = scores

    def read_scores(self):
        try:
            recorded_scores = self.score_file['scores']
        except KeyError:
            recorded_scores = [0]*self.number_scores_to_save
        return recorded_scores


class GUI(Widget):
    def __init__(self, title_screen, score_tracker, **kwargs):
        super(GUI, self).__init__(**kwargs)

        self.title_screen = title_screen
        self.score_tracker = score_tracker

        self.background = Background()
        self.hallway_controller = HallwayController()
        self.hero = Hero()
        self.score = Score(0)

        self.add_widget(self.background)
        self.add_widget(self.hallway_controller)
        self.add_widget(self.hero)
        self.add_widget(self.score)
        #self.add_widget(self.health)

        self.direction = -1
        self.hallway_width_blocks = 7
        self.hallway_width_pixels = self.hallway_width_blocks * BLOCK_SIZE_PIXELS
        #self.max_hallway_width_blocks = 12
        #self.min_hallway_width_blocks = 6

        self.previous_width = (WIDTH_IN_BLOCKS/2) - (self.hallway_width_blocks/2)
        self.max_hallway_shift_blocks = 1
        self.min_hallway_shift_blocks = 0

        self.last_touch = None
        self.update_event = None

        self.number_of_frames = 0
        self.base_interval = 20
        #self.trigger = Clock.create_trigger(self.update, timeout=0)
        #self.trigger()

        self.hallway_controller.setup_opening(self.hallway_width_blocks)

    #def on_touch_move(self, touch):
    #    self.last_touch = touch
        #for wall in self.hallway_controller.right_walls+self.hallway_controller.left_walls:
        #    if wall.collide_point(touch.x, touch.y):
        #        print(touch.x, touch.y)

    def reset(self):
        self.number_of_frames = 0
        self.background.v = [.4, .4, .4]
        self.update_event.cancel()
        self.previous_width = (WIDTH_IN_BLOCKS / 2) - (self.hallway_width_blocks / 2)
        self.hallway_controller.setup_opening(self.hallway_width_blocks)
        self.hero.refill_health()

        self.score_tracker.write_score(self.score.current_score)
        self.score.set_score(0)

    def on_touch_down(self, touch):
        self.title_screen.remove_title()
        #self.update_event = Clock.schedule_interval(self.update, 1.0 / 28.0)
        self.set_clock(1.0/self.base_interval)

    def set_clock(self, interval):
        if self.update_event:
            self.update_event.cancel()
        self.update_event = Clock.schedule_interval(self.update, interval)

    def on_touch_up(self, touch):
        self.reset()
        #self.update_event.cancel()
        #self.previous_width = (WIDTH_IN_BLOCKS / 2) - (self.hallway_width_blocks / 2)
        #self.hallway_controller.setup_opening(self.hallway_width_blocks)

    def on_touch_move(self, touch):
        self.last_touch = touch
        self.hero.on_touch_move(touch)

    def check_change_direction(self):
        # see if the path is close to the edge
        close_to_edge = self.distance_from_edge()
        self.min_hallway_shift_blocks = 0
        # see if the path needs to change direction
        if close_to_edge or (random.random() > 0.93):
            self.direction = self.direction * -1
            # if close to edge, change at least this many blocks
            self.min_hallway_shift_blocks = 1

    def distance_from_edge(self):
        return ((self.previous_width <= self.max_hallway_shift_blocks) or
                (self.previous_width >= (WIDTH_IN_BLOCKS -
                                         self.max_hallway_shift_blocks -
                                         self.hallway_width_blocks)))


    def update(self, dt):
        self.number_of_frames += 1
        frames_reduced = round(self.number_of_frames/100)
        self.set_clock(1/(self.base_interval + frames_reduced))
        self.background.v = [0.4,0.4,0.4]

        if self.last_touch:
            collision, wall_hit = self.hallway_controller.check_collision(self.hero)
            if collision:
                self.background.v = [1, 0, 0]
                #self.health.progress_bar.value -= 1
                #self.health.health_remaining -= BLOCK_SIZE_PIXELS/4
                self.hero.health_remaining -= BLOCK_SIZE_PIXELS/4

        self.score.increment_score(1)

        #check if dead, and reset if so
        if self.hero.dead():
            self.reset()
            #self.hero.refill_health()
            #self.hallway_controller.setup_opening(self.hallway_width_blocks)
            #self.previous_width = (WIDTH_IN_BLOCKS / 2) - (self.hallway_width_blocks / 2)


        self.check_change_direction()

        width_change = random.randint(self.min_hallway_shift_blocks, self.max_hallway_shift_blocks)*self.direction

        left_wall_x = 0
        left_wall_width_blocks = self.previous_width + width_change
        left_wall_width_pixels = left_wall_width_blocks * BLOCK_SIZE_PIXELS
        right_wall_x = left_wall_width_pixels + self.hallway_width_pixels
        right_wall_width = Window.width - right_wall_x

        #add the new walls
        self.hallway_controller.add_left_wall(size = (left_wall_width_pixels, BLOCK_SIZE_PIXELS),
                                              pos = (left_wall_x, Window.height))
        self.hallway_controller.add_right_wall(size = (right_wall_width, BLOCK_SIZE_PIXELS),
                                               pos = (right_wall_x, Window.height))
        #move the walls down and remove bottom ones
        self.hallway_controller.move_walls(BLOCK_SIZE_PIXELS)
        self.hallway_controller.remove_walls()
        #set the previous width
        self.previous_width = left_wall_width_blocks


class TitleScreen(Widget):

    def __init__(self):
        super(TitleScreen, self).__init__()
        self.title = 'TITLE'
        self.title_label = Label(text='{}'.format(self.title),
                                 font_size='30sp',
                                 color=[1,1,1,1],
                                 text_size=(Window.width, Window.height/10))
        self.title_label.x = Window.width/2
        self.title_label.y = Window.height/1.2
        #self.title_label.x = Window.width - (self.title_label.width * 3)
        #self.title_label.y = Window.height - (self.title_label.height * 1.2)
        self.add_widget(self.title_label)
        #with self.canvas:

    def remove_title(self):
        self.remove_widget(self.title_label)


class Application(App):
    """
    pass
    """
    def build(self):
        parent = Widget()
        data_storage = self.user_data_dir
        score_tracker = ScoreTracker(data_storage)
        title_screen = TitleScreen()


        gui = GUI(title_screen, score_tracker)
        #Clock.schedule_interval(gui.update, 1.0/28.0)
        parent.add_widget(gui)
        parent.add_widget(title_screen)
        #Clock.create_trigger(gui.update, timeout=0.0333)
        return parent
        #return Button(text='hello world')

if __name__ == '__main__' :
    Application().run()