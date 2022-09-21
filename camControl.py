import requests 
import time
import json
from termcolor import colored

# ptzURL = "http://192.168.0.195:7071/api/ptz/move"         # MWIR
# videoURL = "http://192.168.0.195:7071/api/video/put"      # MWIR
# videoGetURL = "http://192.168.0.195:7071/api/video/get"   # MWIR
ptzURL = "http://192.168.0.180:7071/api/ptz/move" 
videoURL = "http://192.168.0.180:7071/api/video/put"
videoGetURL = "http://192.168.0.180:7071/api/video/get"

headers = {'Content-Type': 'Application/json; charset=utf-8'} 

update_interval = 1.8

def printDict(blob):
  for _key in list(blob.keys()):
    print(f"{_key}: {blob[_key]}")

def getCamInfo():
  response = requests.get(
    videoGetURL,
    headers=headers,
  )

  return json.loads(response.text)

def readFocusVal():
  # URL = "http://192.168.0.195:7071/api/video/focusPos"  # MWIR
  URL = "http://192.168.0.180:7071/api/video/focusPos"
  response = requests.get(
    URL,
    headers=headers
  )

  result = json.loads(response.text) #["EOSFocusCurPos"]

  # print(f"[readFocusVal] {result}")

  return 0 if result == {} else result["EOSFocusCurPos"]

  # return json.loads(response.text)["EOSFocusCurPos"]

def readZoomVal():
  # URL = "http://192.168.0.195:7071/api/video/viewPos"   # MWIR
  URL = "http://192.168.0.180:7071/api/video/viewPos"
  response = requests.get(
    URL,
    headers=headers
  )

  result = json.loads(response.text)

  return 0 if result == {} else result["EOSViewCurPos"]

def getGrayMode():
  status = getCamInfo()
  return status['EOSHotMode']

def sendPost(url, body):
  response = requests.post(
                            url,
                            headers=headers,
                            data=json.dumps(body)
                          )
  print(colored(f"POST Action Response {response.status_code}", "yellow"))

def selectFilter(cmd):
  url = videoURL 
  body = {"EOSCutFilter": cmd}
  print(f"[Action] select Filter {cmd}")
  sendPost(url, body)

def grayInversion():
  current_grayMode = getGrayMode()
  url = videoURL
  body = {"EOSHotMode": 0 if current_grayMode==1 else 1}
  print(f"[Action] Set GrayInversion Mode")
  sendPost(url, body)


def setVideoManualMode():
  url = videoURL
  body = {"EOSVideoMode":2}
  print(f"[Action] Set Video ManualMode")
  sendPost(url, body)


def setVideoMode(cmd):
  print(f"[setVideoMode] recv cmd: {cmd}")
  url = videoURL
  if cmd.strip().lower()=='auto':
    param = 0
  elif cmd.strip().lower()=='manual':
    param = 2
  else:
    print(f"[setVideoMode] Unknown cmd: {cmd}")
    return

  body = {"EOSVideoMode": param}

  print(f"[Action] Set Video Mode : {cmd}")
  sendPost(url, body)
  

def cFocus(cmd):

  url = videoURL
  if cmd.strip().lower()=='near':
    param = 1
  elif cmd.strip().lower()=='far':
    param = 2
  else:
    print(f"[cFocus] Unknown cmd: {cmd}")
    return

  body = {'EOSFocusMove': param}

  print(f"[Action] Continuous Focus Position Move : {cmd}")
  sendPost(url, body)

def oneshotAutoFocus():
  time.sleep(.1)
  url = videoURL
  body = {"EOSAutoFocus":1}


  print(f"[Action] Set FocusOneshot Auto Focus")
  sendPost(url, body)


def focusRequest(cmd):
  url = videoURL

  cfocusVal = readFocusVal()
  step=1000

  if cmd=='far':
     focusVal = min(cfocusVal+step, 10000)
  elif cmd=='near':
    focusVal = max(cfocusVal-step, 20)
  else:
    print(f'UnKnown Focus Command: {cmd}')
    return
  
  body = {"EOSFocusAbsPos": focusVal}

  print(f"[Action] Focus Position Move : {cfocusVal} ---> {focusVal}")
  sendPost(url, body)

  time.sleep(update_interval)
  print(colored(f"[PostAction] Current FocusVal: {readFocusVal()})", "yellow"))


