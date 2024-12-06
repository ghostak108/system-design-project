#!/usr/bin/env pybricks-micropython

# Pfad der Pybricks Bibliothek angeben !WICHTIG!

# Importiere die Bibliotheken

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, ColorSensor, UltrasonicSensor)
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# Initialisiere den EV3 Brick

ev3 = EV3Brick()

# Die Motoren initialisieren

right_motor = Motor(Port.A)
left_motor = Motor(Port.D)

# Die Sensoren initialisieren

sensor_right = ColorSensor(Port.S2)
sensor_center = ColorSensor(Port.S4)
sensor_left = ColorSensor(Port.S1)

# Der Ultraschallsensor initialisieren

ultrasonic_sensor = UltrasonicSensor(Port.S3)

# Die Drivebase festlegen und Maße angeben

robot = DriveBase(left_motor, right_motor, wheel_diameter=55, axle_track=145)

# Variablen erstellen

BLACK_VALUE = 0
WHITE_VALUE = 0
THRESHOLD = 0

# Funktionen für reflektionen erstellen

sensor_left_reflection = sensor_left.reflection()
sensor_center_reflection = sensor_center.reflection()
sensor_right_reflection = sensor_right.reflection()

# Dictionary für Linienstatus erstellen

on_line_status = {}

# Funktionen zur linien auswertung erstellen

def ersteAuswertung(sensor_left_reflection, sensor_center_reflection, sensor_right_reflection):
    global BLACK_VALUE, WHITE_VALUE
    BLACK_VALUE = sensor_center_reflection
    WHITE_VALUE = (sensor_left_reflection + sensor_right_reflection) / 2


def berechne_threshold(BLACK_VALUE, WHITE_VALUE):
    return (BLACK_VALUE + WHITE_VALUE) / 2


def is_on_black_line(sensor_value, threshold=THRESHOLD):
    return sensor_value <= threshold


def linienauswertung():
    global on_line_status

    sensor_values = {
        "right": sensor_right.reflection(),
        "center": sensor_center.reflection(),
        "left": sensor_left.reflection()
    }

    on_line_status = {
        "right": is_on_black_line(sensor_values["right"], THRESHOLD),
        "center": is_on_black_line(sensor_values["center"], THRESHOLD),
        "left": is_on_black_line(sensor_values["left"], THRESHOLD)
    }

    print("Sensorwerte:", sensor_values)
    print("Schwellenwert:", THRESHOLD)
    print("Linienstatus (True = auf der Linie, False = nicht auf der Linie):", on_line_status)

# funktion erstellen die schleife immer laufen lässt (durch true wert)

def tollcool():
    return True

# funktion zur aktualisierung des schwellenwertes für linienerkennung

def eindurchlauf():
    global THRESHOLD

    ersteAuswertung(sensor_left_reflection, sensor_center_reflection, sensor_right_reflection)
    THRESHOLD = berechne_threshold(BLACK_VALUE, WHITE_VALUE)
    linienauswertung()

# funktion zur objekterkennung

def detect_object():
    distance = ultrasonic_sensor.distance()
    if distance < 200:
        print("Object detected")
        return True
    else:
        print("No object detected")
        return False

# funktionen für die fahrbewegungen (fahren, lenken, stoppen, wenden)

def gerade():
    robot.drive(-120, 0)
    wait(100)


def move_rechts():
    robot.drive(-100, -300)
    wait(100)


def move_links():
    robot.drive(-100, 300)
    wait(100)


def wenden():
    robot.turn(450)
    wait(100)


def stop():
    robot.drive(0, 0)
    wait(100)

# funktion die die fahrbewegungen steuert (mit if verkettungen)

def fahren():
    while tollcool() == True:
        
        detect_object()
        eindurchlauf()

        status = (on_line_status["left"], on_line_status["center"], on_line_status["right"])

        if status == (False, True, False):
            gerade()
            print("move gerade")

        elif status == (False, True, True):
            move_rechts()
            print("move rechts")

        elif status == (False, False, True):
            move_rechts()
            print("leicht rechts")

        elif status == (True, True, False):
            move_links()
            print("move links")

        elif status == (True, False, False):
            move_links()
            print("leicht links")

        elif status == (False, False, False) and detect_object() == False:
            gerade()
            print("move gerade")

        elif status == (False, False, False) and detect_object() == True:
            wenden()
            print("turn")

        elif status == (True, True, True) and detect_object() == False:
            gerade()
            print("searching")

        elif status == (True, True, True) and detect_object() == True:
            stop()
            print("stop moving")

# main funktion zur ausführung des codes

if __name__ == "__main__":
    while True:
        fahren()
