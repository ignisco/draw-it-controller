import pygame as pg
import numpy as np

pg.init()
pg.joystick.init()
joystick = pg.joystick.Joystick(0)
joystick.init()


class Prompt:
    def __init__(self, pos, size, text, buttons, input_field=None):
        self.action = None
        self.hats_pressed = False
        self.active_button = 0
        self.pos = tuple(np.array(pos) - np.array(size) / 2)
        self.size = size
        self.buttons = buttons
        self.input_field = input_field
        self.font = pg.font.Font(None, 20)
        self.textBitmap = self.font.render(text, True, (0, 0, 0))

    def draw(self, screen):
        pg.draw.rect(screen, (255, 255, 255), self.pos + self.size)
        screen.blit(self.textBitmap, (self.pos[0] + 10, self.pos[1] + 10))
        for idx, button in enumerate(self.buttons):
            if idx == self.active_button:
                button.mark()
            else:
                button.unmark()
            button.draw(screen)

        if self.input_field:
            self.input_field.draw(screen)

    def update(self):
        hat = joystick.get_hat(0)
        if abs(hat[0]) and not self.hats_pressed:
            self.active_button += hat[0]
            self.active_button %= len(self.buttons)
            self.hats_pressed = True
        elif not abs(hat[0]):
            self.hats_pressed = False

        if joystick.get_button(1):  # X on PS4 controller
            self.save_image()

        if joystick.get_button(2):  # O on PS4 controller
            self.action = "delete"

        if self.input_field:
            self.input_field.update()

    def save_image(self):
        if self.buttons[self.active_button].text == "Yes":
            self.action = "c_save " + self.input_field.text
            if "." not in self.input_field.text:
                self.action += ".png"


class Button:
    def __init__(self, pos, size, text):
        self.pos = pos
        self.text = text
        self.size = size
        self.color = (120, 120, 120)
        self.font = pg.font.Font(None, 20)
        self.textBitmap = self.font.render(text, True, (0, 0, 0))

    def draw(self, screen):
        pg.draw.rect(screen, self.color, self.pos + self.size)
        screen.blit(self.textBitmap, (self.pos[0] + 5, self.pos[1] + 2))

    def mark(self):
        self.color = (120, 240, 120)

    def unmark(self):
        self.color = (120, 120, 120)


class InputField:
    def __init__(self, pos, text):
        self.pos = pos
        self.text = text
        self.font = pg.font.Font(None, 30)

    def draw(self, screen):
        text_bitmap = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(text_bitmap, self.pos)

    def update(self):
        pass
