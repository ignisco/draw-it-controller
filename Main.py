import pygame as pg
import numpy as np
import Prompt

pg.init()
pg.joystick.init()
scale = 1.5
win_size = (np.array((800, 600)) * scale).astype(int)
win = pg.display.set_mode(win_size)
pg.display.set_caption("Draw It - Controller Edition")
icon = pg.image.load("icon.png")
pg.display.set_icon(icon)
clock = pg.time.Clock()

keydict = {
            pg.K_w: (0, -1),
            pg.K_a: (-1, 0),
            pg.K_s: (0, 1),
            pg.K_d: (1, 0),
            }

colors = {
            "White": (255, 255, 255),
            "Yellow": (255, 255, 0),
            "Orange": (255, 102, 0),
            "Red": (221, 0, 0),
            "Pink": (255, 0, 153),
            "Purple": (51, 0, 153),
            "Blue": (0, 0, 204),
            "Light Blue": (0, 153, 255),
            "Light Green": (0, 170, 0),
            "Green": (0, 102, 0),
            "Dark Brown": (102, 51, 0),
            "Brown": (153, 102, 51),
            "Light Grey": (187, 187, 187),
            "Grey": (136, 136, 136),
            "Dark Grey": (68, 68, 68),
            "Black": (0, 0, 0)
         }

color_list = list(colors.values())

win_color = 7
win.fill(color_list[win_color])

eraser_img = pg.image.load("eraser.png")


def update_win_color():
    global win_color
    win_color %= len(color_list)
    win.fill(color_list[win_color])
    drawings.append(win.copy())


try:
    joystick = pg.joystick.Joystick(0)
    joystick.init()
except pg.error:
    print("No controller detected!")
    running = False


