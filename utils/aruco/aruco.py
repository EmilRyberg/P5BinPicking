import pyrealsense2 as rs
from PIL import Image as pimg
import numpy as np
import cv2.aruco as aruco
import cv2

aruco_coordinates_0 = np.array([[-72.1, -468.5, -400], [-72.0, -425.4, -400], [-28.9, -425.4, -400], [-28.8, -468.5, -400]])
aruco_coordinates_1 = np.array([[503.5, 100, -400], [503.5, 56.8, -400], [460, 56.7, -400], [460, 100, -400]])
aruco_coordinates_2 = np.array([[189, 61, -400], [145.9, 59.9, -400], [145.9, 103, -400], [188.4, 103, -400]])
aruco_coordinates_3 = np.array([[470, -472.2, -400], [469.3, -429.9, -400], [511.9, -429.3, -400], [512.5, -472, -400]])


#print(aruco_coordinates_0)
board_points = np.float32(np.array([aruco_coordinates_0, aruco_coordinates_1, aruco_coordinates_2, aruco_coordinates_3]))
aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
ids = np.float32(np.array([0, 1, 2, 3]))

board = aruco.Board_create(board_points, aruco_dict, ids)

pil_image = pimg.open("img.png")
open_cv_image = np.array(pil_image)
# Convert RGB to BGR
opencv_image = open_cv_image[:, :, ::-1].copy()
opencv_image_gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)

default_intrinsics = np.array([[1393.77, 0, 956.754], [0, 1393.14, 545.3], [0, 0, 1]])
intrinsic_matrix = np.array([[1393.77, 0, 956.754], [0, 1393.14, 545.3], [0, 0, 1]])
default_distortion = np.array([0, 0, 0, 0, 0], dtype=np.float32)
distortion = default_distortion.T


(corners, detected_ids, rejected_image_points) = aruco.detectMarkers(opencv_image_gray, aruco_dict)
marker0 = np.array([[236,1049],[236, 972],[311, 971],[311, 1049]], dtype=np.float32)
marker3 = np.array([[1220, 1036],[1215, 958],[1292, 958],[1294, 1033]], dtype=np.float32)
marker2 = np.array([[693, 98],[619, 100],[615, 27],[690, 25]], dtype=np.float32)
marker1 = np.array([[1243, 17],[1245, 88],[1171, 90],[1169, 17]], dtype=np.float32)
corners2 = [marker0, marker3, marker2, marker1]

newcam_mtx, roi=cv2.getOptimalNewCameraMatrix(intrinsic_matrix, default_distortion, (1920,1080), 1, (1920,1080))

world_cords = np.concatenate((aruco_coordinates_0, aruco_coordinates_1, aruco_coordinates_2, aruco_coordinates_3))
image_cords = np.concatenate((marker0, marker1, marker2, marker3))
ret, rvec2, tvec2 = cv2.solvePnP(world_cords, image_cords, newcam_mtx, distortion)

#print(corners)
#print(detected_ids)

#rvec,tvec,c = aruco.estimatePoseSingleMarkers(corners, 50, default_intrinsics, distortion)
#aruco.drawAxis(opencv_image_gray, default_intrinsics, distortion, rvec[3], tvec[3], 50)
#cv2.imshow("image", opencv_image_gray)


(error, intrinsic_matrix, distortion, rvecs, tvecs) = aruco.calibrateCameraAruco(corners, detected_ids, np.array([len(detected_ids)]), board, opencv_image_gray.shape, intrinsic_matrix, distortion, flags=cv2.CALIB_USE_INTRINSIC_GUESS)
rvecs = np.array([rvecs[0][0], rvecs[0][1], rvecs[0][2]]) #opencv stupid
tvecs = np.array([tvecs[0][0],tvecs[0][1],tvecs[0][1]], dtype=np.float32) #opencv stupid

#print(rvecs)
#print(tvecs)
#print(intrinsic_matrix)
#print(distortion)


x = 1171
y = 90
pixel_coordinates = np.array([[x, y, 1]])
pixel_coordinates = pixel_coordinates.T

rodrigues, jac = cv2.Rodrigues(rvec2)
rodrigues_inverse = np.linalg.inv(rodrigues)
rodrigues_translation = np.column_stack((rodrigues,tvec2))
projection_matrix = default_intrinsics.dot(rodrigues_translation)
intrinsics_inverse = np.linalg.inv(default_intrinsics)

inverse_newcam_mtx = np.linalg.inv(newcam_mtx)

xyz = np.array([[1000,500,-400,1.0]], dtype=np.float32)
xyz = xyz.T
suv = projection_matrix.dot(xyz)
scaling_factor = suv[2,0]
print(scaling_factor)

scaling_factor = 792

pixel_coordinates = scaling_factor*pixel_coordinates
xyz_c = inverse_newcam_mtx.dot(pixel_coordinates)
xyz_c = xyz_c-tvec2
world_coordinates = rodrigues_inverse.dot(xyz_c)
print(world_coordinates)


print("DONE")
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
