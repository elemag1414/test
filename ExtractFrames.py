import os, sys, cv2
import numpy as np
import time 
from mouse_util import MouseGesture, COLOR
from tkinter import Tk
from tkinter.filedialog import askopenfilename



def printHelp():
  print('''
  q           : exit program
  p (or space): toggle pause/play
  w           : generate frame images and mask filter images

  Instruction: 
    1. Choose threshold value using trackbar.
    2. Investigate Filtered Frames through playing it.
    3. If you want modify filtering area, 
        press p to pause the video.
        Then, select new area by click and drag the mouse to choose.
        You can select new area by click and drag new area 
        Once you find appropriate area to filter, then press p to continue filtering.
    4. If track bar value and filter area are correctly set up, 
        then generate the image frame and mask filter image by pressing 'w'
  ''')

def frameWaitTime(st):
  dTime = int(time.time() - st) 
  dTime = 1 if dTime < 0 else dTime
  return dTime 

def maskingFrame(_img, threshold, overlay=False):
  blank = np.zeros(_img.shape, dtype=np.uint8)

  if _img is None:
    return _img
  img = _img.copy()
  grayImg = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

  try: 
    min, max = threshold
  except:
    min = 0
    max = threshold
  maskPixels = np.where((grayImg < max) & (grayImg > min))

  if overlay:
    img[maskPixels] = COLOR.yellow 
    return img
  else:
    blank[maskPixels] = COLOR.white
    return blank

def trackbarOnChange(pos):
    print(f"value: {pos}")

# Flags
write = False
loop = True
pause = False 


baseDir = '/home/etri/DataSets/GasDetection/FLAB/20220922/'
# fileLists = [x for x in os.listdir(baseDir) if x.split('.')[-1].lower() == 'mp4']
# print('Number of files: ', len(fileLists))


while True:
  path = askopenfilename(title="Select folder", filetypes=(('mp4 files', '*.mp4'), ("all files", "*.*")), initialdir=baseDir)
  print(f'path: {path}')

  if (len(path) == 0) or not(os.path.exists(path)):
    print(f'path: {path}')
    _keyIn = input(f"Press enter to select folder ['q' to exit]... ")
    if _keyIn.strip().lower() == 'q':
      print("exit...")
      sys.exit()
  elif os.path.exists(path):
    selectedFile = path.split('/')[-1]
    break
  else: 
    _keyIn = input(f"{path} is not valid video file\nPress enter to select folder ['q' to exit]... ")
    if _keyIn.strip().lower() == 'q':
      print("exit...")
      sys.exit()


# selectedFile = fileLists[0]

dataFileName = '.'.join(selectedFile.split('.')[:-1])
saveDataBaseDir = os.path.join('./data', dataFileName)
imDataDir = os.path.join(saveDataBaseDir, 'Images')
if not os.path.isdir(imDataDir):
  os.makedirs(imDataDir)
maskDataDir = os.path.join(saveDataBaseDir, 'Masks')
if not os.path.isdir(maskDataDir):
  os.makedirs(maskDataDir)


vidFile = os.path.join(baseDir, selectedFile)

windowName = selectedFile
cv2.namedWindow(windowName)
cv2.createTrackbar("threshold", windowName, 0, 255, trackbarOnChange)
cv2.setTrackbarPos("threshold", windowName, 100)

# Mouse Gesture
mouseGesture = MouseGesture(windowName)

font = cv2.FONT_HERSHEY_SIMPLEX

cap = cv2.VideoCapture(vidFile)

FPS = cap.get(cv2.CAP_PROP_FPS)
NumFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
# print(FPS)
frameTime = int(1000/FPS)
fcnt = 1
prevFrame = None

while True:
  st = time.time()

  thresh = cv2.getTrackbarPos("threshold", windowName)
  success, frame = cap.read()
  if not success:
    if loop:
      cap = cv2.VideoCapture(vidFile)
      success, frame = cap.read()
      fcnt = 1
    else:
      print('exit')
      break

  # User Input
  dTime = frameWaitTime(st)
  keyIn = cv2.waitKey(frameTime - dTime)
  if keyIn == ord('q'):
    break 
  elif keyIn == ord('p') or keyIn == ord(' '):
    pause = not pause 
  elif keyIn == ord('h'):
    printHelp()
  elif keyIn == ord('w'):
    loop = False
    write = True
    cap = cv2.VideoCapture(vidFile)
    success, frame = cap.read()
    fcnt = 1

  
  if pause:
    cv2.putText(prevFrame, f"pause", (300, 30), font, 1, COLOR.red, 2)
    mouseGesture.updateFrame(prevFrame)
    prevFrame = mouseGesture.getNewFrame()
    cv2.imshow(windowName, prevFrame)
    continue

  # Main Mask Filtering
  if mouseGesture.boxCoord is not None:
    _frame = mouseGesture.getPatchArea(frame)
    maskedFrame = maskingFrame(_frame, thresh)
  else:
    maskedFrame = maskingFrame(frame, thresh)

  if write:
    print('im path: ', os.path.join(imDataDir, f"{dataFileName}#{fcnt}.jpg")) 
    cv2.imwrite(os.path.join(imDataDir, f"{dataFileName}#{fcnt}.jpg"), frame)
    cv2.imwrite(os.path.join(maskDataDir, f"{dataFileName}#{fcnt}.jpg"), maskedFrame)
    if not(fcnt/10):
      print(f"PROGRESS: {fcnt*100/NumFrames:.2f}")

  mergedFrame = np.concatenate((frame, maskedFrame), axis=1)
  cv2.putText(mergedFrame, f"{fcnt}/{NumFrames}", (10, 30), font, 1, COLOR.yellow, 2)
  prevFrame = mergedFrame.copy()

  cv2.imshow(windowName, mergedFrame)

  fcnt += 1

cv2.destroyAllWindows()
cap.release()