import cv2
import numpy as np


def template_matches(template, img, threshold = 0.5, matchType = cv2.TM_CCOEFF_NORMED):
    res = cv2.matchTemplate(img, template, matchType)
    loc = np.where( res >= threshold)
    return zip(*loc[::-1])