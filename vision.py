from darknetpy.detector import Detector
import pyrealsense2 as rs
from PIL import Image as pimg
import numpy as np

HORIZONTAL = 0
VERTICAL = 1

YOLOCFGPATH = '/home/rob/Desktop/P5BinPicking/DarkNet/'

class Vision:
    def __init__(self):
        self.rs = rs.pipeline()
        self.cfg=rs.config()
        self.part = (-1, -1, -1)
        self.detector=Detector(YOLOCFGPATH+'cfg/obj.data', YOLOCFGPATH+'cfg/yolov3-tiny.cfg',YOLOCFGPATH+'yolov3-tiny_final.weights')
        self.counter = 0
        self.class_id1 = 0
        self.class_id2 = 0

    def capture_image(self):
        #basically the capture script benedek made
        #maybe a better way to get a way from the camera
        self.cfg.enable_stream(rs.stream.color, 1920, 1080, rs.format,rgb8, 30)

        try:
            # Wait for a coherent pair of frames: depth and color
            for i in range(30):
                frames = self.rs.wait_for_frames()

            while True:
                frames = self.rs.wait_for_frames()

                color_frame = frames.get_color_frame()

                # Convert images to numpy arrays
                color_image = np.asanyarray(color_frame.get_data())

                color_image_ready_to_save = pimg.fromarray(color_image, 'RGB')

                color_image_ready_to_save.save('webcam_capture.png')

                input('Capture and image')

        finally:

            # Stop streaming
            pipeline.stop()


    def detect_object(self, class_id):
        results=self.detector.detect('webcam_capture.png')
        self.class_id1, self.class_id2 = class_id
        #result is an array of dictionaries
        for x in range(len(results)):
            d = results[self.counter]
            if ((d['class'] == self.class_id1 or d['class'] == self.class_id2) and d['prob'] > 0.8):
                classify=d['class']
                prob=d['prob']
                width=d['right']-d['left']
                height=d['bottom']-d['top']
                x_coord=width/2 + d['left']
                y_coord=height/2 + d['top']
                if height > width:
                    orientation = HORIZONTAL
                elif width > height:
                    orientation = VERTICAL
                else:
                    orientation = HORIZONTAL
                    print("[W] Could not determine orientation, using 1 as default")
                self.part=(x_coord, y_coord, orientation)
                break
            self.counter += 1
        print(self.part)
        return self.part


            
