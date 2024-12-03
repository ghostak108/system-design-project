from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# Initialisieren
ev3 = EV3Brick()

# Motoren und Sensoren konfigurieren
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)
color_sensor = ColorSensor(Port.S1)

# Roboterbasis konfigurieren
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=114)

# Linie erkennen: Schwellenwert kalibrieren
BLACK = 10  # Schwarzer Wert
WHITE = 90  # Weißer Wert
THRESHOLD = (BLACK + WHITE) / 2

# P-Regler Parameter
PROPORTIONAL_GAIN = 1.2

while True:
    # Farbsensorwert lesen
    reflection = color_sensor.reflection()
    
    # Fehler berechnen
    error = reflection - THRESHOLD
    
    # Steuerung mit P-Regler
    turn_rate = PROPORTIONAL_GAIN * error
    
    # Roboter steuern
    robot.drive(100, turn_rate)
    
    # Kurz warten
    wait(10)