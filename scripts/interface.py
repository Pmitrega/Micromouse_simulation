from scripts.labyrinth import Labyrinth, MapEditor
from scripts.robot_model import Robot, Point2D
from scripts.control import LabRobInterface
from scripts.control import Control
import scripts.draw as draw
import enum
from typing import Tuple, List
import easygraphics as graphics
import easygraphics.dialog as dialog
import threading
import math
from scripts.constants import DRAW_PRESCALER, LABYRINTH_WALL_SIZE, TOTAL_SIZE, LABYRINTH_SIZE


class RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class Mode(enum.Enum):
    START = 0
    MENU = 1
    EDITOR = 2
    SIMULATION = 3


class Menu:
    gap = 3
    offset: Point2D
    size: Point2D
    options: List[str]
    modes: List[Mode]

    def __init__(self):
        self.options = ["Edit map", "Start simulation"]
        self.modes = [Mode.EDITOR, Mode.SIMULATION]
        self.size = Point2D(300, 80)
        self.offset = Point2D(800 - self.size.x / 2, 100)


class Interface:
    controller: Control
    lab: Labyrinth
    robot: Robot
    editor: MapEditor
    menu: Menu
    timer: threading.Timer
    mode: Mode = Mode.START
    end_flag = False

    def __init__(self, lab: Labyrinth, robot: Robot):
        self.lab = lab
        self.robot = robot
        self.menu = Menu()
        self.editor = MapEditor(lab)
        self.img = None
        self.controller = Control(robot, lab)
        self.timer = RepeatTimer(0.02, self.controller.control_task)
        self.timer2 = RepeatTimer(0.02, self.controller.read_sensors)

    def begin(self):
        self.img = graphics.create_image_from_file("vriskers-700x451.jpg")
        graphics.init_graph(1600, 900)
        graphics.set_render_mode(graphics.RenderMode.RENDER_MANUAL)
        self.mode = Mode.MENU
        self.loop()
        graphics.close_graph()

    def perform_menu_tasks(self):
        graphics.draw_image(0, 0, self.img)
        x, y = graphics.get_cursor_pos()
        draw.draw_menu(self.menu)
        self.img = graphics.create_image_from_file("vriskers-700x451.jpg")
        if graphics.has_mouse_msg():
            msg = graphics.get_mouse_msg()
            if msg.type == graphics.MouseMessageType.PRESS_MESSAGE:
                for i in range(len(self.menu.options)):
                    if self.menu.offset.x < x < (self.menu.offset.x + self.menu.size.x) and (
                            self.menu.offset.y + self.menu.gap * i + self.menu.size.y * i) < y < (
                            self.menu.offset.y + self.menu.size.y * (i + 1) + self.menu.gap * i):
                        self.mode = self.menu.modes[i]

    def perform_editor_tasks(self):
        graphics.fill_image(graphics.Color.BLACK)
        draw.draw_map(self.editor.lab, graphics.Color.DARK_GREEN)
        draw.draw_mess_editor()
        self.editor.edit_map()
        if graphics.has_kb_hit():
            key = graphics.get_char()
            if key == 's':
                name = dialog.get_string("Enter name of file", default_response="map.txt", title="Save map")
                if name is not None:
                    try:
                        self.editor.save_map(name)
                        dialog.show_message("Saved successfully")
                    except:
                        dialog.show_message("failed to save file")

            if key == 'x':
                self.mode = Mode.MENU

    def perform_simulation_tasks(self):
        name = "map.txt"
        graphics.fill_image(graphics.Color.BLACK)
        draw.draw_mess_sim(self.controller.sim_time)
        draw.draw_map(self.lab)
        draw.draw_robot(self.robot)
        readings = []
        readings, starts, ends = LabRobInterface.read_all_sensors(self.robot, self.lab)
        draw.draw_sensors_lines(starts, ends)
        if graphics.has_kb_hit():
            key = graphics.get_char()
            if key == 'l':
                name = dialog.get_string("Enter name of file", default_response="map.txt", title="Load map")
                if name is not None:
                    self.lab.read_map(name)
            if key == 'x':
                self.mode = Mode.MENU
            if key == 'r':
                self.controller.task = 0
                self.controller.is_on = False
                self.controller.reset()
            if key == 's':
                if not self.timer.is_alive():
                    self.timer.start()
                    self.timer2.start()
                    self.controller.is_on = True
                elif not self.controller.is_on:
                    self.controller.is_on = True
                else:
                    self.controller.is_on = False

    def loop(self):
        while graphics.is_run():
            if graphics.delay_jfps(60, 0):
                if self.mode == Mode.MENU:
                    self.perform_menu_tasks()
                elif self.mode == Mode.EDITOR:
                    self.perform_editor_tasks()
                elif self.mode == Mode.SIMULATION:
                    self.perform_simulation_tasks()
