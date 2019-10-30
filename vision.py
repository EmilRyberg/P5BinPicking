from darknetpy.detector import Detector
import pyrealsense2 as realsense
from PIL import Image as pimg
from PIL import ImageDraw, ImageEnhance, ImageColor
import numpy as np
from part_enum import PartEnum


HORIZONTAL = 0
VERTICAL = 1

YOLOCFGPATH = '/home/rob/Desktop/P5BinPicking/DarkNet/'

class Vision:
    def __init__(self):
        self.detector = Detector(YOLOCFGPATH+'cfg/obj.data', YOLOCFGPATH+'cfg/yolov3-tiny.cfg',YOLOCFGPATH+'yolov3-tiny_final.weights')
        self.counter = 0

    def capture_image(self):
        #basically the capture script benedek made
        #maybe a better way to get a way from the camera
        rs = realsense.pipeline()
        cfg = realsense.config()
        cfg.enable_stream(realsense.stream.depth, 1280, 720, realsense.format.z16, 30)
        cfg.enable_stream(realsense.stream.color, 1920, 1080, realsense.format.rgb8, 30)
        cfg.enable_stream(realsense.stream.color, 1920, 1080, realsense.format.rgb8, 30)
        profile = rs.start(cfg)

        try:
            frames = None
            # Wait for a coherent pair of frames: depth and color
            for i in range(90):
                frames = rs.wait_for_frames()

            color_frame = frames.get_color_frame()

            # Convert images to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())

            color_image_ready_to_save = pimg.fromarray(color_image, 'RGB')

            color_image_ready_to_save.save(YOLOCFGPATH+'webcam_capture.png')

        finally:

            # Stop streaming
            rs.stop()


    def detect_object(self, class_id):
        results = self.detector.detect(YOLOCFGPATH+'webcam_capture.png')
        self.draw_boxes(results)
        class_id1, class_id2 = class_id
        part = (-1, -1, -1)
        #result is an array of dictionaries
        for i in range(len(results)):
            d = results[i]
            if (d['class'] == class_id1 or d['class'] == class_id2) and d['prob'] > 0.6:
                classify = d['class']
                prob = d['prob']
                width = d['right']-d['left']
                height = d['bottom']-d['top']
                x_coord = width/2 + d['left']
                y_coord = height/2 + d['top']
                if height > width:
                    orientation = HORIZONTAL
                elif width > height:
                    orientation = VERTICAL
                else:
                    orientation = HORIZONTAL
                    print("[W] Could not determine orientation, using 1 as default")
                part = (x_coord, y_coord, orientation)
                break
        print(part)
        return part

    def draw_boxes(self, results):
        source_img = pimg.open(YOLOCFGPATH+'webcam_capture.png').convert("RGBA")
        for i in range(len(results)):
            d = results[i]
            if d['prob'] > 0.6:
                classify = d['class']
                prob = d['prob']
                width = d['right']-d['left']
                height = d['bottom']-d['top']
                x_coord = width/2 + d['left']
                y_coord = height/2 + d['top']
                draw = ImageDraw.Draw(source_img)
                draw.rectangle(((d['left'], d['top']), (d['right'], d['bottom'])), fill=None, outline=(200, 0, 150), width=6)
                draw.text((x_coord, y_coord), d['class'])
        source_img.save('boundingboxes.png')

    def find_flipped_parts(self):
        results = self.detector.detect(YOLOCFGPATH+'webcam_capture.png')
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
                gripper = PartEnum.BACKCOVER.value
                if height > width:
                    orientation = HORIZONTAL
                elif width > height:
                    orientation = VERTICAL
                else:
                    orientation = HORIZONTAL
                    print("[W] Could not determine orientation, using 1 as default")
                part = [gripper, x_coord, y_coord, orientation]
                parts_to_flip.append(part)
            elif d['class'] == 'PCBFlipped' and d['prob'] > 0.6:
                classify = d['class']
                prob = d['prob']
                width = d['right'] - d['left']
                height = d['bottom'] - d['top']
                x_coord = width / 2 + d['left']
                y_coord = height / 2 + d['top']
                gripper = PartEnum.PCB.value
                if height > width:
                    orientation = HORIZONTAL
                elif width > height:
                    orientation = VERTICAL
                else:
                    orientation = HORIZONTAL
                print("[W] Could not determine orientation, using 1 as default")
                part = [gripper, x_coord, y_coord, orientation]
                parts_to_flip.append(part)
        print(parts_to_flip)
        return parts_to_flip


            
