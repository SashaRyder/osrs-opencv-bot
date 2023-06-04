import cv2
import numpy as np


def template_matches(template, img):
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.5
    loc = np.where( res >= threshold)
    return zip(*loc[::-1])