from darknetpy.detector import Detector
import pyrealsense2 as rs
from PIL import Image as pimg
import numpy as np


class Vision
    def __init__(self)
        self.rs.pipelice()
        self.cfg=rs.config()
        self.detector=Detector('<path-to-.data>', '<path-to-.cfg','<path-to-.weights')

    def capture_image(self)
        #basically the capture script benedek made
        #maybe a better way to get a way from the camera
        cfg.enable_stream(rs.stream.color, 1920, 1080, rs.format,rgb8, 30)

        try:
        # Wait for a coherent pair of frames: depth and color
        for i in range(30):
            frames = pipeline.wait_for_frames()

        while True:
            frames = pipeline.wait_for_frames()

            color_frame = frames.get_color_frame()

            # Convert images to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())

            color_image_ready_to_save = pimg.fromarray(color_image, 'RGB')

            color_image_ready_to_save.save('webcam_capture.png')

            input('Capture and image')

        finally:

        # Stop streaming
        pipeline.stop()


    def detect_objects(self)
        results=self.detector.detect('webcam_capture.png')

        #result is an array of dictionaries
        counter=0
        for x in range(len(results)):
            d=results[counter]
            classify=d['class']
            prob=d['prob']
            width=d['right']-d['left']
            height=d['bottom']-d['top']
            x_coord=width+d['left']
            y_coord=height+d['top']
            item=(classify, prob, width, height, x_coord, y_coord,)
            counter += 1

        
        return item


            
