from scripts.constants import DRAW_PRESCALER, LABYRINTH_WALL_SIZE, TOTAL_SIZE, LABYRINTH_SIZE
from typing import List, Union, Tuple
import easygraphics as graphics
import math


class Point2D:
    x: float
    y: float

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        p = Point2D(x, y)
        return p


class DistanceSensor:
    rel_loc: Point2D  # relative to center of robot
    fi: Union[int, float]  # angle in base robot position, 0 deg is horizontal upward
    size: List[float]  # width and length of sensor

    def __init__(self, rel_loc: Point2D, fi: Union[int, float], size: List[float]):
        self.rel_loc = rel_loc
        self.fi = fi
        if len(size) != 2:
            raise ValueError("size must have length of 2")
        self.size = size[:]


class Engine:
    inertia: float = 3
    omega: float = 0
    radius: float = 1
    max_omega_5v: float

    def set_velocity(self, v: float):
        self.omega = v / self.radius

    def get_velocity(self):
        return self.omega * self.radius


class Frame:
    points: List[Point2D]

    def __init__(self, size):
        p1 = Point2D(-size, -size)
        p2 = Point2D(-size, size)
        p3 = Point2D(size, size)
        p4 = Point2D(size, -size)
        self.points = [p1, p2, p3, p4]


class Robot:
    sq_size = 3  # size of half of robot
    ses_len = sq_size * 2 / 3
    frame: Frame
    mass: float
    omega: float
    rotation: float
    radius: float
    location: Point2D
    sensors: List[DistanceSensor]
    engines: List[Engine]
    velocity: float
    ENC_SCALER:int = 10
    enc_left: int = 0
    enc_right: int = 0

    def __init__(self):
        e1 = Engine()
        e2 = Engine()
        self.radius = 3.0
        self.engines = [e1, e2]
        self.location = Point2D(LABYRINTH_WALL_SIZE / 2 + 30, LABYRINTH_WALL_SIZE / 2 + 30)
        self.rotation = 125
        self.frame = Frame(self.sq_size)
        d1 = DistanceSensor(
            Point2D(self.ses_len / 2 * (-1 - 2 ** (1 / 2)), -self.sq_size + self.ses_len / 2 * (1 + (2 ** 1 / 2))),
            fi=-90, size=[0.5, self.ses_len])
        d2 = DistanceSensor(Point2D(self.ses_len / 2 * (-1 - (2 ** (1 / 2)) / 2),
                                    -self.sq_size + self.ses_len / 2 * ((2 ** 1 / 2) / 2)), fi=-45,
                            size=[0.5, self.ses_len])
        d3 = DistanceSensor(Point2D(0, -self.sq_size), fi=0, size=[0.5, self.ses_len])
        d4 = DistanceSensor(
            Point2D(self.ses_len / 2 * (1 + (2 ** (1 / 2)) / 2), -self.sq_size + self.ses_len / 2 * ((2 ** 1 / 2) / 2)),
            fi=45, size=[0.5, self.ses_len])
        d5 = DistanceSensor(
            Point2D(self.ses_len / 2 * (1 + 2 ** (1 / 2)), -self.sq_size + self.ses_len / 2 * (1 + (2 ** 1 / 2))),
            fi=90, size=[0.5, self.ses_len])
        self.sensors = [d1, d2, d3, d4, d5]

    def set_engine_voltage(self):
        pass

    def get_sensor_reading(self, sensor: DistanceSensor):
        pass

    def rotate(self, fi):
        self.rotation += fi

    def set_engines(self, v_l: float, v_r: float):
        self.engines[0].set_velocity(v_l)
        self.engines[1].set_velocity(v_r)
        self.velocity = (self.engines[0].get_velocity() + self.engines[1].get_velocity()) / 2
        print(self.velocity)

    def move_by_engines(self, time_step):
        delta_fi = time_step * (self.engines[1].get_velocity() - self.engines[0].get_velocity()) / 2 / self.radius
        delta_fi *= 180/math.pi
        self.velocity = (self.engines[0].get_velocity() + self.engines[1].get_velocity()) / 2
        self.enc_left += self.engines[0].get_velocity() * time_step * self.ENC_SCALER
        self.enc_right += self.engines[1].get_velocity() * time_step * self.ENC_SCALER
        x = time_step * self.velocity * math.sin(math.radians(self.rotation))
        y = -time_step * self.velocity * math.cos(math.radians(self.rotation))
        x_y = Point2D(x, y)
        self.rotate(delta_fi)
        self.location = self.location + x_y
    """
    :return tuple(enc_left, enc_right)
    """
    def get_encoder_reading(self):
        return round(self.enc_left), round(self.enc_right)
