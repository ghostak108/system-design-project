#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, ColorSensor, UltrasonicSensor)
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait
from abstand import detect_object

# Initialisierung des EV3 Bricks
ev3 = EV3Brick()

# Motoren mit Anpassung für die Übersetzung
left_motor = Motor(Port.D)
right_motor = Motor(Port.A)

# Farbsensoren
sensor_right = ColorSensor(Port.S2)
sensor_center = ColorSensor(Port.S4)
sensor_left = ColorSensor(Port.S1)

# Ultraschallsensor
ultrasonic_sensor = UltrasonicSensor(Port.S3)

# Roboterbasis mit angepasstem Raddurchmesser
robot = DriveBase(left_motor, right_motor, wheel_diameter=277.5, axle_track=145)

def move_links():
    robot.drive(300, -30)
    wait(200)

def move_gerade():
    robot.drive(600, 0)
    wait(400)

def move_rechts():
    robot.drive(300, 30)
    wait(200)

def wenden():
    robot.turn(180)

def drive_forever():
    robot.drive(1000, 0)
    wait(5000000)

# Initialisierung der Schwellenwerte
BLACK_VALUE = sensor_center.reflection()
WHITE_VALUE = (sensor_left.reflection() + sensor_right.reflection()) / 2
THRESHOLD = (BLACK_VALUE + WHITE_VALUE) / 2

def is_on_black_line(sensor_value):
    return sensor_value <= THRESHOLD

def ausnahme():
    global THRESHOLD
    THRESHOLD -= 10  # Erhöht die Schwelle

def ausnahme_ende():
    global THRESHOLD
    THRESHOLD += 10  # Senkt die Schwelle wieder

# Globale Variable für den Linienstatus
on_line_status = {}

def linienauswertung():
    global on_line_status
    sensor_values = {
        "right": sensor_right.reflection(),
        "center": sensor_center.reflection(),
        "left": sensor_left.reflection()
    }
    on_line_status = {
        "right": is_on_black_line(sensor_values["right"]),
        "center": is_on_black_line(sensor_values["center"]),
        "left": is_on_black_line(sensor_values["left"])
    }
    print("Sensorwerte:", sensor_values)
    print("Linienstatus (True = auf der Linie, False = nicht auf der Linie):", on_line_status)

def fahren():
    global BLACK_VALUE, WHITE_VALUE, THRESHOLD
    while detect_object():
        linienauswertung()
        if on_line_status["center"] and not on_line_status["right"] and not on_line_status["left"]:
            move_gerade()
            BLACK_VALUE = sensor_center.reflection()
            WHITE_VALUE = (sensor_left.reflection() + sensor_right.reflection()) / 2
            THRESHOLD = (BLACK_VALUE + WHITE_VALUE) / 2
        elif on_line_status["right"] and on_line_status["center"] and not on_line_status["left"]:
            move_rechts()
        elif on_line_status["right"] and not on_line_status["center"] and not on_line_status["left"]:
            move_rechts()
        elif on_line_status["left"] and on_line_status["center"] and not on_line_status["right"]:
            move_links()
        elif on_line_status["left"] and not on_line_status["center"] and not on_line_status["right"]:
            move_links()
        elif not on_line_status["left"] and not on_line_status["center"] and not on_line_status["right"]:
            robot.drive(200, 0)
            wait(2000)
            ausnahme()
            linienauswertung()
            ausnahme_ende()
            if not on_line_status["left"] and not on_line_status["center"] and not on_line_status["right"]:
                wenden()
            else:
                continue
        else:
            robot.drive(0, 0)

def warten():
    while not detect_object():
        wait(1000)

if __name__ == "__main__":
    while True:
        fahren()
        warten()