from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Stop, Color
from pybricks.robotics import DriveBase
from pybricks.tools import wait

ev3 = EV3Brick()

left_motor = Motor(Port.D)
right_motor = Motor(Port.A)
arm_motor = Motor(Port.B)
claw_motor = Motor(Port.C)
sensor_left = ColorSensor(Port.S1)
sensor_right = ColorSensor(Port.S2)
sensor_center = ColorSensor(Port.S4)
ultrasonic_sensor = UltrasonicSensor(Port.S3)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55, axle_track=145)
BASE_SPEED = -150
SEARCH_SPEED = -90
RETREAT_SPEED = 170
SPIN_RATE = 420
BALL_ARM_SPEED = 280
BALL_CLAW_SPEED = 260
line_threshold = 30
light_level = 30
ball_locked = False
manipulator_ready = False
speed_profile = {"target": BASE_SPEED, "current": BASE_SPEED}
environment_state = {"incline": "flat", "light": "normal"}
line_state = {"left": False, "center": False, "right": False}
line_history = {"lost_frames": 0, "found_frames": 0}
search_mode = False
current_action = "init"

def announce(action, tone=None):
    global current_action
    current_action = action
    ev3.screen.clear()
    ev3.screen.print(action)
    ev3.screen.print("L:{} C:{} R:{}".format(int(line_state["left"]), int(line_state["center"]), int(line_state["right"])))
    ev3.screen.print("Incline:{}".format(environment_state["incline"]))
    ev3.screen.print("Light:{}".format(environment_state["light"]))
    ev3.screen.print("Ball:{}".format("locked" if ball_locked else "free"))
    ev3.screen.print("Mode:{}".format("search" if search_mode else "track"))
    ev3.screen.print("Speed:{:.0f}".format(speed_profile["current"]))
    tones = {"pickup": 880, "release": 520, "obstacle": 300, "search": 660, "track": 440, "init": 700, "line": 500, "lost": 250, "regain": 900}
    f = tone if tone is not None else tones.get(action, 440)
    ev3.speaker.beep(f, 80)

def capture_reflections(samples=5):
    totals = {"left": 0, "center": 0, "right": 0}
    for _ in range(samples):
        totals["left"] += sensor_left.reflection()
        totals["center"] += sensor_center.reflection()
        totals["right"] += sensor_right.reflection()
        wait(5)
    return {key: totals[key] / samples for key in totals}

def initialize_references():
    global line_threshold, light_level
    readings = capture_reflections(8)
    baseline = (readings["center"] + (readings["left"] + readings["right"]) / 2) / 2
    line_threshold = baseline
    light_level = (readings["left"] + readings["center"] + readings["right"]) / 3

def update_threshold(readings):
    global line_threshold
    blended = (readings["center"] + (readings["left"] + readings["right"]) / 2) / 2
    line_threshold = 0.7 * line_threshold + 0.3 * blended

def register_line_presence(on_line):
    if on_line:
        line_history["found_frames"] += 1
        line_history["lost_frames"] = max(0, line_history["lost_frames"] - 1)
    else:
        line_history["lost_frames"] += 1

def evaluate_line_state(readings):
    global line_state
    line_state = {
        "left": readings["left"] <= line_threshold,
        "center": readings["center"] <= line_threshold,
        "right": readings["right"] <= line_threshold
    }
    register_line_presence(any(line_state.values()))

def update_light_profile(readings):
    global light_level, environment_state
    average = (readings["left"] + readings["center"] + readings["right"]) / 3
    light_level = 0.6 * light_level + 0.4 * average
    if light_level < 15:
        environment_state["light"] = "dark"
    elif light_level > 65:
        environment_state["light"] = "bright"
    else:
        environment_state["light"] = "normal"

def maybe_reinitialize_baseline():
    global line_history
    if line_history["lost_frames"] > 80:
        initialize_references()
        line_history = {"lost_frames": 0, "found_frames": 0}

def detect_object(limit=180):
    distance = ultrasonic_sensor.distance()
    if distance is None:
        return False
    return distance < limit

def detect_ball():
    color_match = sensor_center.color()
    signature = sensor_center.reflection()
    return color_match == Color.RED or signature < line_threshold * 0.8

def signal(event):
    announce(event)

def manage_ball_logic(ball_present):
    global ball_locked
    if ball_present and not ball_locked:
        pickup_ball()
        signal("pickup")
    elif ball_locked and ready_to_release():
        release_ball()
        signal("release")

def ready_to_release():
    return sensor_center.reflection() > line_threshold * 1.4

