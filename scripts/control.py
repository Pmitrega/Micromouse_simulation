from scripts.robot_model import Robot, Point2D
from scripts.labyrinth import Labyrinth
import math
from typing import List
from scripts.constants import DRAW_PRESCALER, LABYRINTH_WALL_SIZE, TOTAL_SIZE, LABYRINTH_SIZE


def is_in_range(v: float, rang: List[float]):
    if rang[0] <= v <= rang[1]:
        return True
    else:
        return False


def distance(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** (1 / 2)


class LabRobInterface:
    @staticmethod
    def where_facing_x(robot: Robot, index):
        sensor = robot.sensors[index]
        sensor_tot_fi = robot.rotation + sensor.fi
        from_0_360 = sensor_tot_fi % 360
        if from_0_360 < 180:
            return 1
        else:
            return -1

    def where_facing_y(robot: Robot, index):
        sensor = robot.sensors[index]
        sensor_tot_fi = robot.rotation + sensor.fi
        from_0_360 = sensor_tot_fi % 360
        if 90 < from_0_360 < 270:
            return 1
        else:
            return -1

    def is_facing_to_point(robot: Robot, x, y, index):
        sensor = robot.sensors[index]
        facing_x = LabRobInterface.where_facing_x(robot, index)
        facing_y = LabRobInterface.where_facing_y(robot, index)
        sensor_tot_fi = robot.rotation + sensor.fi
        tot_rel_x = sensor.rel_loc.x * math.cos(math.radians(robot.rotation)) - sensor.rel_loc.y * math.sin(
            math.radians(robot.rotation))
        tot_rel_y = sensor.rel_loc.x * math.sin(math.radians(robot.rotation)) + sensor.rel_loc.y * math.cos(
            math.radians(robot.rotation))
        tot_loc_y = tot_rel_y + robot.location.y
        tot_loc_x = tot_rel_x + robot.location.x
        if (x - tot_loc_x) * facing_x > 0 and (y - tot_loc_y) * facing_y > 0:
            return True
        else:
            return False

    ## I made a monster
    @staticmethod
    def get_sensor_reading(robot: Robot, lab: Labyrinth, index):
        sensor = robot.sensors[index]
        sensor_tot_fi = robot.rotation + sensor.fi
        if not sensor_tot_fi % 180:
            robot.rotation += 0.001
            sensor_tot_fi = robot.rotation + sensor.fi

        tot_rel_x = sensor.rel_loc.x * math.cos(math.radians(robot.rotation)) - sensor.rel_loc.y * math.sin(
            math.radians(robot.rotation))
        tot_rel_y = sensor.rel_loc.x * math.sin(math.radians(robot.rotation)) + sensor.rel_loc.y * math.cos(
            math.radians(robot.rotation))

        tot_loc_y = tot_rel_y + robot.location.y
        tot_loc_x = tot_rel_x + robot.location.x
        b = 0

        a = -1 / math.tan(math.radians(sensor_tot_fi))
        if sensor_tot_fi % 180:
            b = tot_loc_y - a * tot_loc_x

        y_f = lambda x: a * x + b
        x_f = lambda y: (y - b) / a
        width = lab.map[0][0].wall_width
        min_distance = math.inf
        y0_0 = math.inf
        y0_1 = math.inf
        x0_0 = math.inf
        x0_1 = math.inf
        min_point = Point2D(0, 0)
        for i in range(len(lab.map)):
            for j in range(len(lab.map[0])):
                loc_x = lab.map[i][j].location.x
                loc_y = lab.map[i][j].location.y
                if lab.map[i][j].exists and lab.map[i][j].vert_horiz == 'h':
                    x_range = [loc_x - LABYRINTH_WALL_SIZE / 2, loc_x + LABYRINTH_WALL_SIZE / 2]
                    y_range = [loc_y - width / 2, width / 2 + loc_y]
                    y0_0 = loc_y - width / 2
                    y0_1 = loc_y + width / 2
                    x0_0 = loc_x - LABYRINTH_WALL_SIZE / 2
                    x0_1 = loc_x + LABYRINTH_WALL_SIZE / 2
                elif lab.map[i][j].exists and lab.map[i][j].vert_horiz == 'v':
                    x_range = [loc_x - width / 2, loc_x + width / 2]
                    y_range = [loc_y - LABYRINTH_WALL_SIZE / 2, loc_y + LABYRINTH_WALL_SIZE / 2]
                    y0_0 = loc_y - LABYRINTH_WALL_SIZE / 2
                    y0_1 = loc_y + LABYRINTH_WALL_SIZE / 2
                    x0_0 = loc_x - width / 2
                    x0_1 = loc_x + width / 2
                else:
                    x_range = [0, 0]
                    y_range = [0, 0]

                if lab.map[i][j].exists:
                    lmd = min_distance
                    if is_in_range(y_f(x0_0), y_range) and is_in_range(x0_0,
                                                                       x_range) and LabRobInterface.is_facing_to_point(
                        robot, x0_0, y_f(x0_0), index):
                        min_distance = min(min_distance, distance(tot_loc_x, tot_loc_y, x0_0, y_f(x0_0)))
                    if min_distance != lmd:
                        min_point.x = x0_0

                    lmd = min_distance
                    if is_in_range(y_f(x0_1), y_range) and is_in_range(x0_1,
                                                                       x_range) and LabRobInterface.is_facing_to_point(
                        robot, x0_1, y_f(x0_1), index):
                        min_distance = min(min_distance, distance(tot_loc_x, tot_loc_y, x0_1, y_f(x0_1)))
                    if min_distance != lmd:
                        min_point.x = x0_1

                    lmd = min_distance
                    if is_in_range(y0_0, y_range) and is_in_range(x_f(y0_0),
                                                                  x_range) and LabRobInterface.is_facing_to_point(robot,
                                                                                                                  x_f(y0_0),
                                                                                                                  y0_0,
                                                                                                                  index):
                        min_distance = min(min_distance, distance(tot_loc_x, tot_loc_y, x_f(y0_0), y0_0))
                    if min_distance != lmd:
                        min_point.x = x_f(y0_0)

                    lmd = min_distance
                    if is_in_range(y0_1, y_range) and is_in_range(x_f(y0_1),
                                                                  x_range) and LabRobInterface.is_facing_to_point(robot,
                                                                                                                  x_f(y0_1),
                                                                                                                  y0_1,
                                                                                                                  index):
                        min_distance = min(min_distance, distance(tot_loc_x, tot_loc_y, x_f(y0_1), y0_1))
                    if min_distance != lmd:
                        min_point.x = x_f(y0_1)

        min_point.y = y_f(min_point.x)
        start = Point2D(tot_loc_x, tot_loc_y)
        return min_distance, start, min_point

    @staticmethod
    def read_all_sensors(robot: Robot, lab: Labyrinth):
        readings = []
        starts = []
        ends = []
        for i in range(len(robot.sensors)):
            r, s, e = LabRobInterface.get_sensor_reading(robot, lab, i)
            readings.append(r)
            starts.append(s)
            ends.append(e)
        return readings, starts, ends


class Control:
    task = 0
    is_on: False
    robot: Robot
    lab: Labyrinth
    sim_time = 0.0
    readings_distance = [0, 0, 0, 0, 0]

    def __init__(self, robot: Robot, lab: Labyrinth):
        self.robot = robot
        self.lab = lab

    def reset(self):
        self.robot.location = Point2D(9, 9)
        self.robot.rotation = 0
        self.sim_time = 0

    def move_forward(self, step):
        x = step * math.sin(math.radians(self.robot.rotation))
        y = -step * math.cos(math.radians(self.robot.rotation))
        self.robot.location = self.robot.location + Point2D(x, y)

    def turn_around(self, deg):
        self.robot.rotation += deg

    def read_sensors(self):
        self.readings_distance = LabRobInterface.read_all_sensors(self.robot, self.lab)[0]

    def control_task(self):
        """
        Place control algorithm here, code is run every 0.02s// can be change in Interface __init__ (timer)

        """
        if self.is_on:
            self.sim_time += 0.02
            self.robot.move_by_engines(0.02)

        """
        here place your code
        """

        if self.readings_distance[2] < 3.0:
            self.robot.set_engines(0, 0)
            print(self.robot.get_encoder_reading())
        else:
            self.robot.set_engines(15, 0)
