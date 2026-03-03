import cv2
import numpy as np
import time
from ai_edge_litert.interpreter import Interpreter

# ===== CONFIG =====
IP_CAMERA_URL = "https://10.10.2.96:8080/video"  # Replace with your camera URL
MODEL_PATH = "Model/converted_tflite_quantized/model.tflite"
CLASS_NAMES = ["Biodegradable", "NonBiodegradable"]

# ===== LOAD TFLITE MODEL =====
interpreter = Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]
input_type = input_details[0]['dtype']
output_type = output_details[0]['dtype']

# ===== FUNCTION TO RUN INFERENCE ON A FRAME =====
def get_model_output(frame):
    img = cv2.resize(frame, (width, height))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.expand_dims(img, axis=0)

    if input_type == np.float32:
        img = img.astype(np.float32) / 255.0
    elif input_type == np.uint8:
        img = img.astype(np.uint8)
    else:
        raise ValueError(f"Unsupported input type: {input_type}")

    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])[0]

    pred_index = np.argmax(output_data)
    predicted_tag = CLASS_NAMES[pred_index]

    # Normalize confidence to 0–100%
    if output_type == np.uint8:
        confidence = (output_data[pred_index] / 255.0) * 100
    else:
        confidence = output_data[pred_index] * 100

    return predicted_tag, confidence

# ===== OPEN IP CAMERA =====
cap = cv2.VideoCapture(IP_CAMERA_URL)
if not cap.isOpened():
    print("Failed to connect to IP camera")
    exit()

print("Waiting 5 seconds before taking snapshot...")
time.sleep(5)  # wait for camera to adjust / stabilize

# Grab a single frame
ret, frame = cap.read()
if not ret:
    print("Failed to grab frame")
    cap.release()
    exit()

# Run inference
tag, conf = get_model_output(frame)
print(f"Predicted tag: {tag} ({conf:.2f}%)")

# Optionally, show the snapshot
cv2.putText(frame, f"{tag} ({conf:.1f}%)", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
cv2.imshow("Snapshot", frame)
cv2.waitKey(0)  # wait until any key pressed
cv2.destroyAllWindows()

cap.release()