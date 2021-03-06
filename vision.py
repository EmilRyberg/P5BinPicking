from darknetpy.detector import Detector
import pyrealsense2 as rs
from PIL import Image as pimg
from PIL import ImageDraw
import numpy as np
from enums import PartEnum, OrientationEnum
import os
from orientation_detector import OrientationDetector
from class_converter import convert_to_part_id

YOLOCFGPATH = '/DarkNet/'
IMAGE_NAME = "webcam_capture.png"
ORIENTATION_MODEL_PATH = "orientation_cnn.hdf5"

class Vision:
    def __init__(self):
        self.rs_pipeline = rs.pipeline()
        self.current_directory = os.getcwd()
        yolo_cfg_path_absolute = self.current_directory + YOLOCFGPATH
        self.image_path = self.current_directory + "/" + IMAGE_NAME
        self.detector = Detector(yolo_cfg_path_absolute + 'cfg/obj.data', yolo_cfg_path_absolute + 'cfg/yolov3-tiny.cfg', yolo_cfg_path_absolute + 'yolov3-tiny_final.weights')
        self.counter = 0
        self.first_run = True
        self.results = None
        self.orientationCNN = OrientationDetector(ORIENTATION_MODEL_PATH)

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
            rgb_camera.set_option(rs.option.white_balance, 4600)
            rgb_camera.set_option(rs.option.exposure, 80)
            #rgb_camera.set_option(rs.option.saturation, 65)
            #rgb_camera.set_option(rs.option.contrast, 50)


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

    def find_parts(self, class_id, fuse_index=-1):
        class_id1, class_id2 = class_id
        part = (-1, -1, -1, -1, -1)
        # result is an array of dictionaries
        found_class_index = 0
        for i in range(len(self.results)):
            d = self.results[i]
            if (d['class'] == class_id1 or d['class'] == class_id2) and d['prob'] > 0.6:
                if fuse_index > -1 and fuse_index != found_class_index:
                    found_class_index += 1
                    continue
                part_class = d['class']
                prob = d['prob']
                width = d['right'] - d['left']
                height = d['bottom'] - d['top']
                x_coord = width / 2 + d['left']
                y_coord = height / 2 + d['top']
                if height > width:
                    orientation = OrientationEnum.VERTICAL.value
                    grip_width = width * 0.58
                elif width > height:
                    orientation = OrientationEnum.HORIZONTAL.value
                    grip_width = height * 0.58
                else:
                    orientation = OrientationEnum.HORIZONTAL.value
                    grip_width = height * 0.58
                    print("[W] Could not determine orientation, using 1 as default")
                new_part_id = convert_to_part_id(part_class)
                part = (new_part_id, x_coord, y_coord, orientation, grip_width)
                break
        print(part)
        return part

    def detect_object(self):
        self.results = self.detector.detect(self.image_path)
        self.draw_boxes(self.results)

    def draw_boxes(self, results):
        source_img = pimg.open(self.image_path).convert("RGBA")
        for i in range(len(results)):
            d = results[i]
            if d['prob'] > 0.6:
                classify = d['class']
                prob = d['prob']
                width = d['right'] - d['left']
                height = d['bottom'] - d['top']
                x_coord = width / 2 + d['left']
                y_coord = height / 2 + d['top']
                draw = ImageDraw.Draw(source_img)
                draw.rectangle(((d['left'], d['top']), (d['right'], d['bottom'])), fill=None, outline=(200, 0, 150), width=6)
                draw.text((x_coord, y_coord), d['class'])
        source_img.save('boundingboxes.png')

    def is_facing_right(self, np_image):
        result = self.orientationCNN.is_facing_right(np_image)
        print("[INFO] Part is facing right. {}".format(result))
        return result

    def get_image_path(self):
        return self.image_path

if __name__ == "__main__":
    hey = Vision()
    while True:
        hey.capture_image()
        hey.detect_object()
        input()