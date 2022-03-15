# -*- coding: utf-8 -*-

import ui
import photos
import dialogs
import console
import math
import json
# import pathlib
import os
import time
import sys
from objc_util import ObjCInstance, on_main_thread

class Ease():
    @classmethod
    def liner(self, start, end, progress):
        return (end - start) * progress + start
    @classmethod
    def inSine(self, start, end, progress):
        return (end - start) * (1 - math.cos(progress * math.pi / 2)) + start
    @classmethod
    def inQuad(self, start, end, progress):
        return (end - start) * (progress ** 2) + start
    @classmethod
    def inQuad_inverse(self, start, end, value):
        progress = math.sqrt(max((value - start) / (end - start), 0))
        return progress
    @classmethod
    def InExpo(self, start, end, progress):
        return  0 if x == 0 else pow(2, 10 * x - 10);

def compairString(large, small):
    for l, s in zip(large, small):
        if l == s:
            continue
        else:
            if ord(l) > ord(s):
                return True
            else:
                return False

def sortedAlbums(albumAssetCollections):
    sorted = []
    for AAC in albumAssetCollections:
        for i, s in enumerate(sorted):
            if not compairString(AAC.title, s.title):
                sorted.insert(i, AAC)
                break
        else:
            sorted.append(AAC)
    return sorted

def getAlbumWithDialog():
    albumAssetCollections = photos.get_albums()
    albumAssetCollections = sortedAlbums(albumAssetCollections)
    albumTitles = [a.title for a in albumAssetCollections]
    selectedAlbumTitle = dialogs.list_dialog(
        title='アルバムを選択',
        items=albumTitles
        )
    
    if selectedAlbumTitle == None:
        exit()
    else:
        selectedAlbumNum = albumTitles.index(selectedAlbumTitle)
        return albumAssetCollections[selectedAlbumNum]

imageLastPos = (0,0)
trueImageLastPos = (0,0)

def setImageLastPos():
    global v
    global imageLastPos
    global trueImageLastPos
    global trueLastScale
    global lastScale
    imageLastPos = v['Image'].center
    trueImageLastPos = v['Image'].center
    trueLastScale = lastScale
    
touchBeganPos = (0,0)

def setTouchBeganPos(location):
    global touchBeganPos
    global lastTouchLocation
    touchBeganPos = location
    lastTouchLocation = location

lastTouchLocation = (0.0,0.0)

def moveImage(location):
    global imageLastPos
    global touchBeganPos
    global lastTouchLocation
    dpos = [da-a for (a, da) in zip(lastTouchLocation, location)]
    v['Image'].center += dpos # [a+da for (a, da) in zip(imageLastPos, dpos)]
    lastTouchLocation = location

lastScale = 1.0
trueLastScale = 1.0
initialImageScale = (0, 0)

def imageZoom(zoomCenter, scale, isUpdateSlider=False):
    global v
    global initialImageScale
    global lastScale
    global ancorHitboxSize
    global imageLastPos
    ancorHitboxSize = min(Ease.inSine(10,200,v['slider_zoom'].value), 70)
    v['Image'].height, v['Image'].width = initialImageScale[0] * scale, initialImageScale[1] * scale
    v['Image'].x -= (scale / lastScale - 1) * (zoomCenter[0] - v['Image'].x)
    v['Image'].y -= (scale / lastScale - 1) * (zoomCenter[1] - v['Image'].y)
    imageLastPos = (
        (imageLastPos[0] - zoomCenter[0]) * (scale / lastScale) + zoomCenter[0],
        (imageLastPos[1] - zoomCenter[1]) * (scale / lastScale) + zoomCenter[1]
        )
    lastScale = scale
    
    global boxCount
    if not boxCount == 0:
        global selectedBox
        setAncorValue(selectedBox)
        
    if isUpdateSlider:
        v['slider_zoom'].value = Ease.inQuad_inverse(1, 16, scale)

