#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, ColorSensor, UltrasonicSensor)
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait


#Create your objects here.
ev3 = EV3Brick()

#Motor Einstellung
right_motor = Motor(Port.A)
left_motor = Motor(Port.D)

#ColorSensor Einstellung
sensor_right = ColorSensor(Port.S4)
sensor_center = ColorSensor(Port.S2)
sensor_left = ColorSensor(Port.S1)

#UltraschallSensor Einstellung
ultrasonic_sensor = UltrasonicSensor(Port.S3)

#Robotergestell
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=145)


def detect_object():
    # Fortlaufende Messung des Abstands
    distance = ultrasonic_sensor.distance()  # Messung des Abstands in mm
    if distance > 100:
        return True
    else:
        return False


if __name__ == "__main":
    while True:  # Endlosschleife
        if detect_object():  # Hindernis ist nicht zu nah
            move_gerade()
        else:  # Hindernis erkannt
            print("Hindernis erkannt! Roboter stoppt.")
            break  # Schleife beenden oder eine andere Aktion ausführen


"""programm funktioniert für einen stopp der bewegung"""