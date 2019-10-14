import pyrealsense2 as rs
from PIL import Image as pimg
import numpy as np
import cv2.aruco as aruco
import cv2
import time

# based on this guide: https://www.fdxlabs.com/calculate-x-y-z-real-world-coordinates-from-a-single-camera-using-opencv/

class Calibration:
    def __init__(self):
        # marker locations in robot world frame
        aruco_coordinates_0 = np.array([[-380.7, -278.2, 0], [-350.30, -248.1, 0], [-320.1, -278.6, 0], [-350.3, -308.8, 0]])
        aruco_coordinates_1 = np.array([[395.4, -252.2, 0], [426.7, -283.7, 0], [396.2, -313.5, 0], [366.1, -282.9, 0]])
        aruco_coordinates_2 = np.array([[175.7, -90.0, 0], [145.1, -60.0, 0], [174.6, -29.3, 0], [205.8, -60.0, 0]])
        aruco_coordinates_3 = np.array([[-0.3, -664.4, 0], [29.5, -634.2, 0], [60.2, -664.7, 0], [30.4, -694.9, 0]])
        self.markers = np.array([aruco_coordinates_0, aruco_coordinates_1, aruco_coordinates_2, aruco_coordinates_3], dtype=np.float32)
        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
        # ids = np.float32(np.array([0, 1, 2, 3]))
        # board = aruco.Board_create(self.markers, aruco_dict, ids)

        # intrinsic matrix reported by realsense sdk
        self.default_intrinsic_matrix = np.array([[1393.77, 0, 956.754], [0, 1393.14, 545.3], [0, 0, 1]])
        intrinsic_matrix = np.array([[1393.77, 0, 956.754], [0, 1393.14, 545.3], [0, 0, 1]])
        # in theory the image is undistorted in HW in the camera
        default_distortion = np.array([0, 0, 0, 0, 0], dtype=np.float32)
        self.distortion = default_distortion.T

    def calibrate(self, np_image, x_coordinate, y_coordinate):
        timer = time.time()

        # RGB to BGR, then grayscale
        opencv_image = np_image[:, :, ::-1].copy()
        opencv_image_gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)

        (corners, detected_ids, rejected_image_points) = aruco.detectMarkers(opencv_image_gray, self.aruco_dict)
        corners = np.array(corners).reshape((len(detected_ids), 4, 2)) #opencv stupid
        detected_ids = np.array(detected_ids).reshape((len(detected_ids))) #opencv stupid
        if len(detected_ids) <= 3:
            print("[WARNING] calibration found less than 4 markers")
        assert (len(detected_ids) >= 3), "Cannot work with 2 or less markers"

        #putting all the coordinates into arrays understood by solvePNP
        marker_world_coordinates = None
        image_coordinates = None
        for i in range(len(detected_ids)):
            if i == 0:
                marker_world_coordinates = self.markers[detected_ids[i]]
                image_coordinates = corners[i]
            else:
                marker_world_coordinates = np.concatenate((marker_world_coordinates, self.markers[detected_ids[i]]))
                image_coordinates = np.concatenate((image_coordinates, corners[i]))

        # finding exstrinsic camera parameters
        error, r_vector, t_vector = cv2.solvePnP(marker_world_coordinates, image_coordinates, self.default_intrinsic_matrix, self.distortion)

        r_matrix, jac = cv2.Rodrigues(r_vector)
        r_matrix_inverse = np.linalg.inv(r_matrix)
        intrinsic_matrix_inverse = np.linalg.inv(self.default_intrinsic_matrix)

        # finding correct scaling factor by adjusting it until the calculated Z is very close to 0, mathematically correct way didn't work ¯\_(ツ)_/¯
        scaling_factor = 1185
        i = 0
        while True:
            pixel_coordinates = np.array([[x_coordinate, y_coordinate, 1]]).T
            pixel_coordinates = scaling_factor * pixel_coordinates
            xyz_c = intrinsic_matrix_inverse.dot(pixel_coordinates)
            xyz_c = xyz_c - t_vector
            world_coordinates = r_matrix_inverse.dot(xyz_c)
            print(scaling_factor)
            i += 1
            # print(i)
            # print(world_coordinates)
            if world_coordinates[2] > -399.5:
                scaling_factor += 1
            elif world_coordinates[2] < -400.5:
                scaling_factor -= 1
            elif i > 100:
                raise Exception("scaling factor finding is taking loner than 100 iterations, should be under 50")
            else:
                break
        print("[INFO] Calibration took %.2f seconds" % (time.time() - timer))
        return world_coordinates


"""
marker0 = np.array([[236,1049],[236, 972],[311, 971],[311, 1049]], dtype=np.float32)
marker3 = np.array([[1220, 1036],[1215, 958],[1292, 958],[1294, 1033]], dtype=np.float32)
marker2 = np.array([[693, 98],[619, 100],[615, 27],[690, 25]], dtype=np.float32)
marker1 = np.array([[1243, 17],[1245, 88],[1171, 90],[1169, 17]], dtype=np.float32)
corners2 = [marker0, marker3, marker2, marker1]
"""

"""
rt_matrix = np.column_stack((r_matrix, t_vector))
projection_matrix = default_intrinsic_matrix.dot(rt_matrix)
xyz = np.array([[1000,500,-400,1.0]], dtype=np.float32)
xyz = xyz.T
suv = projection_matrix.dot(xyz)
scaling_factor = suv[2,0]
print(scaling_factor)
"""
if __name__ == "__main__":
    calibration = Calibration()

    pil_image = pimg.open("img.png")
    np_image = np.array(pil_image)

    print(calibration.calibrate(np_image, 1000, 500))

    exit()
    pipeline = rs.pipeline()
    cfg = rs.config()
    cfg.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    cfg.enable_stream(rs.stream.color, 1920, 1080, rs.format.rgb8, 30)
    profile = pipeline.start(cfg)

    try:
        for i in range(30):
            frames = pipeline.wait_for_frames()

        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

    finally:
        pipeline.stop()