def imageZoomBySliderValue(zoomCenter):
    scale = Ease.inQuad(1, 16, v['slider_zoom'].value)
    imageZoom(zoomCenter, scale)

def onSliderZoom(_):
    global centerPos
    imageZoomBySliderValue(centerPos)
    
    
lastSliderValue = 0

def setLastZoomScale():
    global lastSliderValue
    lastSliderValue = v['slider_zoom'].value

def zoomWithDoubletouch(touch):
    global touchBeganPos
    global lastSliderValue
    global v
    coef = 800
    dy = touch.location[1] - touchBeganPos[1]
    v['slider_zoom'].value = lastSliderValue + dy / coef
    imageZoomBySliderValue(touchBeganPos)


def createAncorGuide():
    global ancorGuideNames
    global v
    for agn in ancorGuideNames:
        view = ui.View(frame=(0,0,100,100), background_color=(0.5, 0.5, 0.5, 0.3), name=agn)
        view.corner_radius = 50
        view.alpha = 0.0
        v['ancor_guide_layer'].add_subview(view)

def showAncorGuid():
    global v
    if not v['show_ancor_guid_switch'].value:
        return
    global ancorGuideNames
    global boxCount
    if boxCount == 0:
        return
    for agn in ancorGuideNames:
        v['ancor_guide_layer'][agn].alpha = 1.0

def hideAncorGuid():
    global ancorGuideNames
    for agn in ancorGuideNames:
        v['ancor_guide_layer'][agn].alpha = 0.0

def updateAncorGuid():
    global boxCount
    if boxCount == 0:
        return
    ancorsPos = getAncorsPos()
    global ancorGuideNames
    global ancorHitboxSize
    for i,agn in enumerate(ancorGuideNames):
        v['ancor_guide_layer'][agn].center = ancorsPos[i]
        v['ancor_guide_layer'][agn].width = ancorHitboxSize * 2
        v['ancor_guide_layer'][agn].height = ancorHitboxSize * 2
        v['ancor_guide_layer'][agn].corner_radius =  ancorHitboxSize
    
boxCount = 0

boxData = {}

def setAncorValue(box):
    global v
    global boxAncors
    global boxData
    
    boxData = {
        'x': box.x + v['Image'].x,
        'y': box.y + v['Image'].y,
        'absx': box.x,
        'absy': box.y,
        'w': box.width,
        'h': box.height
    }
    updateAncorGuid()
    # print(boxData)

selectedBox = ui.View

def selectBox():
    global selectedBox
    global v
    selectedBox = v['Image']['rangeBox' + str(boxCount - 1)]
    setAncorValue(selectedBox)

selectedAncor = 'tl'
ancorHitboxSize = 5

def getAncorsPos():
    global boxData
    return (
        (boxData['x']                   , boxData['y']                   ), # tl
        (boxData['x'] + boxData['w'] / 2, boxData['y']                   ), # tm
        (boxData['x'] + boxData['w']    , boxData['y']                   ), # tr
        (boxData['x']                   , boxData['y'] + boxData['h'] / 2), # ml
        (boxData['x'] + boxData['w']    , boxData['y'] + boxData['h'] / 2), # mr
        (boxData['x']                   , boxData['y'] + boxData['h']    ), # bl
        (boxData['x'] + boxData['w'] / 2, boxData['y'] + boxData['h']    ), # bm
        (boxData['x'] + boxData['w']    , boxData['y'] + boxData['h']    ), # br
        (boxData['x'] + boxData['w'] / 2, boxData['y'] + boxData['h'] / 2), # center
        )

