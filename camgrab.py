#!/usr/bin/python

# The MIT License (MIT)
# 
# Copyright (c) 2014 Corrado Ubezio
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Capturing a single image from webcam

In Linux there are the following methods:

METHOD 1: RTSP protocol
avconv -i rtsp://<user>:<pass>@<local_ip>:<port>/video.mjpg -vframes 1 -r 1 -s 640x480 image.jpg

METHOD 2: HTTP protocol
avconv -i http://<user>:<pass>@<local_ip>:<port>/video.mjpg -vframes 1 -r 1 -s 640x480 image.jpg

METHOD 3: If the camera is smart enough, it is possible to send an http request to take a snapshot
wget --tries=2 --timeout=10 http://<user>:<pass>@<local_ip>:<port>/cgi-bin/jpg/image -O snapshot.jpg

See also: Link: http://stackoverflow.com/a/11094891
"""

from cv2 import *
from os import remove, stat
from os.path import isfile
import requests

def imageCaptureFromIP(cameraUrl, username, password, imageFileName):
    # See: http://stackoverflow.com/a/13137873
    try:
        r = requests.get(cameraUrl, auth=(username, password), timeout=10, stream=True)
    except Exception:
        # TODO: better to handle exceptions as in:
        # http://docs.python-requests.org/en/latest/user/quickstart/#errors-and-exceptions
        return False
    if r.status_code != 200:
        return False
    with open(imageFileName, 'wb') as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
    if not isfile(imageFileName):
        return False
    statinfo = stat(imageFileName)
    if statinfo.st_size == 0:
        remove(imageFileName)
        return False
    return True

def imageCaptureFromUSB(cameraNumber, imageFileName):
    # initialize the camera
    cam = VideoCapture(cameraNumber)
    s, img = cam.read()
    if not s:
        # frame captured returns errors
        return False
    imwrite(imageFileName, img) #save JPG image
    return True

def imageCapture(cameraDesc, imageFileName):
    camProtAndAddr = cameraDesc['source'].split('://')
    if camProtAndAddr[0] == 'usb':
        s = imageCaptureFromUSB(eval(camProtAndAddr[1]), imageFileName)
    elif camProtAndAddr[0] == 'http':
        s = imageCaptureFromIP(cameraDesc['source'],
                        cameraDesc['optional-auth']['user-name'],
                        cameraDesc['optional-auth']['password'],
                        imageFileName)
    else:
        s = False
    return s
    

if __name__ == "__main__":
    from camshotcfg import ConfigDataLoad
    from datetime import datetime
    cfg = ConfigDataLoad('camshotcfg.json')

    # Make the grabbed picture file path
    now = datetime.now()
    picturesDirName = '{0:s}/CAMSHOT_{1:%Y%m%d}'.format(cfg.data['camshot-datastore'], now)
 
    cameraIndex = 0
    for camera in cfg.data['cameras-list']:
        print 'Get image from',  camera['source']
        pictureFileFullName = '{0:s}/CS{1:%Y%m%d%H%M}_{2:02d}.jpg'.format(picturesDirName, now, cameraIndex)
        imageCapture(camera, pictureFileFullName)
        cameraIndex = cameraIndex + 1