class Player:

    def __init__(self, size, is_ghost=False):
        self.freeze = False
        self.buttons_pressed = []
        self.hats_pressed = False
        self.active = True
        self.equal_scale = False
        self.erase_mode = False
        self.pos = (0, 0)
        self.org_speed = 3
        self.speed = 3
        self.size_speed = 3
        self.org_size = size
        self.size = size
        self.color_value = 0
        self.color = color_list[self.color_value]
        if not is_ghost:
            self.ghost = Player(size, True)
            self.ghost.color = color_list[win_color]

    def update(self):
        if self.freeze:
            return
        self.joystick_movement()
        self.joystick_buttons()
        self.joystick_size()

    def update_color(self):
        self.color_value %= len(color_list)
        self.color = color_list[self.color_value]

    def joystick_movement(self):
        movement = [0, 0]
        for i in range(2):
            movement[i] = joystick.get_axis(i)
        if max([abs(value) for value in movement]) < 0.05:
            return  # Small values are sometimes registered when controller is untouched. Prevented by this if-statement
        self.pos = tuple(np.array(self.pos) + np.array(movement) * self.speed)

    def joystick_size(self):
        size = [1, -1]
        for i in range(2):
            size[i] *= joystick.get_axis(i + 2)
        highest_reading = max([abs(value) for value in size])
        if highest_reading < 0.05:
            return  # Small values are sometimes registered when controller is untouched. Prevented by this if-statement
        if self.equal_scale:
            value = sum(size) / 2
            for i in range(2):
                size[i] = value

        added_size = np.array(size) * self.size_speed
        self.pos = tuple(np.array(self.pos) - added_size/2)
        self.size = (np.array(self.size) + added_size)
        self.size = tuple(map(abs, self.size))
        # self.speed = self.org_speed * self.size[0] / self.org_size[0]

    def joystick_buttons(self):

        if joystick.get_button(1):  # X on PS4 controller
            self.active = True
            if self.color not in color_list:
                self.color = color_list[self.color_value]

            if 1 not in self.buttons_pressed:
                self.buttons_pressed.append(1)
        else:
            self.active = False
            if self.color in color_list:
                dark_color = []
                for value in self.color:
                    if value - 20 < 0:
                        dark_color.append(0)
                    else:
                        dark_color.append(value - 20)
                self.color = tuple(dark_color)

        if joystick.get_button(2):  # O on PS4 controller
            self.erase_mode = True

        if joystick.get_button(0) and 0 not in self.buttons_pressed:  # Square on PS4 controller
            if len(drawings) > 1:
                drawings.pop(-1)
                self.buttons_pressed.append(0)

        if joystick.get_button(5):  # R1 on PS4 controller
            closest_rect_size = sum(self.size)/len(self.size)
            self.size = (closest_rect_size, closest_rect_size)

        if joystick.get_button(4) and 4 not in self.buttons_pressed: # L1 on PS4 Controller
            self.equal_scale = True
            self.buttons_pressed.append(4)

        for i in range(6, 8):

            if joystick.get_button(i) and i not in self.buttons_pressed:
                self.speed *= 2
                self.buttons_pressed.append(i)

        if joystick.get_button(8):  # Share on PS4 controller
            global prompt
            prompt_pos = (win_size[0] / 2, win_size[1] / 3)
            prompt_size = (160, 90)
            button_yes = Prompt.Button((prompt_pos[0] - prompt_size[0] * 0.1, prompt_pos[1] + prompt_size[1] * 0.8),
                                       (32, 18), "Yes")
            input_field = Prompt.InputField((prompt_pos[0] - prompt_size[0] * 0.4, prompt_pos[1] - prompt_size[1] * 0), "Drawing.png")
            prompt = (Prompt.Prompt(prompt_pos, prompt_size, "Would you like to save?", (button_yes,), input_field))

            self.freeze = True

        hat = joystick.get_hat(0)
        if abs(hat[0]) and not self.hats_pressed:
            self.color_value += hat[0]
            self.update_color()
        elif abs(hat[1]) and not self.hats_pressed:
            global win_color
            win_color += hat[1]
            update_win_color()
            self.ghost.color = color_list[win_color]
        if abs(hat[0]) or abs(hat[1]):
            self.hats_pressed = True
        else:
            self.hats_pressed = False

        for button in self.buttons_pressed:
            if not joystick.get_button(button):
                self.buttons_pressed.remove(button)
                if button in (6, 7):
                    self.speed /= 2
                if button == 4:
                    self.equal_scale = False

                if button == 1:
                    drawings.append(win.copy())

    def draw(self):
        global drawings, drawing
        if not self.active and not self.erase_mode:
            drawing = False
        else:
            drawing = True

        if self.erase_mode:
            pg.draw.rect(win, self.ghost.color, self.ghost.pos + self.ghost.size)
            if joystick.get_button(2):
                eraser = eraser_img.copy()
                eraser = pg.transform.scale(eraser, tuple(int(i) for i in self.size))
                win.blit(eraser, self.pos + self.size)
            else:
                drawings.append(win.copy())
                self.erase_mode = False
        else:
            pg.draw.rect(win, self.color, self.pos + self.size)
        self.ghost.pos = self.pos
        self.ghost.size = self.size


objects = [Player((20, 20))]
prompt = None
running = True
drawing = False
drawings = [win.copy()]


while running:
    events = pg.event.get()[:]
    for event in events:
        if event.type == pg.QUIT:
            running = False
            break
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
                break
            if event.key == pg.K_c:
                update_win_color()

            if prompt:
                if event.key == pg.K_DELETE:
                    prompt.input_field.text = ""
                elif event.key == pg.K_BACKSPACE:
                    prompt.input_field.text = prompt.input_field.text[0:-1]
                elif event.key == pg.K_RETURN:
                    prompt.save_image()
                else:
                    prompt.input_field.text += event.unicode

    # Drawing

    if len(drawings) > 0 and not drawing:
        win.blit(drawings[-1], (0, 0))

    for object in objects:
        object.update()
        object.draw()

    if prompt:
        prompt.update()
        prompt.draw(win)

        if prompt.action:
            if "c_save" in prompt.action:
                location = "".join(prompt.action.split("c_save "))
                pg.image.save(drawings[-1], location)
            prompt = None
            for object in objects:
                object.freeze = False

    pg.display.flip()
    clock.tick(60)

pg.quit()



