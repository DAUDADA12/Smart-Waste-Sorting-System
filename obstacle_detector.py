from gpiozero import InputDevice
import time
from main import scan
from motorHandler import open_left, open_right

IR_PIN = 17
sensor = InputDevice(IR_PIN)

scanning = False

try:
    while True:
        if not scanning and not sensor.is_active:  # Obstacle detected
            scanning = True
            print("Obstacle detected! Starting scan...")
            
            tag, conf = scan()
            
            if tag is not None:
                print(f"Predicted tag: {tag} ({conf:.2f}%)")
                
                if tag == "Biodegradable":
                    open_left()
                else:
                    open_right()
                    
            else:
                print("Scan failed.")
                
            scanning = False
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Exiting...")