def zoomRequest(cmd):
  url = videoURL

  czoomVal = readZoomVal()
  step=500

  if cmd=='zoomin':
     zoomVal = min(czoomVal+step, 10000)
  elif cmd=='zoomout':
    zoomVal = max(czoomVal-step, 20)
  
  body = {"EOSViewAbsPos": zoomVal}
  print(f"[Action] Zoom Position Move : {czoomVal} ---> {zoomVal}")
  sendPost(url, body)
  
  time.sleep(update_interval)
  print(colored(f"[PostAction] Current ZoomVal: {readZoomVal()})", "yellow"))


def zoomAbsMove(val):
  url = videoURL

  czoomVal = readZoomVal()
  
  body = {"EOSViewAbsPos": val}
  print(f"[Action] Zoom Position Move : {czoomVal} ---> {val}")
  sendPost(url, body)
  
  time.sleep(update_interval)
  print(colored(f"[PostAction] Current ZoomVal: {readZoomVal()})", "yellow"))

def focusAbsMove(val):
  url = videoURL

  cfocusVal = readFocusVal()
  
  body = {"EOSFocusAbsPos": val}
  print(f"[Action] Focus Position Move : {cfocusVal} ---> {val}")
  sendPost(url, body)
  
  time.sleep(update_interval)
  print(colored(f"[PostAction] Current ZoomVal: {readFocusVal()})", "yellow"))


def contZoomRequest(cmd):
  url = videoURL

  if cmd=='zoomin':
    req = 1
  elif cmd=='zoomout':
    req = 2
  elif cmd=='zoomstop':
    req = 0
  
  body = {"EOSZoom": req}

  try: 
    print(f"[Action] Continuous Zoom Position Move : {cmd}")
    sendPost(url, body)
  except Exception as ex: 
    print(ex) 

def ptzRequest(cmd): 
  url = ptzURL 
  if cmd=='stop' or cmd=='ptstop':
    body = {'Command':'ptstop'} 
  elif cmd=='zoomstop':
    body = {'Command':'zoomstop'} 
  else:
    body = {'Command':f'{cmd}','Speed':0.2}
  
  try: 
    print(f"[Action] PTZ Request : {cmd}")
    sendPost(url, body)
  except Exception as ex: 
    print(ex) 

def setCutFilter(val):
  if val > 3 or val < 0:
    print('Invalid Cutfilter value...')
    return

  url = videoURL
  body = {'EOSCutFilter': val}
  try: 
    print(f"[Action] setCutFilter-{val}")
    sendPost(url, body)
  except Exception as ex: 
    print(ex) 

def camCalibration(): # video correction : external shutter
  url = videoURL
  body = {"EOSVideoCorrect": 1} # 0: Defocus, 1: extenal shutter

  print(f"[Action] Cam Calibration (external shutter) ")
  sendPost(url, body)

### Old Interfaces
def videoRequest(cmds): 
  url = videoURL 
  
  try: 
    vidCommandDict = {
          'VideoCorrect':      -1,  
          'VideoMode':          1,
          'BrightnessVariance': 0,
          'BrightnessVal':      0,
          'ContrastVariance':   0,
          'ContrastVal':        0,
          'DigitalZoom':        0,
          'HotMode':            2,
          'IRColor':            9,
          'Sharpness':         -1,
          'ViewMode':          -1,
          'AFType':            -1,
          'AFRegion':           0,
          'Defocus':            0,
          'Pos':                0,
          'FocusMove':         -1,
          'EOIRCutFilter':     -1
        }

    print(colored(f"[VideoCtrl] POST Action", "yellow"))
    for _key, _val in cmds.items():
      print(colored(f"\t({_key}: {_val})", "yellow"))
      if _key not in list(vidCommandDict.keys()):
        print(colored("Requested Video Control Field Not Allowed", "red"))
        return
      vidCommandDict[_key] = _val
      # printDict(vidCommandDict)


    vidCommandDict_json = json.dumps(vidCommandDict).encode('utf-8')
    response = requests.post(
                              url, 
                              headers=headers, 
                              data=vidCommandDict_json
                            )
    print(colored(f"[VideoCtrl] POST Action Response {response.status_code}", "yellow"))

  except Exception as ex: 
    print(ex) 


if __name__ == '__main__':
  videoRequest("Defocus")