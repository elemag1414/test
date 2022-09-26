import os, sys, cv2
import numpy as np
import time 
from mouse_util import MaskMouseGesture, COLOR
from tkinter import Tk
from tkinter.filedialog import askdirectory

baseDir = './data/'

while True:
  path = askdirectory(title="Select folder", initialdir=baseDir)
  print(f'path: {path}')

  if len(path) == 0:
    _keyIn = input(f"{path} is not valid folder\nPress enter to select folder ['q' to exit]... ")
    if _keyIn.strip().lower() == 'q':
      print("exit...")
      sys.exit()
  elif ('Images' in os.listdir(path)) and ('Masks' in os.listdir(path)):
    print(f'{path} is selected')
    selectedVideo = path.split('/')[-1]
    break
  else:
    _keyIn = input(f"{path} is not valid folder\nPress enter to select folder ['q' to exit]... ")
    if _keyIn.strip().lower() == 'q':
      print("exit...")
      sys.exit()

# vidLists = os.listdir(baseDir) 
# print('Number of video folders: ', len(vidLists))
# selectedVideo = vidLists[0]

imDataDir = os.path.join(baseDir, selectedVideo, 'Images')
print(f'imDataDir: {imDataDir}')
maskDataDir = os.path.join(baseDir, selectedVideo, 'Masks')
print(f'maskDataDir: {maskDataDir}')

assert os.path.exists(imDataDir)
assert os.path.exists(maskDataDir)

imageFiles = sorted([os.path.basename(x) for x in os.listdir(imDataDir) if x.split('.')[-1].lower() == 'jpg'])

fcntLists = sorted([int((''.join(x.split('#')[-1])).split('.')[0]) for x in imageFiles])

cv2.namedWindow(selectedVideo)

# Mouse Gesture
mouseGesture = MaskMouseGesture(selectedVideo)


### functions
def printHelp():
  print('''
  q           : exit program
  n (or space): next frame
  u           : undo all modification
  j           : increase erase box size
  k           : decrease erase box size
  ''')

def overlayFrame(im, mask):
  frame = im.copy()
  cmask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
  pixels = np.where(cmask>250)
  frame[pixels] = COLOR.red
  return frame

def eraseArea(mask, boxCoord):
  startX, startY = boxCoord[0]
  endX, endY = boxCoord[1]
  # print(f"start: {startX}, {startY}")
  # print(f"end: {endX}, {endY}")
  mask[startY:endY, startX:endX] = COLOR.black
  return mask

def saveMask(mask, fileName):
  _fileName = os.path.join(maskDataDir, fileName)
  cv2.imwrite(_fileName, mask)

def caption(im, msg, location=(250, 30)):
  return cv2.putText(im, msg, location, cv2.FONT_HERSHEY_SIMPLEX, .8, COLOR.yellow, 2)

def overlayImage(im1, im2, weight=50): # weight should be in [1, 99]
  return cv2.addWeighted(im1, float(100-weight)*.01, im2, float(weight)*.01, 0)

def changeMaskColor(mask, color=COLOR.red):
  cmask = mask.copy()
  gmask = cv2.cvtColor(cmask.copy(), cv2.COLOR_BGR2GRAY)
  pixels = np.where(gmask>250)
  cmask[pixels] = color 
  return cmask

###

exitSet = False
for fcnt in fcntLists:
  image = f"{selectedVideo}#{fcnt}.jpg"
  if exitSet:
    break
  print(f'[loop] imDataDir: {imDataDir}, image: {image}')
  im = cv2.imread(os.path.join(imDataDir, image))
  assert os.path.exists(os.path.join(imDataDir, image)), os.path.join(imDataDir, image)
  im = caption(im, image) 
  mask = cv2.imread(os.path.join(maskDataDir, image))
  maskBackup = mask.copy()
  assert os.path.exists(os.path.join(maskDataDir, image)), os.path.join(maskDataDir, image)

  while True:
    overlayIm = overlayImage(im, changeMaskColor(mask), 20)
    mergeFrame = np.concatenate((mask, overlayIm), axis=1)
    mouseGesture.updateFrame(mergeFrame)
    boxCoord = mouseGesture.getBoxCoord()

    if boxCoord is not None:
      if mouseGesture.lbpressed:
        mask = eraseArea(mask, boxCoord)
        overlayIm = overlayImage(im, changeMaskColor(mask), 20)
        mergeFrame = np.concatenate((mask, overlayIm), axis=1)
        mergeFrame = cv2.rectangle(mergeFrame, boxCoord[0], boxCoord[1], COLOR.red, 2)    # Mouse box
      else:
        mergeFrame = cv2.rectangle(mergeFrame, boxCoord[0], boxCoord[1], COLOR.yellow, 2) # Mouse box
      
    cv2.imshow(selectedVideo, mergeFrame)
    
    keyIn = cv2.waitKey(10)
    if keyIn == ord('q'):
      if mouseGesture.isModified: 
        print(f"Save Modified Mask {image}")
        saveMask(mask, image)
        mouseGesture.isModified=False
      exitSet = True
      break
    elif keyIn == ord('h'):
      printHelp()
    elif keyIn == ord('j'):
      print('Increase bbox')
      mouseGesture.increaseBoxSize()
    elif keyIn == ord('k'):
      print("Decrease bbox")
      mouseGesture.decreaseBoxSize()
    elif keyIn == ord('u'): # undo modifying mask
      mask = maskBackup.copy()
      mouseGesture.isModified = False 
    elif keyIn == ord('n') or keyIn == ord(' '):
      if mouseGesture.isModified: 
        print(f"Save Modified Mask {image}")
        saveMask(mask, image)
        mouseGesture.isModified=False
      break

  
  
