import tensorflow as tf
import numpy as np
import PIL.Image as pimg


class OrientationDetector:
    def __init__(self, model_path):
        self.model = tf.keras.models.load_model(model_path)

    def is_facing_right(self, image_np_array, threshold=0.5):
        pil_image = pimg.fromarray(image_np_array, 'RGB')
        resized_image = pil_image.resize((224, 224))
        resized_image_np = np.array(resized_image)
        resized_image_np = np.expand_dims(resized_image_np, axis=0) / 255
        prediction = self.model.predict(resized_image_np)
        if prediction >= threshold:
            return True
        return False