def getNearestAncor(touch):
    global boxCount
    global ancorHitboxSize
    if boxCount == 0:
        return False
    global selectedAncor
    flag = False
    ancors = getAncorsPos()
    minDistance = ancorHitboxSize
    
    for i, ancor in enumerate(ancors):
        d = math.sqrt(sum([(a-b) ** 2 for (a, b) in zip(touch.location, ancor)]))
        if d < minDistance:
            minDistance = d
            ancornames = ['tl', 'tm', 'tr', 'ml', 'mr', 'bl', 'bm', 'br', 'center']
            selectedAncor = ancornames[i]
            flag = True
            
    return flag

def moveAncor(touch):
    global boxData
    global touchBeganPos
    global selectedAncor
    dpos = [b-a for (a, b) in zip(touchBeganPos, touch.location)]
    if selectedAncor in ['tl', 'tr', 'tm']:
        selectedBox.y = boxData['absy'] + min(dpos[1], boxData['h'])
        selectedBox.height = max(boxData['h'] - dpos[1], 1)
    if selectedAncor in ['bl', 'br', 'bm']:
        selectedBox.height = max(boxData['h'] + dpos[1], 1)
    if selectedAncor in ['tl', 'bl', 'ml']:
        selectedBox.x = boxData['absx'] + min(dpos[0], boxData['w'])
        selectedBox.width = max(boxData['w'] - dpos[0], 1)
    if selectedAncor in ['tr', 'br', 'mr']:
        selectedBox.width = max(boxData['w'] + dpos[0], 1)
    if selectedAncor in ['center']:
        selectedBox.y = boxData['absy'] + dpos[1]
        selectedBox.x = boxData['absx'] + dpos[0]

def createNewBox():
    global boxCount
    global v
    global centerPos
    global themeColors
    
    box = ui.View()
    box.border_width = 2
    boxColor = themeColors[1 if v['theme_switch'].value else 0]['box']
    boxBGColor = themeColors[1 if v['theme_switch'].value else 0]['boxbg']
    box.border_color = boxColor
    ancorDotSize = 5
    ancorDots = [
        ui.View(frame=(0,0,ancorDotSize,ancorDotSize), flex='RB', name='ancorDot0'),
        ui.View(frame=(50-ancorDotSize/2,0,ancorDotSize,ancorDotSize), flex='LRB', name='ancorDot1'),
        ui.View(frame=(100-ancorDotSize,0,ancorDotSize,ancorDotSize), flex='LB', name='ancorDot2'),
        ui.View(frame=(0,50-ancorDotSize/2,ancorDotSize,ancorDotSize), flex='RTB', name='ancorDot3'),
        ui.View(frame=(100-ancorDotSize,50-ancorDotSize/2,ancorDotSize,ancorDotSize), flex='LTB', name='ancorDot4'),
        ui.View(frame=(0,100-ancorDotSize,ancorDotSize,ancorDotSize), flex='RT', name='ancorDot5'),
        ui.View(frame=(50-ancorDotSize/2,100-ancorDotSize,ancorDotSize,ancorDotSize), flex='LRT', name='ancorDot6'),
        ui.View(frame=(100-ancorDotSize,100-ancorDotSize,ancorDotSize,ancorDotSize), flex='LT', name='ancorDot7'),
        ui.View(frame=(50-ancorDotSize/2,50-ancorDotSize/2,ancorDotSize,ancorDotSize), flex='LRTB', name='ancorDot8'),
        ]
    for d in ancorDots:
        d.background_color = boxColor
        box.add_subview(d)
    box.background_color = boxBGColor
    box.flex = 'WHLRTB'
    box.name = 'rangeBox' + str(boxCount)
    box.bounds = (0,0,200,200)
    v['Image'].add_subview(box)
    imageViewCenterGap = [a-b for (a, b) in zip(v['Image'].center, centerPos)]
    centerPosInImageView = (v['Image'].width / 2, v['Image'].height / 2)
    v['Image']['rangeBox' + str(boxCount)].center = [a-b for (a, b) in zip(centerPosInImageView, imageViewCenterGap)]
    boxCount += 1
    selectBox()

def onButtonCreate(_):
    createNewBox()

