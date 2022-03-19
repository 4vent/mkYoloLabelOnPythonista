# -*- coding: utf-8 -*-

def yoloPos2BoxPos(
    photoX,
    photoY,
    photoWidth,
    photoHeight,
    yoloCenterX,
    yoloCenterY,
    yoloWidth,
    yoloHeight
    ):
    return {
        'x': float(yoloCenterX) * photoWidth + photoX,
        'y': float(yoloCenterY) * photoHeight + photoY,
        'width': float(yoloWidth) * photoWidth,
        'height': float(yoloHeight) * photoHeight
    }

def boxPos2YoloPos(
    photoX,
    photoY,
    photoWidth,
    photoHeight,
    boxCenterX,
    boxCenterY,
    boxWidth,
    boxHeight
    ):
    return {
        'x': (boxCenterX - photoX) / float(photoWidth),
        'y': (boxCenterY - photoY) / float(photoHeight),
        'width': boxWidth / float(photoWidth),
        'height': boxHeight / float(photoHeight)
    }

def makeYoloAnotationLine(labelIndex, photo, boxView):
    yoloLine = boxPos2YoloPos(
        photo['x'],
        photo['y'],
        photo['width'],
        photo['height'],
        boxView.center[0],
        boxView.center[1],
        boxView.width,
        boxView.height
        )
    return '{} {:.6f} {:.6f} {:.6f} {:.6f}'.format(labelIndex, yoloLine["x"], yoloLine["y"], yoloLine["width"], yoloLine["height"])
