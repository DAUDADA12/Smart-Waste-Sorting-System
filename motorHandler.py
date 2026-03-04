import time
from adafruit_servokit import ServoKit

# Initialize the 16-channel servo shield
kit = ServoKit(channels=16)

# Servo channels for left and right
LEFT_SERVO_CHANNEL = 0   # Biodegradable
RIGHT_SERVO_CHANNEL = 1  # Non-biodegradable

# Move a servo to a given angle, wait, then reset
def move_servo(channel, angle=45, wait_time=5):
    print(f"Moving servo on channel {channel} to {angle}°")
    kit.servo[channel].angle = angle
    time.sleep(wait_time)
    print(f"Returning servo on channel {channel} to 0°")
    kit.servo[channel].angle = 0

# Open left chute
def open_left():
    print("Opening left lid (biodegradable)")
    move_servo(LEFT_SERVO_CHANNEL)

# Open right chute
def open_right():
    print("Opening right lid (non-biodegradable)")
    move_servo(RIGHT_SERVO_CHANNEL)