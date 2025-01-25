import tensorflow as tf
import numpy as np
import cv2
from tensorflow.keras.applications import MobileNetV3Small
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input
from tensorflow.keras.preprocessing import image
import json

def classify_and_display_image(img_path):
    # Load the MobileNetV3 model with pretrained weights from ImageNet
    # model = MobileNetV3Small(weights="imagenet")
     # Load the MobileNetV3 model with custom weights path
    weights_path = "weights_mobilenet_v3_small_224_1.0_float.h5"
    model = MobileNetV3Small(weights=None)  # Initialize without weights
    model.load_weights(weights_path)  # Load custom weights
    # Load the image
    img = cv2.imread(img_path)

    # Convert the image from BGR (OpenCV) to RGB (TensorFlow)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Resize the image to 224x224 (MobileNetV3 input size)
    img_resized = cv2.resize(img_rgb, (224, 224))

    # Convert the image to a 4D tensor (batch size, height, width, channels)
    img_array = image.img_to_array(img_resized)
    img_array = np.expand_dims(img_array, axis=0)
    
    # Preprocess the image for MobileNetV3
    img_array = preprocess_input(img_array)

    # Make the prediction
    predictions = model.predict(img_array)
    
    # Decode the top prediction
    # decoded_preds = decode_predictions(predictions, top=1)[0]
    decoded_preds = custom_decode_predictions(predictions, top=1)[0]
    class_label, description, score = decoded_preds[0]
    
    # Display the class label on the image
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = f"{description} ({score:.2f})"
    position = (10, 30)  # Text position (top-left corner)
    color = (0, 255, 0)  # Green color for text
    font_scale = 0.7
    font_thickness = 2

    # Add the text to the image
    cv2.putText(img, text, position, font, font_scale, color, font_thickness, lineType=cv2.LINE_AA)

    # Convert the image back to BGR for OpenCV display
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Show the image with the class label superimposed
    cv2.imshow('Image Classification', img_bgr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Optionally, save the image with the label
    output_path = "output_classified_image.jpg"
    cv2.imwrite(output_path, img_bgr)
    print(f"Image saved at {output_path}")


def custom_decode_predictions(preds, top=5):
    """Decodes predictions using a local ImageNet class index file."""
    with open("imagenet_class_index.json", "r") as f:
        class_index = json.load(f)
    
    results = []
    for pred in preds:
        top_indices = pred.argsort()[-top:][::-1]
        result = [
            (str(i), class_index[str(i)][1], pred[i])
            for i in top_indices
        ]
        results.append(result)
    return results

# Example usage
img_path = '2560px-A-Cat.jpg'  # Replace with your image path
classify_and_display_image(img_path)