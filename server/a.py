import numpy as np
import cv2

layer1 = np.zeros((1024, 1024, 4))

color = (0, 0, 255, 255)
border_color = (0, 255, 0, 255)
radius = 10  # including border
border_width = 1
center = (255, 255)
cv2.circle(layer1, center, radius, color, -1)
cv2.circle(layer1, center, radius, border_color, border_width)

cv2.imwrite("out.png", layer1)