def makeYoloAnotationLine(imageTopLeftPos, imageBottomRightPos, boxView):
    width = imageBottomRightPos[0] - imageTopLeftPos[0]
    height = imageBottomRightPos[1] - imageTopLeftPos[1]
    yoloLine = {
        'label': 0,
        'x': (boxView.x - imageTopLeftPos[0] + boxView.width / 2) / width,
        'y': (boxView.y - imageTopLeftPos[1] + boxView.height / 2) / height,
        'w': boxView.width / width,
        'h': boxView.height / height
    }
    return '{} {:.6f} {:.6f} {:.6f} {:.6f}'.format(yoloLine["label"], yoloLine["x"], yoloLine["y"], yoloLine["w"], yoloLine["h"])

def clearAllBox():
    global v
    global boxCount
    for i in range(boxCount):
        v['Image'].remove_subview(v['Image']['rangeBox' + str(i)])
    boxCount = 0
    
@on_main_thread
def initProgressLabel():
    v['progress_label'].background_color = (1.0, 1.0, 1.0, 0.7)
    v['progress_label'].corner_radius = 16
    ObjCInstance(v['progress_label']).clipsToBounds = True

def updateProgressLabel():
    global v
    global photoNum
    global assets
    v['progress_label'].text = '{}/{}'.format(photoNum+1, len(assets))
    

photoNum = 0

def openImage():
    global photoNum
    global assets
    global centerPos
    global v
    
    v['slider_zoom'].value = 0
    onSliderZoom('_')
    v['Image'].center = centerPos
    clearAllBox()
    v['Image'].image = assets[photoNum].get_ui_image()
    with open('lastedited.json', 'r') as f:
        lastedited = json.load(f)
        lastedited['assetid'] = assets[photoNum].local_id
    with open('lastedited.json', 'w') as f:
        json.dump(lastedited, f)
    updateProgressLabel()
    
def openNextImage():
    global photoNum
    global assets
    if photoNum == len(assets) - 1:
        dialogs.alert('最新の写真です。', button1='OK', hide_cancel_button=True)
    else:
        photoNum += 1
    openImage()

def openPrevImagee():
    global photoNum
    global assets
    if photoNum == 0:
        dialogs.alert('最初の写真です',  button1='OK', hide_cancel_button=True)
    else:
        photoNum -= 1
    openImage()

def getNowImage():
    pass
    
def onButtonDone(_):
    global photoNum
    global assets
    global boxCount
    imageViewScale = (v['Image'].width, v['Image'].height)
    photoAsset = assets[photoNum]
    photoScale = (photoAsset.pixel_width, photoAsset.pixel_height)
    
    tl, br = (), ()
    if photoScale[0] * (imageViewScale[1] / photoScale[1]) > imageViewScale[0]: # 上下余白の場合
        padding = (imageViewScale[1] - photoScale[1] * (imageViewScale[0] / photoScale[0])) / 2 # 余白の幅
        tl = (0, padding)
        br = (imageViewScale[0], imageViewScale[1] - padding)
    else:                                                                       # 左右余白の場合
        padding = (imageViewScale[0] - photoScale[0] * (imageViewScale[1] / photoScale[1])) / 2 # 余白の高さ
        tl = (padding, 0)
        br = (imageViewScale[0] - padding, imageViewScale[1])
    
    yoloAnotationText = ''
    for i in range(boxCount):
        line = makeYoloAnotationLine(tl, br, v['Image']['rangeBox' + str(i)])
        yoloAnotationText += line + '\n'
    
    if not boxCount == 0:
        photoFileName = str(ObjCInstance(photoAsset).filename())
        # annotationFileName = pathlib.PurePath(photoFileName).stem + '.txt'
        annotationFileName = os.path.splitext(photoFileName)[0] + '.txt'
        if os.path.exists('result/' + annotationFileName):
            yesOrNo = console.alert('ファイルが存在します。', '上書きしますか？', 'はい', 'いいえ', hide_cancel_button=True)
            if yesOrNo == 1:
                with open('result/' + annotationFileName, 'w') as f:
                    f.write(yoloAnotationText)
        else:
            with open('result/' + annotationFileName, 'w') as f:
                f.write(yoloAnotationText)
            
    openNextImage()
    
