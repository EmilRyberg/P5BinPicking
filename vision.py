from darknetpy.detector import Detector
import pyrealsense2 as realsense
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
        self.rs = realsense.pipeline()
        self.current_directory = os.getcwd()
        yolo_cfg_path_absolute = self.current_directory + YOLOCFGPATH
        self.image_path = self.current_directory + "/" + IMAGE_NAME
        self.detector = Detector(yolo_cfg_path_absolute + 'cfg/obj.data', yolo_cfg_path_absolute + 'cfg/yolov3-tiny.cfg', yolo_cfg_path_absolute + 'yolov3-tiny_final.weights')
        self.counter = 0
        self.first_run = True
        self.is_test = is_test
        self.orientationCNN = OrientationDetector(ORIENTATION_MODEL_PATH)

    def __del__(self):
        # Stop streaming
        self.rs.stop()

    def capture_image(self):
        if self.first_run:
            cfg = realsense.config()
            # cfg.enable_stream(realsense.stream.depth, 1280, 720, realsense.format.z16, 30)
            cfg.enable_stream(realsense.stream.color, 1920, 1080, realsense.format.rgb8, 30)
            self.rs.start(cfg)

            frames = None
            # wait for autoexposure to catch up
            for i in range(90):
                frames = self.rs.wait_for_frames()
            self.first_run = False

        frames = self.rs.wait_for_frames()
        color_frame = frames.get_color_frame()

        # Convert images to numpy arrays
        color_image = np.asanyarray(color_frame.get_data())
        color_image_ready_to_save = pimg.fromarray(color_image, 'RGB')
        color_image_ready_to_save.save(self.image_path)
        return color_image_ready_to_save

    def detect_object(self, class_id):
        results = self.detector.detect(self.image_path)
        self.draw_boxes(results)
        class_id1, class_id2 = class_id
        part = (-1, -1, -1)
        # result is an array of dictionaries
        for i in range(len(results)):
            d = results[i]
            if (d['class'] == class_id1 or d['class'] == class_id2) and d['prob'] > 0.6:
                part_class = d['class']
                prob = d['prob']
                width = d['right'] - d['left']
                height = d['bottom'] - d['top']
                x_coord = width / 2 + d['left']
                y_coord = height / 2 + d['top']
                if height > width:
                    orientation = OrientationEnum.HORIZONTAL.value
                elif width > height:
                    orientation = OrientationEnum.VERTICAL.value
                else:
                    orientation = OrientationEnum.HORIZONTAL.value
                    print("[W] Could not determine orientation, using 1 as default")
                new_part_id = convert_to_part_id(part_class)
                part = (new_part_id, x_coord, y_coord, orientation)
                break
        print(part)
        return part

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

    def find_flipped_parts(self):
        results = self.detector.detect(self.image_path)
        parts_to_flip = []
        for i in range(len(results)):
            d = results[i]
            if d['class'] == 'BottomCoverFlipped' or d['class'] == 'BlueCover' or d['class'] == 'WhiteCover' or d['class'] == 'BlackCover' and d['prob'] > 0.6:
                classify = d['class']
                prob = d['prob']
                width = d['right'] - d['left']
                height = d['bottom'] - d['top']
                x_coord = width / 2 + d['left']
                y_coord = height / 2 + d['top']
                if height > width:
                    orientation = OrientationEnum.HORIZONTAL.value
                elif width > height:
                    orientation = OrientationEnum.VERTICAL.value
                else:
                    orientation = OrientationEnum.HORIZONTAL.value
                    print("[W] Could not determine orientation, using 1 as default")
                part_id = convert_to_part_id(classify)
                part = (part_id, x_coord, y_coord, orientation)
                parts_to_flip.append(part)
            elif d['class'] == 'PCBFlipped' and d['prob'] > 0.6:
                classify = d['class']
                prob = d['prob']
                width = d['right'] - d['left']
                height = d['bottom'] - d['top']
                x_coord = width / 2 + d['left']
                y_coord = height / 2 + d['top']
                part_id = PartEnum.PCB.value
                if height > width:
                    orientation = OrientationEnum.HORIZONTAL.value
                elif width > height:
                    orientation = OrientationEnum.VERTICAL.value
                else:
                    orientation = OrientationEnum.HORIZONTAL.value
                print("[W] Could not determine orientation, using 1 as default")
                part = (part_id, x_coord, y_coord, orientation)
                parts_to_flip.append(part)
        print(parts_to_flip)
        return parts_to_flip

    def is_facing_right(self, np_image):
        return self.orientationCNN.is_facing_right(np_image)

    def get_image_path(self):
        return self.image_path
