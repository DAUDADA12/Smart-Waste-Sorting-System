
import RPi.GPIO as GPIO
import time
from main import scan  # Import scan() function from scanner.py

# CONFIG
IR_PIN = 17  # GPIO pin connected to Obstacle IR sensor
GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_PIN, GPIO.IN)  # IR sensor output: HIGH=no object, LOW=object detected

print("Monitoring IR sensor...")

try:
    scanning = False  # Flag to indicate if scan is in progress

    while True:
        if not scanning:  # Only check sensor if not scanning
            sensor_state = GPIO.input(IR_PIN)
            if sensor_state == 0:  # Object detected
                scanning = True  # Set flag
                print("Object detected! Starting scan...")
                
                # Run the scan
                tag, conf = scan()
                
                if tag is not None:
                    print(f"Predicted tag: {tag} ({conf:.2f}%)")
                else:
                    print("Scan failed.")
                
                scanning = False  # Reset flag to allow next detection
        # Small delay to reduce CPU usage
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    GPIO.cleanup()