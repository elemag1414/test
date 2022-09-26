import cv2 
import numpy as np


class COLOR:
  red = (0, 0, 255)
  blue = (255, 0, 0)
  white = (255, 255, 255)
  black = (0, 0, 0)
  gray = (127, 127, 127)
  yellow = (30, 255, 255)

class MouseGesture:
  def __init__(self, window):
    self.window = window
    self.isBox = False # if new box coord set
    self.modifyBox = False
    self.prevFrame = None
    self.curFrame = None
    self.stCoord = None
    self.endCoord = None
    self.boxCoord = None

  def updateFrame(self, frame):
    if self.prevFrame is None:
      self.prevFrame = frame.copy()
    cv2.setMouseCallback(self.window, self.callback, frame)
  
  def getNewFrame(self):
    if self.prevFrame is None:
      print("NO FRAME To Process")
      return False
    if self.boxCoord is None:
      return self.prevFrame
    self.tmpFrame = self.prevFrame.copy()
    return cv2.rectangle(self.tmpFrame, self.boxCoord[0], self.boxCoord[1], COLOR.yellow, 2)

  def getPatchArea(self, frame):
    if self.boxCoord is None:
      return frame
    whiteImg = np.ones(frame.shape, dtype=np.uint8)*255
    stPnt, endPnt = self.boxCoord
    whiteImg[stPnt[1]:endPnt[1], stPnt[0]:endPnt[0]] = frame[stPnt[1]:endPnt[1], stPnt[0]:endPnt[0]]
    return whiteImg

  def sortCoord(self, st, end):
    st_x = min(st[0], end[0])
    st_y = min(st[1], end[1])
    end_x = max(st[0], end[0])
    end_y = max(st[1], end[1])
    return [(st_x, st_y), (end_x, end_y)]

  def callback(self, event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:    
      print(f"LEFT BUTTON DOWN ({x}, {y})")
      self.modifyBox = True
      self.stCoord = (x, y)
      self.endCoord = (x, y)
      # self.boxCoord = [self.stCoord, self.endCoord]
      self.boxCoord = self.sortCoord(self.stCoord, self.endCoord)
    elif event == cv2.EVENT_LBUTTONUP:
      x = min(x, self.prevFrame.shape[1])
      y = min(y, self.prevFrame.shape[0])
      x = max(x, 0)
      y = max(y, 0)
      self.endCoord = (x, y)
      self.boxCoord = self.sortCoord(self.stCoord, self.endCoord)
      self.modifyBox = False
      print(f"LEFT BUTTON RELEASED  Box: {self.boxCoord}")
    elif event == cv2.EVENT_MOUSEMOVE:
      if self.modifyBox:
        print(f"(x, y): ({x}, {y})")
        self.endCoord = (x, y)
        self.boxCoord = self.sortCoord(self.stCoord, self.endCoord)




class MaskMouseGesture:
  def __init__(self, window):
    self.window = window
    self.prevFrame = None
    self.curCoord = None
    self.boxCoord = None
    self.lbpressed = False
    self.maxX = 0
    self.maxY = 0
    self.minBoxSize = 12
    self.boxSize = self.minBoxSize
    self.boxSizeStep = 4
    self.isModified = False

  def getCoordinate(self):
    if self.lbpressed:
      return self.curCoord 
    else: 
      return None
    
  def increaseBoxSize(self):
    self.boxSize += self.boxSizeStep 
    self.boxSize = min(max(self.maxX, self.maxY), self.boxSize)

  def decreaseBoxSize(self):
    self.boxSize -= self.boxSizeStep
    self.boxSize = max(self.minBoxSize, self.boxSize)

  def checkBoundary(self, value, maxValue):
    return min(max(0, value), maxValue)

  def checkBoxBoundary(self, boxCoord):
    (startX, startY), (endX, endY) = boxCoord
    startX = self.checkBoundary(startX, self.maxX) 
    startY = self.checkBoundary(startY, self.maxY) 
    endX = self.checkBoundary(endX, self.maxX) 
    endY = self.checkBoundary(endY, self.maxY) 
    return [(startX, startY), (endX, endY)]


  def getBoxCoord(self):
    if self.curCoord is None: return None
    x, y = self.curCoord
    halfSize = 0.5 * self.boxSize
    startX = int(x - halfSize)
    endX = int(x + halfSize)
    startY = int(y - halfSize)
    endY = int(y + halfSize)
    self.boxCoord = self.checkBoxBoundary([(startX, startY), (endX, endY)])
    return self.boxCoord


  def updateFrame(self, frame):
    if self.prevFrame is None:
      self.prevFrame = frame.copy()
      self.maxX = int(.5 * frame.shape[1])
      self.maxY = int(frame.shape[0])
    cv2.setMouseCallback(self.window, self.callback, frame)


  def callback(self, event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:    
      # print(f"LEFT BUTTON DOWN ({x}, {y})")
      self.lbpressed = True
      self.curCoord = (x, y)
      self.isModified = True

    elif event == cv2.EVENT_LBUTTONUP:
      self.lbpressed = False
      # print(f"LEFT BUTTON RELEASED  Box: {self.boxCoord}")

    elif event == cv2.EVENT_MOUSEMOVE:
      self.curCoord = (x, y)


