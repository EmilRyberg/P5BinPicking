# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 11:19:00 2019

@author: Emil
"""

import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
import argparse


def main(model_name):
    model = tf.keras.models.load_model(model_name)
    video = cv2.VideoCapture(2)
    while True:
        _, frame = video.read()
        width_height_difference = frame.shape[1] - frame.shape[0]
        width_to_cut = int(width_height_difference / 2)
        cropped_frame = frame[0:frame.shape[0], width_to_cut:frame.shape[1]-width_to_cut]
        
        img = Image.fromarray(cropped_frame, 'RGB')

        img = img.resize((224, 224))
        img_array = np.array(img)
        #img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
        img_array = np.expand_dims(img_array, axis=0) / 255

        #Calling the predict method on model to predict 'me' on the image
        predictions = model.predict(img_array)
        text_str = "Is facing right: {0:.2f}%".format(predictions[0, 0] * 100.0)
        cv2.putText(cropped_frame, text_str, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 0), 1, cv2.LINE_AA)

        cv2.imshow("Capturing", cropped_frame)
        cv2.imshow("Resized", np.squeeze(img_array, axis=0))
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main('orientation_cnn.hdf5')