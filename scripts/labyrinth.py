from scripts.constants import DRAW_PRESCALER, LABYRINTH_WALL_SIZE, TOTAL_SIZE, LABYRINTH_SIZE
from scripts.robot_model import Point2D
from typing import List, cast
import easygraphics as graphics
import copy
import math


class Wall:
    exists: bool
    vert_horiz: str
    location: Point2D
    wall_width: float = 2

    def __init__(self, vert_horiz: str = 'h'):
        p = Point2D(0, 0)
        self.location = p
        if vert_horiz != 'h' and vert_horiz != 'v':
            raise ValueError("can be only h or v")
        self.vert_horiz = vert_horiz


class Labyrinth:
    map: List[List[Wall]]

    def __init__(self):
        self.map = []
        for row_idx in range(2 * LABYRINTH_SIZE + 1):
            row = []
            for col_idx in range(LABYRINTH_SIZE + 1):
                wall = Wall()
                wall.exists = True
                row.append(wall)
            self.map.append(row)

    def read_map(self, map_file: str):
        try:
            file = open(map_file, 'r')
        except IOError:
            print("File not found or path is incorrect")
            return None
        ind = 0
        for i in range(2 * LABYRINTH_SIZE + 1):
            line = file.readline()
            for j in range(LABYRINTH_SIZE + 1):
                ind += 1
                if not i % 2:
                    self.map[i][j].vert_horiz = 'h'
                    self.map[i][j].location.y = i / 2 * LABYRINTH_WALL_SIZE
                    self.map[i][j].location.x = LABYRINTH_WALL_SIZE / 2 + j * LABYRINTH_WALL_SIZE
                else:
                    self.map[i][j].vert_horiz = 'v'
                    self.map[i][j].location.y = i / 2 * LABYRINTH_WALL_SIZE
                    self.map[i][j].location.x = j * LABYRINTH_WALL_SIZE
                if line[j] == '0':
                    self.map[i][j].exists = False
                else:
                    self.map[i][j].exists = True
        file.close()

    def print_map(self):
        for walls in self.map:
            for wall in walls:
                print(wall.vert_horiz, end=' ')
            print('')


class MapEditor:
    lab: Labyrinth

    def __init__(self, lab: Labyrinth):
        self.lab = copy.deepcopy(lab)

    def edit_map(self):
        closest = math.inf
        clo_i = 0
        clo_j = 0
        x, y = graphics.get_cursor_pos()
        for i in range(2 * LABYRINTH_SIZE + 1):
            for j in range(LABYRINTH_SIZE + 1):
                dis_x_y = ((self.lab.map[i][j].location.x * DRAW_PRESCALER - x) ** 2 + (
                        self.lab.map[i][j].location.y * DRAW_PRESCALER - y) ** 2) ** (1 / 2)
                if dis_x_y < closest:
                    closest = min(dis_x_y, closest)
                    clo_i = i
                    clo_j = j
        color = graphics.get_fill_color()
        graphics.set_fill_color(graphics.Color.DARK_RED)
        point = self.lab.map[clo_i][clo_j]
        where = Point2D(point.location.x * DRAW_PRESCALER, point.location.y * DRAW_PRESCALER)
        if closest < LABYRINTH_WALL_SIZE / 3 * DRAW_PRESCALER:
            graphics.fill_circle(where.x, where.y, 5)
        graphics.set_fill_color(color)
        if graphics.has_mouse_msg():
            msg = graphics.get_mouse_msg()
            if msg.type == graphics.MouseMessageType.PRESS_MESSAGE and closest < LABYRINTH_WALL_SIZE / 3 * DRAW_PRESCALER:
                if self.lab.map[clo_i][clo_j].exists:
                    self.lab.map[clo_i][clo_j].exists = False
                else:
                    self.lab.map[clo_i][clo_j].exists = True

    def save_map(self, path: str):
        file = open(path, 'w')
        for i in range(2 * LABYRINTH_SIZE + 1):
            line = ""
            for j in range(LABYRINTH_SIZE + 1):
                if not self.lab.map[i][j].exists:
                    line += "0"
                else:
                    line += "W"
            line += "\n"
            file.write(line)
        file.close()
