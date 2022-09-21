
# Original Project on Github: https://github.com/sahilparekh/GStreamer-Python

'''
This Simple program Demonstrates how to use G-Streamer and capture RTSP Frames in Opencv using Python
- Sahil Parekh

* The original program is little bit modified , e.g. input video resolution etc, to share memory between main module and gstreamer module.
* Gstreamer (ver > 1.0) should be installed.  (https://launchpad.net/distros/ubuntu/+source/gstreamer1.0)
    For Ubuntu, you may refer to this for installation help: http://lifestyletransfer.com/how-to-install-gstreamer-on-ubuntu/
- Wun-Cheol Jeong
'''

import os
import time, datetime
import cv2
import sys
from termcolor import colored

import screeninfo
from img_util import VideoWriter 

from camControl import (
                          ptzRequest, 
                          getCamInfo, 
                          printDict, 
                          zoomRequest, 
                          focusRequest,
                          oneshotAutoFocus, 
                          setVideoMode,
                          cFocus,
                          grayInversion,
                          contZoomRequest,
                          setVideoManualMode,
                          readZoomVal,
                          readFocusVal,
                          zoomAbsMove,
                          focusAbsMove,
                          setCutFilter,
                          camCalibration
                        )


from threading import Event 


mainMonitor = screeninfo.get_monitors()[0]

screen_width = mainMonitor.width
screen_height = mainMonitor.height

# cam=cv2.VideoCapture("rtsp://192.168.0.197:25252/eost-ircam") # MWIR
cam = cv2.VideoCapture("rtsp://192.168.0.100:25252/eost-ircam")
fps = cam.get(cv2.CAP_PROP_FPS)
# print(f'FPS Info: {cam.get(cv2.CAP_PROP_FPS)}')

aspectRatioSet = False

class CamStatus:
  def __init__(self):
    self.zoom = 470
    self.focus = 4070
    self.cutFilter = 0
    self.inversion = False

def ptz_ctrl_request(action):
  print(f"PTZ Request: {action}")
  ptzRequest(action)


def dispHelp():
  msg = '''
  ** pt **
  i: up
  m: down
  j: left
  k: right
  <spacebar>: stop pt
  
  ** zoom and focus **
  z: set zoom (view) position
  f: set focus position
  a: oneshot auto focus
  u: update track bar values


  ** IR filter selection **
  0: no filter
  1: filter 1
  2: filter 2

  s: set manual mode
  h: help
  v: gray inversion
  
  g: get current cam info
  e: calibrate cam (external shutter)

  r: toggle video record

  Zoom-Focus Table:::
  'X1':   {'z':20,		'f': 3505},
  'X2':   {'z':1540,	'f': 4489},
  'X4':   {'z':3755,	'f': 3755},
  'X8':   {'z':7310,	'f': 6184},
  'X16':  {'z':9829,  'f': 9801}
  '''

  print(msg)
  
def requestProcess(req, camStatus=None):
  if req == 'j':
    command = 'left'
  elif req == 'k':
    command = 'right'
  elif req == 'i':
    command = 'up'
  elif req == 'm':
    command = 'down'
  elif req == ' ':
    command = 'ptstop'

  elif req == 'a':
    oneshotAutoFocus()
    return
  elif req == 's':
    print('Set Manual Mode')
    setVideoMode('manual')
    return

  elif req == 'h':
    dispHelp()
    return
  
  elif req=='v':
    camStatus.inversion = True if not camStatus.inversion else False
    grayInversion()
    return

  elif req == 'z':
    val = camStatus.zoom
    print(f'Zoom Request: {val}')
    zoomAbsMove(val)
    return

  elif req == 'f':
    val = camStatus.focus
    print(f'Focus Request: {val}')
    focusAbsMove(val)
    return

  elif req == 'g':                # get current cam info
    print('Get Current Cam Info')
    printDict(getCamInfo())
    return

  elif req == 'e':
    camCalibration()
    return 

  elif req == '0':
    camStatus.cutFilter = 0
    setCutFilter(int(req))
    return
  elif req == '1':
    camStatus.cutFilter = 1
    setCutFilter(int(req))
    return
  elif req == '2':
    camStatus.cutFilter = 2
    setCutFilter(int(req))
    return


  else:
    print(f'Invalid command: {req}')
    return
  
  ptz_ctrl_request(command)



