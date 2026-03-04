# scanner.py
import cv2
import numpy as np
import time
from ai_edge_litert.interpreter import Interpreter

# CONFIG
IP_CAMERA_URL = "https://10.10.2.96:8080/video"
MODEL_PATH = "Model/converted_tflite_quantized/model.tflite"
CLASS_NAMES = ["Biodegradable", "NonBiodegradable"]

# LOAD TFLITE MODEL
interpreter = Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]
input_type = input_details[0]['dtype']
output_type = output_details[0]['dtype']

# FUNCTION TO CAPTURE FRAME AND RUN INFERENCE
def scan():
    cap = cv2.VideoCapture(IP_CAMERA_URL)
    if not cap.isOpened():
        print("Failed to connect to IP camera")
        return None, None

    # ==== STABILIZE CAMERA ====
    print("Stabilizing camera for 5 seconds...")
    start_time = time.time()
    while time.time() - start_time < 5:
        ret, _ = cap.read()  # Read and discard frames
        if not ret:
            print("Warning: failed to grab frame while stabilizing")

    # ==== GRAB ACTUAL FRAME ====
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to grab frame")
        return None, None

    # Preprocess frame
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

    if output_type == np.uint8:
        confidence = (output_data[pred_index] / 255.0) * 100
    else:
        confidence = output_data[pred_index] * 100

    # Display snapshot
    cv2.putText(frame, f"{predicted_tag} ({confidence:.1f}%)", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Snapshot", frame)
    cv2.waitKey(5000)  # Show for 5 seconds
    cv2.destroyAllWindows()

    return predicted_tag, confidence