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
    robot.drive(-300, 0)
    wait(1000)


def move_rechts():
    robot.turn(50)
    wait(1000)


def move_links():
    robot.turn(-50)
    wait(1000)


# Minimalwert für Schwarz und Schwellenwert
BLACK_VALUE = sensor_center.reflection()
WHITE_VALUE = (sensor_left.reflection() + sensor_right.reflection()) / 2

# Schwellenwert für Erkennung der schwarzen Linie
THRESHOLD = ((BLACK_VALUE + WHITE_VALUE) / 2)   # Dynamisch zwischen Schwarz und Weiß


# Funktion zur Überprüfung, ob ein Sensor auf der schwarzen Linie ist
def is_on_black_line(sensor_value, threshold=THRESHOLD):
    return sensor_value <= threshold  # True, wenn der Wert unter der Schwelle liegt (auf Schwarz)


def ausnahme(THRESHOLD):
    THRESHOLD -= 10  # erhöht die schwelle
    return THRESHOLD


def ausnahme_ende(THRESHOLD):
    THRESHOLD += 10  # senkt sie wieder
    return THRESHOLD


# Globale Variable für den Status
on_line_status = {}
BLACK_VALUE = {}
WHITE_VALUE = {}


# Hauptprogramm
def linienauswertung():
    global on_line_status  # Zugriff auf die globale Variable
    # Sensorwerte auslesen
    sensor_values = {
        "right": sensor_right.reflection(),
        "center": sensor_center.reflection(),
        "left": sensor_left.reflection()
    }

    # Prüfen, ob die Sensoren auf der schwarzen Linie sind
    on_line_status = {
        "right": is_on_black_line(sensor_values["right"]),
        "center": is_on_black_line(sensor_values["center"]),
        "left": is_on_black_line(sensor_values["left"])
    }

    # Ergebnisse ausgeben
    print("Sensorwerte:", sensor_values)
    print("Linienstatus (True = auf der Linie, False = nicht auf der Linie):", on_line_status)


def fahren():
    while detect_object() == True:
        linienauswertung()  # Aktualisiere `on_line_status` bei jedem Schleifendurchlauf
        if on_line_status["center"] and not on_line_status["right"] and not on_line_status["left"]:
            move_gerade()
            BLACK_VALUE = sensor_center.reflection()
            WHITE_VALUE = (sensor_left.reflection() + sensor_right.reflection()) / 2  # Updated BLACK and WHITE

        elif on_line_status["right"] and on_line_status["center"] and not on_line_status["left"]:  # rechtskurve
            move_rechts()
        elif on_line_status["right"] and not on_line_status["center"] and not on_line_status["left"]:  # korrektur rechts
            move_rechts()
        elif on_line_status["left"] and on_line_status["center"] and not on_line_status["right"]:  # linkskurve
            move_links()
        elif on_line_status["left"] and not on_line_status["center"] and not on_line_status["right"]:  # korrektur links
            move_links()
        else:
            robot.drive(0, 0)


def warten():
    while detect_object == False:
        wait(1000)


if __name__ == "__main__":
    while True:
<<<<<<< HEAD:test.py
        move_gerade()
        move_rechts()
        move_gerade()
        move_links()
    else:
        ...
=======
        fahren()
        warten()
>>>>>>> 9d28aff88f578ce161ede4be5ac7c06024c7c13e:gpt.py
