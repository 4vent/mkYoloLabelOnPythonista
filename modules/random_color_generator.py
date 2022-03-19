# -*- coding: utf-8 -*-

import random
import colorsys

class rgb():
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        self.tuple = (r, g, b)

def getRandomColor(hMin=0, hMax=360, sMin=0, sMax=1, vMin=0, vMax=1):
    h = random.uniform(hMin, hMax)
    s = random.uniform(sMin, sMax)
    v = random.uniform(vMin, vMax)
    return rgb(*colorsys.hsv_to_rgb(h/360, s, v))
