#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, ColorSensor, UltrasonicSensor)
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait
from abstand import detect_object


# Create your objects here.
ev3 = EV3Brick()

# Motor Einstellung
right_motor = Motor(Port.A)
left_motor = Motor(Port.D)
# servo = Servo.Motor(Port.A)

# ColorSensor Einstellung
sensor_right = ColorSensor(Port.S2)
sensor_center = ColorSensor(Port.S4)
sensor_left = ColorSensor(Port.S1)

# UltraschallSensor Einstellung
ultrasonic_sensor = UltrasonicSensor(Port.S3)

# Robotergestell
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=145)


def move_gerade():
    robot.drive(700, 0)


if __name__ == "__main__":
    while True:
        move_gerade()