'''
Main class
'''
class mainStreamClass:

  def __init__(self, rtsp_link):   
    self.camlink = rtsp_link #RTSP cam link
    # self.framerate = 20 #6
    self.recEvent = Event()
    self.videoWriter = VideoWriter(self.recEvent, fps=fps)
    self.canvas_name = "MWIR Dataset"
    self.camStatus = CamStatus()
    self.aspectRatioSet = False
  
  def onZoomChange(self, pos):
    self.camStatus.zoom = pos
    print(f"[zoom] pos: {self.camStatus.zoom}")

  def onFocusChange(self, pos):
    self.camStatus.focus = pos
    print(f"[focus] pos: {self.camStatus.focus}")

  def updateZfVal(self):
    self.camStatus.zoom = readZoomVal()
    self.camStatus.focus = readFocusVal()
    cv2.setTrackbarPos("zoom", self.canvas_name, self.camStatus.zoom)
    cv2.setTrackbarPos("focus", self.canvas_name, self.camStatus.focus)

  def startMain(self):
    
    cv2.namedWindow(self.canvas_name)
    
    self.camStatus.zoom = readZoomVal()
    self.camStatus.focus = readFocusVal()
    cv2.createTrackbar("zoom", self.canvas_name, self.camStatus.zoom, 65535, self.onZoomChange)
    cv2.createTrackbar("focus", self.canvas_name, self.camStatus.focus, 65535, self.onFocusChange)

    while True:
      _, img = cam.read()

      if not self.aspectRatioSet:
        self.aspectRatioSet = True
        cam_width = img.shape[1]
        cam_height = img.shape[0]
        widthRatio = screen_width / cam_width
        heightRatio = screen_height / cam_height
        resize_axis = 'y' if heightRatio < widthRatio else 'x'
        scale = widthRatio if resize_axis == 'x' else heightRatio
        print(f"Image Resolution: {int(scale* img.shape[1])}x{int(scale*img.shape[0])}")

      if self.videoWriter.isRecording:
        self.videoWriter.write(img)
      
      if self.videoWriter.isRecording:
        self.videoWriter.write(img)

      if img is None: 
        print(colored("No Img Frame Received", "yellow"))
        continue 
      img = cv2.resize(img, (int(scale* img.shape[1]*.85), int(scale*img.shape[0]*.85)))

      if self.videoWriter.isRecording:
        cv2.putText(img, "REC", (int(.5*img.shape[1])-30, 80), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)

      if self.camStatus.cutFilter != 0:
        cv2.putText(img, f"F{self.camStatus.cutFilter}", (15, 80), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)
      
      if self.camStatus.inversion:
        cv2.putText(img, f"Inversion", (180, 80), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)
              

      cv2.imshow(self.canvas_name, img)

      keyIn = cv2.waitKey(10)
      if keyIn == ord('q'):
        if self.videoWriter.isRecording:
          self.videoWriter.release()
        break
      elif keyIn == ord('r'):
        if self.videoWriter.isRecording:
          self.videoWriter.release()
          self.recEvent.clear()
        else:
          self.videoWriter.rec()
          self.recEvent.set()
      elif keyIn == ord('u'):
        self.updateZfVal()
      elif keyIn != -1:
        print(f'KEyIn: {keyIn}')
        requestProcess(chr(keyIn), self.camStatus)
        self.updateZfVal()


    print('terminate...')
    cv2.destroyAllWindows()
    return()


if __name__ == "__main__":
  # rtsp_link = "rtsp://192.168.0.197:25252/eost-ircam"
  rtsp_link = "rtsp://192.168.0.100:25252/eost-ircam"
  mc = mainStreamClass(rtsp_link)
  mc.startMain()
