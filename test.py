from darknetpy.detector import Detector
from matplotlib import image, patches, pyplot as plt
import cv2
from PIL import Image, ImageDraw, ImageEnhance, ImageColor

#cap=cv2.VideoCapture(0)


detector = Detector('fock/DarkNet_YOLOV3/cfg/obj.data',
                    'fock/DarkNet_YOLOV3/cfg/yolov3-tiny.cfg',
                    'fock/DarkNet_YOLOV3/yolov3-tiny_final.weights')

results = detector.detect('color.png')

"""
fig, ax = plt.subplots(1)
ax.imshow(image.imread('color.png'))

colors = ['r', 'pink', 'y']

for i, box in enumerate(results):
    l = box['left']
    t = box['top']
    b = box['bottom']
    r = box['right']
    c = box['class']
    color = colors[i % len(colors)]
    
    rect = patches.Rectangle(
        (l, t), 
        r - l, 
        b - t,
        linewidth = 1, 
        edgecolor = color, 
        facecolor = 'none'
    )
    
    ax.text(l, t, c, fontsize = 12, bbox = {'facecolor': color, 'pad': 2, 'ec': color})
    ax.add_patch(rect)

plt.show('color_boxes.png')
"""

#ret, frame = cap.read()
#cv2.imwrite('webcam_capture.png', frame)

#results=detector.detect('webcam_capture.png')

amount_of_objects=len(results)
counter=0
"""
for i in range(len(results)):
	d=results[counter]
	if d['class'] == 'car':
		classify=d['class']
		prob=d['prob']
		width=d['right']-d['left']
		height=d['bottom']-d['top']
		x_coord=width/2+d['left']
		y_coord=height/2+d['top']
		item=(classify, prob, width, height, x_coord, y_coord)
		break
	counter += 1
"""
source_img = Image.open('color.png').convert("RGBA")
res = []
for j in range(amount_of_objects):
	d=results[j]
	width=d['right']-d['left']
	height=d['bottom']-d['top']
	x_coord=width/2+d['left']
	y_coord=height/2+d['top']

	draw = ImageDraw.Draw(source_img)
	draw.rectangle(((d['left'], d['top']), (d['right'], d['bottom'])),fill=None, outline=(200,0,150), width=6)
	draw.text((x_coord, y_coord), d['class'])
	source_img.save('testing2.png')


"""
draw = ImageDraw.Draw(source_img)
draw.rectangle(((0, 00), (100, 100)), fill="black")
draw.text((20, 70), "something123", font=ImageFont.truetype("font_path123"))

source_img.save(out_file, "JPEG")

"""


#cap.release()
#print(res)
#x=len(results)
#print(results)
#print(item)
#print(x)
