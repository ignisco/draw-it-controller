import pygame as pg
import numpy as np

pg.init()
pg.joystick.init()
scale = 1.5
win_size = (np.array((800, 600)) * scale).astype(int)
win = pg.display.set_mode(win_size)
move_surface = pg.surface.Surface(win_size)
clock = pg.time.Clock()

keydict = {
            pg.K_w: (0, -1),
            pg.K_a: (-1, 0),
            pg.K_s: (0, 1),
            pg.K_d: (1, 0),
            }
try:
    joystick = pg.joystick.Joystick(0)
    joystick.init()
except pg.error:
    print("No controller detected!")
    running = False


class Player:

    def __init__(self, size, is_ghost=False):
        self.buttons_pressed = []
        self.active = True
        self.pos = (0, 0)
        self.speed = 3
        self.size_speed = 3
        self.size = size
        self.colors = [(150, 0, 0), (255, 0, 0)]
        self.color = self.colors[self.active]
        if not is_ghost:
            self.ghost = Player(size, True)
            self.ghost.color = ((0, 0, 0),)

    def update(self):
        self.joystick_movement()
        self.joystick_buttons()
        self.joystick_size()

    def joystick_movement(self):
        movement = [0, 0]
        for i in range(2):
            movement[i] = joystick.get_axis(i)
        if max([abs(value) for value in movement]) < 0.05:
            return  # Small values are sometimes registered when controller is untouched. Prevented by this if-statement
        self.pos = tuple(np.array(self.pos) + np.array(movement) * self.speed)

    def joystick_size(self):
        size = [0, 0]
        for i in range(2):
            size[i] = joystick.get_axis(i + 2)
        if max([abs(value) for value in size]) < 0.05:
            return  # Small values are sometimes registered when controller is untouched. Prevented by this if-statement
        added_size = np.array(size) * self.size_speed
        self.pos = tuple(np.array(self.pos) - added_size/2)
        self.size = (np.array(self.size) + added_size)
        self.size = tuple(map(abs, self.size))

    def joystick_buttons(self):

        if joystick.get_button(1): # X on PS4 controller
            self.active = True
            self.color = self.colors[self.active]
        else:
            self.active = False
            self.color = self.colors[self.active]

        for button in self.buttons_pressed:
            if not joystick.get_button(button):
                self.buttons_pressed.remove(button)

    def draw(self):
        if not self.active:
            pg.draw.rect(move_surface, self.ghost.color, self.ghost.pos + self.ghost.size)
            pg.draw.rect(move_surface, self.color, self.pos + self.size)
        else:
            pg.draw.rect(win, self.color, self.pos + self.size)
        self.ghost.pos = self.pos
        self.ghost.size = self.size


objects = [Player((20, 20))]
running = True
while running:
    events = pg.event.get()[:]
    for event in events:
        if event.type == pg.QUIT:
            running = False;
            break
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
                break
            if event.key == pg.K_c:
                win.fill((0,0,0))

    # Drawing

    for object in objects:
        object.update()
        object.draw()

    win.blit(move_surface, (0, 0))
    pg.display.flip()
    clock.tick(60)

pg.quit()



