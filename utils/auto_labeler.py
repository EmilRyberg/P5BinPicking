from darknetpy.detector import Detector
import os
import glob
from PIL import Image
import numpy as np
import time

YOLOCFGPATH = "/DarkNet/"
IMAGES_TO_LABEL_GLOB = "images/*"
LABEL_PATH = "labels"


class AutoLabeler:
    def __init__(self):
        self.current_directory = os.getcwd()
        self.class_list = np.loadtxt("class_list.txt", dtype=np.str)
        yolo_cfg_path_absolute = self.current_directory + YOLOCFGPATH
        self.detector = Detector(yolo_cfg_path_absolute + 'cfg/obj.data',
                                 yolo_cfg_path_absolute + 'cfg/yolov3-tiny.cfg',
                                 yolo_cfg_path_absolute + 'yolov3-tiny_final.weights')
        if not os.path.isdir(LABEL_PATH):
            os.mkdir(LABEL_PATH)

    def label_images(self):
        files_to_label = glob.glob(IMAGES_TO_LABEL_GLOB)
        number_of_files = len(files_to_label)
        print(f"{number_of_files} to label in total")
        start_time = time.time()
        for index, file_path in enumerate(files_to_label):
            image = Image.open(file_path)
            label_matrix = []
            print(f"Labeling {index + 1}/{number_of_files}")
            results = self.detector.detect(file_path)
            is_first = True
            for result in results:
                if result["prob"] < 0.6:
                    continue
                c = [index for index, label in enumerate(self.class_list) if label == result["class"]][0]
                width = result["right"] - result["left"]
                height = result["bottom"] - result["top"]
                x_coord = width / 2 + result["left"]
                y_coord = height / 2 + result["top"]
                width_relative = width / image.width
                height_relative = height / image.height
                x_coord_relative = x_coord / image.width
                y_coord_relative = y_coord / image.height
                label_matrix.append([c, x_coord_relative, y_coord_relative, width_relative, height_relative])

            label_matrix_np = np.array(label_matrix)
            base_label_file_name = os.path.basename(file_path)[:os.path.basename(file_path).rfind('.')] + ".txt"
            label_file_name = f"{LABEL_PATH}/{base_label_file_name}"
            np.savetxt(label_file_name, label_matrix_np)
            time_elapsed = time.time() - start_time
            estimated_time_remaining = (time_elapsed / (index + 1)) * (len(files_to_label) - (index + 1)) / (1000 * 60)
            print(f"Saving file as {label_file_name} -- Est {estimated_time_remaining:.2f} mins remaining")


if __name__ == "__main__":
    instance = AutoLabeler()
    instance.label_images()


