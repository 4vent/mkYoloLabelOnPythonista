import ui
import photos
import dialogs
import console
import math
import json
import pathlib
from objc_util import ObjCInstance

class Ease():
    def liner(start, end, progress):
        return (end - start) * progress + start
    def inSine(start, end, progress):
        return (end - start) * (1 - math.cos(progress * math.pi / 2)) + start
    def inQuad(start, end, progress):
        return (end - start) * (progress ** 2) + start

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

def setImageLastPos():
    global v
    global imageLastPos
    imageLastPos = v['Image'].center
    
touchBeganPos = (0,0)

def setTouchBeganPos(touch):
    global touchBeganPos
    touchBeganPos = touch.location

def moveImage(touch):
    global imageLastPos
    global touchBeganPos
    dpos = [da-a for (a, da) in zip(touchBeganPos, touch.location)]
    v['Image'].center = [a+da for (a, da) in zip(imageLastPos, dpos)]

lastScale = 1.0

def onSliderZoom(_):
    global v
    global initialImageScale
    global lastScale
    global centerPos
    global ancorHitboxSize
    scale = Ease.inQuad(1, 10, v['slider_zoom'].value)
    ancorHitboxSize = min(scale ** 10 * 5, 70)
    v['Image'].height, v['Image'].width = initialImageScale[0] * scale, initialImageScale[1] * scale
    v['Image'].x -= (scale / lastScale - 1) * (centerPos[0] - v['Image'].x)
    v['Image'].y -= (scale / lastScale - 1) * (centerPos[1] - v['Image'].y)
    lastScale = scale
    
lastSliderValue = 0

def setLastZoomScale():
    global lastSliderValue
    lastSliderValue = v['slider_zoom'].value

def zoomWithDoubletouch(touch):
    global touchBeganPos
    global lastSliderValue
    global v
    coef = 500
    dy = touch.location[1] - touchBeganPos[1]
    v['slider_zoom'].value = lastSliderValue + dy / coef
    onSliderZoom('_')


def createAncorGuide():
    global ancorGuideNames
    global v
    for agn in ancorGuideNames:
        view = ui.View(frame=(0,0,10,10), background_color=(1.0, 1.0, 1.0, 0.1), name=agn)
        view.corner_radius = 5
        v['touch_panel'].add_sub_view(view)

def updateAncorGuidPos():
    ancorsPos = getAncorsPos()
    global ancorGuideNames
    for i,agn in enumerate(ancorGuideNames):
        v['touch_panel'][agn].center = ancorsPos[i]

def showAncorGuid():
    global ancorGuideNames
    for agn in ancorGuideNames:
        v['touch_panel'][agn].alpha = 0.0

def hideAncorGuid():
    global ancorGuideNames
    for agn in ancorGuideNames:
        v['touch_panel'][agn].alpha = 1.0

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
    updateAncorGuidPos()
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
    
    box = ui.View()
    box.border_width = 2
    box.border_color = (1.0, 0.0, 0.0, 1.0)
    ancorDotSize = 5
    ancorDots = [
        ui.View(frame=(0,0,ancorDotSize,ancorDotSize), flex='RB'),
        ui.View(frame=(50-ancorDotSize/2,0,ancorDotSize,ancorDotSize), flex='LRB'),
        ui.View(frame=(100-ancorDotSize,0,ancorDotSize,ancorDotSize), flex='LB'),
        ui.View(frame=(0,50-ancorDotSize/2,ancorDotSize,ancorDotSize), flex='RTB'),
        ui.View(frame=(100-ancorDotSize,50-ancorDotSize/2,ancorDotSize,ancorDotSize), flex='LTB'),
        ui.View(frame=(0,100-ancorDotSize,ancorDotSize,ancorDotSize), flex='RT'),
        ui.View(frame=(50-ancorDotSize/2,100-ancorDotSize,ancorDotSize,ancorDotSize), flex='LRT'),
        ui.View(frame=(100-ancorDotSize,100-ancorDotSize,ancorDotSize,ancorDotSize), flex='LT'),
        ui.View(frame=(50-ancorDotSize/2,50-ancorDotSize/2,ancorDotSize,ancorDotSize), flex='LRTB'),
        ]
    for d in ancorDots:
        d.background_color = (1.0, 0.0, 0.0, 1.0)
        box.add_subview(d)
    box.background_color = (1.0, 0.0, 0.0, 0.2)
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
    return f'{yoloLine["label"]} {yoloLine["x"]:.6f} {yoloLine["y"]:.6f} {yoloLine["w"]:.6f} {yoloLine["h"]:.6f}'