def ensure_manipulator_ready():
    global manipulator_ready
    if manipulator_ready:
        return
    claw_motor.run_time(-BALL_CLAW_SPEED, 400, Stop.BRAKE, True)
    arm_motor.run_target(BALL_ARM_SPEED, 0, Stop.BRAKE, True)
    manipulator_ready = True

def pickup_ball():
    global ball_locked
    ensure_manipulator_ready()
    robot.drive(0, 0)
    claw_motor.run_time(BALL_CLAW_SPEED, 700, Stop.HOLD, True)
    arm_motor.run_target(BALL_ARM_SPEED, -110, Stop.HOLD, True)
    claw_motor.run_time(-BALL_CLAW_SPEED, 500, Stop.HOLD, True)
    arm_motor.run_target(BALL_ARM_SPEED, 40, Stop.HOLD, True)
    ball_locked = True
    announce("ball_locked")

def release_ball():
    global ball_locked
    robot.drive(0, 0)
    arm_motor.run_target(BALL_ARM_SPEED, -60, Stop.HOLD, True)
    claw_motor.run_time(BALL_CLAW_SPEED, 500, Stop.COAST, True)
    arm_motor.run_target(BALL_ARM_SPEED, 0, Stop.COAST, True)
    claw_motor.run_time(-BALL_CLAW_SPEED, 400, Stop.COAST, True)
    ball_locked = False
    announce("ball_free")

def detect_incline(target_speed):
    global environment_state
    actual = (abs(left_motor.speed()) + abs(right_motor.speed())) / 2
    expected = abs(target_speed)
    if expected == 0:
        environment_state["incline"] = "flat"
        return
    ratio = actual / expected
    if ratio < 0.65:
        environment_state["incline"] = "uphill"
    elif ratio > 1.3:
        environment_state["incline"] = "downhill"
    else:
        environment_state["incline"] = "flat"

def adjust_speed_for_incline(target_speed):
    if environment_state["incline"] == "uphill":
        return target_speed * 1.25
    if environment_state["incline"] == "downhill":
        return target_speed * 0.7
    return target_speed

def adjust_speed_for_light(target_speed):
    if environment_state["light"] == "dark":
        return target_speed * 0.8
    if environment_state["light"] == "bright":
        return target_speed * 1.05
    return target_speed

def adjust_speed_for_payload(target_speed):
    if ball_locked:
        return target_speed * 0.85
    return target_speed

def update_speed_profile():
    global speed_profile
    target = BASE_SPEED
    target = adjust_speed_for_incline(target)
    target = adjust_speed_for_light(target)
    target = adjust_speed_for_payload(target)
    speed_profile["target"] = target
    speed_profile["current"] = 0.6 * speed_profile["current"] + 0.4 * target

def halt_motion():
    robot.drive(0, 0)
    wait(60)

def reverse_from_obstacle():
    robot.drive(RETREAT_SPEED, 0)
    wait(320)

def perform_u_turn():
    robot.turn(SPIN_RATE)
    wait(80)

def handle_obstacle():
    global search_mode, line_history
    signal("obstacle")
    halt_motion()
    reverse_from_obstacle()
    perform_u_turn()
    line_history = {"lost_frames": 0, "found_frames": 0}
    search_mode = False
    announce("post_obstacle")

def compute_turn_rate():
    left = line_state["left"]
    center = line_state["center"]
    right = line_state["right"]
    if center and not left and not right:
        return 0
    if center and right and not left:
        return -120
    if center and left and not right:
        return 120
    if right and not center:
        return -220
    if left and not center:
        return 220
    return 0

def apply_drive_control():
    robot.drive(speed_profile["current"], compute_turn_rate())
    wait(80)
    announce("line")

def lost_line_recovery():
    global search_mode
    search_mode = True
    direction = -220 if line_history["lost_frames"] % 2 == 0 else 220
    robot.drive(SEARCH_SPEED, direction)
    wait(150)
    announce("lost")

def regain_line_control():
    global search_mode
    if search_mode:
        halt_motion()
        search_mode = False
        announce("regain")

def mission_cycle():
    readings = capture_reflections()
    update_threshold(readings)
    evaluate_line_state(readings)
    update_light_profile(readings)
    detect_incline(speed_profile["target"])
    update_speed_profile()
    maybe_reinitialize_baseline()
    ball_present = detect_ball()
    manage_ball_logic(ball_present)
    obstacle = detect_object()
    if obstacle:
        handle_obstacle()
        return
    if any(line_state.values()):
        regain_line_control()
        apply_drive_control()
    else:
        lost_line_recovery()

def mission_loop():
    initialize_references()
    ensure_manipulator_ready()
    while True:
        mission_cycle()

if __name__ == "__main__":
    mission_loop()
