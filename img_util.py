import os, cv2, datetime
import numpy as np 
from termcolor import colored

font = cv2.FONT_HERSHEY_SIMPLEX 

class COLOR:
  """
  COLOR:
    ;COLOR definition class

      COLOR.blue, 
      COLOR.green, 
      COLOR.red, 
      COLOR.white, 
      COLOR.cyan,
      COLOR.magenta,
      COLOR.yellow
  """
  blue = (255, 0, 0)
  green = (0, 255, 0)
  red = (0, 0, 255)
  white = (255, 255, 255)
  cyan = (255, 255, 0)
  magenta = (255, 0, 255)
  yellow = (0, 255, 255)
  black = (0, 0, 0)



def blankImage(imageSize, color):
  # if len(imageSize) != len(color):
  #   print(colored(f"Dimension of imageSize doesn't match to that of color!", "red"))
  return np.full(imageSize, color, dtype=np.uint8)


class VideoWriter:
  def __init__(self, recEvent, fps=30):
    self.isRecording = False
    self.fps = fps
    self.recEvent = recEvent
    self.frameSize = (640, 480)
  
  def setFileName(self, fileName):
    self.fileName = fileName
  
  def createVideoWriter(self, fileName):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    self.recorder = cv2.VideoWriter(
                                  fileName, 
                                  fourcc, 
                                  self.fps, 
                                  self.frameSize 
                                )
    print(f'Video Writer Object Created')
    self.isRecording = True

  def rec(self):
    if self.recEvent.is_set():
      self.recEvent.clear()
      self.release()
    else:
      self.recEvent.set()
      self.recEvent.set()
      now = datetime.datetime.now()
      fileName = now.strftime("./video/vid%m%d_%H%M%S.mp4")
      if not os.path.exists("./video"):
        os.makedirs("./video")
      print(f"video save to: {fileName}")
      self.createVideoWriter(fileName)

  def write(self, frame):
    self.recorder.write(frame)
  
  def release(self):
    self.isRecording = False
    self.recorder.release()
  