def onButtonBack(_):
    openPrevImagee()

activeTouchIDs = {}

def getPinchCenterPos():
    global activeTouchIDs
    center = (
        (dict(activeTouchIDs).values()[0][0] + dict(activeTouchIDs).values()[1][0]) / 2,
        (dict(activeTouchIDs).values()[0][1] + dict(activeTouchIDs).values()[1][1]) / 2
    )
    return center

pinchBeganDistance = 0.0

def getPinchDistance():
    global activeTouchIDs
    distance = math.sqrt(
        (dict(activeTouchIDs).values()[0][0] - dict(activeTouchIDs).values()[1][0]) ** 2 +
        (dict(activeTouchIDs).values()[0][1] - dict(activeTouchIDs).values()[1][1]) ** 2
    )
    return distance
(む)
def pinch():
    global v
    global pinchBeganDistance
    global lastSliderValue
    global trueLastScale
    center = getPinchCenterPos()
    pinchDistance = getPinchDistance()
    zoomRate = (pinchDistance / pinchBeganDistance)
    imageZoom(center, trueLastScale * zoomRate, isUpdateSlider=True)
    #if zoomRate < 1:
    #    v['slider_zoom'].value = lastSliderValue - Ease.inQuad_inverse(1, 16, 1/zoomRate)
    #else:
    #    v['slider_zoom'].value = lastSliderValue + Ease.inQuad_inverse(1, 16, zoomRate)
    moveImage(center)
    imageZoomBySliderValue(center)

ancorGuideNames = [
    'ancorGuideTL',
    'ancorGuideTM',
    'ancorGuideTR',
    'ancorGuideML',
    'ancorGuideMR',
    'ancorGuideBL',
    'ancorGuideBM',
    'ancorGuideBR',
    'ancorGuideC',
    ]
    
isAncorEditing = False
lastTouchTimestamp = 0
doubleTouchFlag = False
multiTouchFlag = False

class touchView(ui.View):
    def touch_began(self, touch):
        global isAncorEditing
        global lastTouchTimestamp
        global doubleTouchFlag
        global activeTouchIDs
        global multiTouchFlag
        activeTouchIDs[touch.touch_id] = touch.location
        if lastTouchTimestamp + 0.2 > touch.timestamp:
            doubleTouchFlag = True
            setLastZoomScale()
        lastTouchTimestamp = touch.timestamp
        if getNearestAncor(touch):
            isAncorEditing = True
        else:
            setImageLastPos()
        
        if len(activeTouchIDs) == 2:
            multiTouchFlag = True
            setTouchBeganPos(getPinchCenterPos())
            global pinchBeganDistance
            pinchBeganDistance = getPinchDistance()
            setLastZoomScale()
        else:
            setTouchBeganPos(touch.location)
        hideAncorGuid()
    
    def touch_moved(self, touch):
        global isAncorEditing
        global doubleTouchFlag
        global activeTouchIDs
        global multiTouchFlag
        activeTouchIDs[touch.touch_id] = touch.location
        if lastTouchTimestamp + 0.08 < touch.timestamp:
            if multiTouchFlag:
                if len(activeTouchIDs) == 2:
                    pinch()
            elif doubleTouchFlag:
                zoomWithDoubletouch(touch)
            elif isAncorEditing:
                moveAncor(touch)
            else:
                moveImage(touch.location)
        
    def touch_ended(self, touch):
        global isAncorEditing
        global selectedBox
        global doubleTouchFlag
        global selectedAncor
        global multiTouchFlag
        if boxCount > 0:
            selectBox()
        del activeTouchIDs[touch.touch_id]
        if len(activeTouchIDs) == 0:
            multiTouchFlag = False
        isAncorEditing = False
        doubleTouchFlag = False
        selectedAncor = None
        updateAncorGuid()
        showAncorGuid()


