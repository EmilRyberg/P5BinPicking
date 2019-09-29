import pyrealsense2 as rs
from PIL import Image as pimg
import numpy as np
import time


pipeline = rs.pipeline()
cfg = rs.config()
cfg.enable_stream(rs.stream.depth,1280,720,rs.format.z16,30)
cfg.enable_stream(rs.stream.color,1920, 1080, rs.format.rgb8, 30)
profile = pipeline.start(cfg)

try:

        # Wait for a coherent pair of frames: depth and color
        for i in range(30):
            frames=pipeline.wait_for_frames()
            
        while True:
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
    
            # Convert images to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
    
            depth_image_tf = np.zeros((720,1280), dtype=np.uint8)
            
            for y in range(720):
                for x in range(1280):
                    pixel = (255/3000) * depth_image[y,x]
                    if pixel >255:
                        pixel = 255
                    depth_image_tf[y,x] = pixel
        
            depth_image_ready_to_save = pimg.fromarray(depth_image_tf, 'L')
            color_image_ready_to_save = pimg.fromarray(color_image, 'RGB')
            
            #depth_image_ready_to_save.show()
            #color_image_ready_to_save.show()
            timestamp = str(time.time())
            color_image_ready_to_save.save('color'+timestamp+'.png')
            depth_image_ready_to_save.save('depth'+timestamp+'.png')
            input('saved '+timestamp)

finally:

    # Stop streaming
    pipeline.stop()