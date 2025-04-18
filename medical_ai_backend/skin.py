import sys
import json
from transformers import AutoModelForImageClassification, ViTImageProcessor
from PIL import Image
import torch

def predict_skin_disease(image_path):
    try:
        # Load model and processor
        MODEL_NAME = "sagarvk24/skin-disorders-classifier"
        model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)
        processor = ViTImageProcessor.from_pretrained(MODEL_NAME)

        # Load image
        image = Image.open(image_path).convert("RGB")

        # Preprocess the image
        inputs = processor(images=image, return_tensors="pt")

        # Get predictions
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            predicted_class_idx = logits.argmax(-1).item()

        # Retrieve label
        labels = model.config.id2label
        predicted_label = labels[predicted_class_idx]

        # Return JSON response
        result = {"predicted_disease": predicted_label}
        print(json.dumps(result))
    
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    image_path = sys.argv[1]
    predict_skin_disease(image_path)
