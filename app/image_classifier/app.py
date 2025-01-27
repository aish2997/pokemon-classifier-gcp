from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
import cv2
import json
from tensorflow.keras.applications import MobileNetV3Small
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input

app = Flask(__name__)

# Load model and weights
model = MobileNetV3Small(weights=None)
model.load_weights("weights/weights_mobilenet_v3_small_224_1.0_float.h5")

with open("imagenet_class_index.json", "r") as f:
    class_index = json.load(f)

def custom_decode_predictions(preds, top=1):
    """
    Decodes the predictions from the model into human-readable labels.

    Args:
        preds (np.ndarray): Array of predictions from the model.
        top (int): Number of top predictions to return for each input.

    Returns:
        list: A list of decoded predictions. Each prediction is a list of tuples
              with the format (class_id, class_description, probability).
    """
    results = []
    for pred in preds:
        top_indices = pred.argsort()[-top:][::-1]
        result = [(str(i), class_index[str(i)][1], pred[i]) for i in top_indices]
        results.append(result)
    return results

@app.route('/classify', methods=['POST'])
def classify():
    """
    Handles the image classification request.

    This function accepts an image file through a POST request, preprocesses the image,
    and predicts its class using the MobileNetV3Small model.

    Returns:
        Response: A JSON response containing the predicted class, description, and confidence score.

        If no image is uploaded, returns a 400 error with a message.
    """
    file = request.files.get('image')
    if not file:
        return jsonify({"error": "No image uploaded"}), 400
    
    # Read and preprocess the image
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (224, 224))
    img_array = np.expand_dims(preprocess_input(np.array(img_resized)), axis=0)

    # Prediction
    preds = model.predict(img_array)
    decoded_preds = custom_decode_predictions(preds, top=1)
    class_label, description, score = decoded_preds[0][0]

    return jsonify({"class": class_label, "description": description, "score": float(score)})