# -*- coding: utf-8 -*-

import unicodedata

def getStringWidth(str=''):
    width = 0
    half = ['H', 'Na', 'N']
    for c in str:
        # uc = ord(c)
        if unicodedata.east_asian_width(c) in half:
            width += 1
        else:
            width += 2
    return width