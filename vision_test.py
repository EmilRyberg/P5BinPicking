import pyrealsense2 as rs
import numpy as np
from PIL import Image as pimg
import os

class Vision:
    def __init__(self):
        self.rs_pipeline = rs.pipeline()
        self.counter = 0
        self.first_run = True
        self.current_directory = os.getcwd()
        self.image_path = self.current_directory + "/testimage.png"

    def __del__(self):
        # Stop streaming
        self.rs_pipeline.stop()

    def capture_image(self):
        if self.first_run:
            cfg = rs.config()
            # cfg.enable_stream(realsense.stream.depth, 1280, 720, realsense.format.z16, 30)
            cfg.enable_stream(rs.stream.color, 1920, 1080, rs.format.rgb8, 30)

            profile = self.rs_pipeline.start(cfg)
            sensors = profile.get_device().query_sensors()
            rgb_camera = sensors[1]
            rgb_camera.set_option(rs.option.white_balance, 3000)


            frames = None
            # wait for autoexposure to catch up
            for i in range(90):
                frames = self.rs_pipeline.wait_for_frames()
            self.first_run = False

        frames = self.rs_pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        # Convert images to numpy arrays
        color_image = np.asanyarray(color_frame.get_data())
        color_image_ready_to_save = pimg.fromarray(color_image, 'RGB')
        color_image_ready_to_save.save(self.image_path)
        return color_image

if __name__ == "__main__":
    hey = Vision()
    hey.capture_image()