import numpy as np
import cv2

def print_img(img):
    cv2.imshow('image', img)
    k = cv2.waitKey(0)
    if k == 27:         # wait for ESC key to exit
        cv2.destroyAllWindows()

img = cv2.imread('car.jpg')
height, width, channels = img.shape
height_half, height_quarter = height // 2, height // 4
width_half, width_quarter = width // 2, width // 4
img_half = cv2.resize(img, (width_half, height_half), interpolation=cv2.INTER_AREA)
img_quarter = cv2.resize(img, (width_quarter, height_quarter), interpolation=cv2.INTER_AREA)

edges = cv2.Canny(img_half, 100, 200)
edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

kernel = np.ones((5, 5), np.float32) / 25
avg = cv2.filter2D(img_quarter, -1, kernel)

blur = cv2.GaussianBlur(img_quarter, (5,5), 0)

kernel = np.ones((5, 5), np.uint8)
erosion = cv2.erode(img_quarter, kernel, iterations = 1)

random = np.random.randint(0, 255, img_quarter.shape, dtype=np.uint8)

result = np.zeros((height, width + width_half, channels), np.uint8)
result[:height, :width] = img
result[:height_half, width:width+width_half] = edges
result[height_half:height_half+height_quarter, width:width+width_quarter] = avg
result[height_half:height_half+height_quarter, width+width_quarter:width+width_half] = blur
result[height_half+height_quarter:height-1, width:width+width_quarter] = erosion
result[height_half+height_quarter:height-1, width+width_quarter:width+width_half] = random

cv2.imwrite('result.jpg', result)