def clearAllBox():
    global v
    global boxCount
    for i in range(boxCount):
        v['Image'].remove_subview(v['Image']['rangeBox' + str(i)])
    boxCount = 0

photoNum = 0

def openImage():
    global photoNum
    global assets
    clearAllBox()
    v['Image'].image = assets[photoNum].get_ui_image()
    with open('lastedited.json', 'r') as f:
        lastedited = json.load(f)
        lastedited['assetid'] = assets[photoNum].local_id
    with open('lastedited.json', 'w') as f:
        json.dump(lastedited, f)
    
def openNextImage():
    global photoNum
    global centerPos
    global assets
    if photoNum == len(assets) - 1:
        dialogs.alert('最新の写真です。', button1='OK', hide_cancel_button=True)
    else:
        photoNum += 1
    v['slider_zoom'].value = 0
    onSliderZoom('_')
    v['Image'].center = centerPos
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
    
    photoFileName = str(ObjCInstance(photoAsset).filename())
    annotationFileName = pathlib.PurePath(photoFileName).stem + '.txt'
    if not boxCount == 0:
        try:
            with open('result/' + annotationFileName, 'x') as f:
                f.write(yoloAnotationText)
        except FileExistsError:
            yesOrNo = console.alert('ファイルが存在します。', '上書きしますか？', 'はい', 'いいえ', hide_cancel_button=True)
            if yesOrNo == 1:
                with open('result/' + annotationFileName, 'w') as f:
                    f.write(yoloAnotationText)
            
    openNextImage()

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
class touchView(ui.View):
    def touch_began(self, touch):
        global isAncorEditing
        global lastTouchTimestamp
        global doubleTouchFlag
        if lastTouchTimestamp + 0.2 > touch.timestamp:
            doubleTouchFlag = True
            setLastZoomScale()
        lastTouchTimestamp = touch.timestamp
        if getNearestAncor(touch):
            isAncorEditing = True
        else:
            setImageLastPos()
            
        setTouchBeganPos(touch)
        hideAncorGuid()
    
    def touch_moved(self, touch):
        global isAncorEditing
        global doubleTouchFlag
        if lastTouchTimestamp + 0.08 < touch.timestamp:
            if doubleTouchFlag:
                zoomWithDoubletouch(touch)
            elif isAncorEditing:
                moveAncor(touch)
            else:
                moveImage(touch)
        
    def touch_ended(self, touch):
        global isAncorEditing
        global selectedBox
        global doubleTouchFlag
        global selectedAncor
        if boxCount > 0:
            selectBox()
        
        isAncorEditing = False
        doubleTouchFlag = False
        selectedAncor = None
        updateAncorGuidPos()
        showAncorGuid()


def setPhotoNumByPickAssets(assets):
    global photoNum
    selectedAsset = photos.pick_asset(assets)
    photoNum = assets.index(selectedAsset)

def start():
    global v
    global initialImageScale
    global centerPos
    initialImageScale = [v['Image'].height, v['Image'].width]
    centerPos = v['Image'].center
    v['slider_zoom'].continuous = True
    createAncorGuide()

def openLastEdetedFile():
    global assets
    global photoNum
    with open('lastedited.json', 'r') as f:
        lastEditing = json.loads(f.read())
        LEAlbumID = lastEditing['albumid']
        albums = photos.get_albums()
        if not LEAlbumID in [a.local_id for a in albums]:
            return False
        albumIndex = [a.local_id for a in albums].index(LEAlbumID)
        assets = albums[albumIndex].assets
        assets.reverse()
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
    

if __name__ == '__main__':
    global v
    global assets
    
    v = ui.load_view()
    
    v['Image'].content_mode = ui.CONTENT_SCALE_ASPECT_FIT
            
    if not openLastEdetedFile():
        onButtonSelect('_')
    
    v.present('fullscreen')
    start()