def setPhotoNumByPickAssets(assets):
    global photoNum
    selectedAsset = photos.pick_asset(assets)
    photoNum = assets.index(selectedAsset)

def openLastEdetedFile():
    global assets
    global photoNum
    with open('lastedited.json', 'r') as f:
        lastEditing = json.loads(f.read())
        if not 'albumid' in lastEditing:
            return False
        LEAlbumID = lastEditing['albumid']
        albums = photos.get_albums()
        if not LEAlbumID in [a.local_id for a in albums]:
            return False
        albumIndex = [a.local_id for a in albums].index(LEAlbumID)
        assets = albums[albumIndex].assets
        assets.reverse()
        if not 'assetid' in lastEditing:
            return False
        LEAssetID = lastEditing['assetid']
        if not LEAssetID in [a.local_id for a in assets]:
            return False
        photoNum = [a.local_id for a in assets].index(LEAssetID)
        openImage()
        return True
        
def onButtonSelect(_):
    global assets
    selectedAlbum = getAlbumWithDialog()
    with open('lastedited.json', 'r') as f:
        lastedited = json.load(f)
        lastedited['albumid'] = selectedAlbum.local_id
    with open('lastedited.json', 'w+') as f:
        json.dump(lastedited, f)
    assets = selectedAlbum.assets
    assets.reverse()
    setPhotoNumByPickAssets(assets)
    openImage()

def onButtonDelete(_):
    global boxCount
    global v
    if boxCount == 0:
        return
    v['Image'].remove_subview(selectedBox)
    boxCount -= 1
    if boxCount == 0:
        return
    selectBox()

def onSwitchShowAncorGuid(sender):
    global boxCount
    if sender.value:
        if not boxCount == 0:
            setAncorValue(selectedBox)
            showAncorGuid()
    else:
        hideAncorGuid()
        
is2PColor = False
themeColors = (
    {
        'box': (1.0, 0.0, 0.0, 1.0),
        'boxbg': (1.0, 0.0, 0.0, 0.2),
        'guide': (0.0, 1.0, 0.0, 1.0)
    },
    {
        'box': (0.0, 1.0, 1.0, 1.0),
        'boxbg': (0.0, 1.0, 1.0, 0.2),
        'guide': (1.0, 0.0, 1.0, 1.0)
    }
)

def onSwitch2PColor(sender):
    global v
    global boxCount
    global is2PColor
    global themeColor
    index = 0
    if sender.value:
        index = 1
    v['guidBox'].border_color = themeColors[index]['guide']
    for i in range(boxCount):
        v['Image']['rangeBox' + str(i)].border_color = themeColors[index]['box']
        v['Image']['rangeBox' + str(i)].background_color = themeColors[index]['boxbg']
        for j in range(9):
            v['Image']['rangeBox' + str(i)]['ancorDot' + str(j)].background_color = themeColors[index]['box']
        
centerPos = (0,0)

def awake():
    global v
    initProgressLabel()
    v['touch_panel'].multitouch_enabled = True
    v['slider_zoom'].continuous = True
    v['Image'].content_mode = ui.CONTENT_SCALE_ASPECT_FIT

def start():
    global v
    global centerPos
    global initialImageScale
    centerPos = v['touch_panel'].center
    initialImageScale = [v['touch_panel'].height, v['touch_panel'].width]
    if not openLastEdetedFile():
        onButtonSelect('_')
    createAncorGuide()

if __name__ == '__main__':
    global v
    
    v = ui.load_view()
    awake()
            
    v.present('fullscreen')
    start()
