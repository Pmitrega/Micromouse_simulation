import easygraphics as eg
from scripts import labyrinth
from scripts.robot_model import Robot
from scripts import draw
from scripts.interface import Menu, Interface

menu = Menu()
lab = labyrinth.Labyrinth()
lab.read_map("map.txt")
editor = labyrinth.MapEditor(lab)
editor.lab = lab
robot = Robot()
interface = Interface(lab, robot)

"""
Put control algorithm in Control.control_task in control.py

"""
def main():
    interface.begin()


if __name__ == '__main__':
    eg.easy_run(main)
