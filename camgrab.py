#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2015 Corrado Ubezio
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


def grabImageFromIP(cameraUrl, username, password):
    '''Grabs a snapshot from the IP camera referenced by its URL.

    Returns bool, JPEG bytearray.
    '''
    from requests import get
    # See: http://stackoverflow.com/a/13137873

    try:
        r = get(cameraUrl, auth=(username, password), timeout=10, stream=True)
    except Exception:
        # TODO: better to handle exceptions as in:
        # http://docs.python-requests.org/en/latest/user/quickstart/#errors-and-exceptions
        return False, None
    if r.status_code != 200:
        return False, None
    jpgImage = b""
    for chunk in r.iter_content(1024):
        jpgImage = jpgImage + chunk
    if len(jpgImage) == 0:
        return False, None
    return True, jpgImage


def grabImageFromUSB(cameraNumber=0):
    '''Grabs a snapshot from the specified USB camera.

    Returns bool, video frame decoded as a JPEG bytearray.
    '''
    from cv2 import VideoCapture, imencode

    # initialize the camera
    cam = VideoCapture(cameraNumber)
    retVal, rawData = cam.read()
    if not retVal:
        # frame captured returns errors
        return False, None
    retVal, jpgData = imencode('.jpg', rawData)
    if not retVal:
        # image encode errors
        return False, None
    return retVal, bytearray(jpgData)


def grabImage(cameraDesc):
    '''Wraps grabImageFromIP and grabImageFromUSB
    The camera type (usb or ip) is get from the descriptor.

    Returns bool, JPEG bytearray.
    '''
    retval = False
    jpgImage = b""
    camProtAndAddr = cameraDesc['source'].split('://')
    if camProtAndAddr[0] == 'usb':
        retval, jpgImage = grabImageFromUSB(eval(camProtAndAddr[1]))
    elif camProtAndAddr[0] == 'http':
        retval, jpgImage = grabImageFromIP(cameraDesc['source'],
                        cameraDesc['optional-auth']['user-name'],
                        cameraDesc['optional-auth']['password'])
    return retval, jpgImage


def imageCapture(cameraDesc, imageFileName):
    '''Saves a snapshot from a camera to the specified file.
    The camera type (usb or ip) is get from the descriptor.

    Returns bool
    '''
    retVal, jpgImage = grabImage(cameraDesc)
    if not retVal:
        # grabImage returns errors
        return False
    try:
        with open(imageFileName, 'wb') as f:
            f.write(jpgImage)
    except IOError:
        retVal = False
    return retVal


if __name__ == "__main__":
    from camshotcfg import ConfigDataLoad
    from datetime import datetime
    from os import makedirs, path

    cfg = ConfigDataLoad('camshotcfg.json')
    ## TODO handle the exceptions

    # Make the grabbed picture file path
    now = datetime.now()
    picturesDirName = '{0:s}/CAMSHOT_{1:%Y%m%d}'.format(cfg.data['camshot-datastore'], now)
    picturesDirExist = True
    try:
        makedirs(picturesDirName)
        print 'Create directory', picturesDirName
    except OSError:
        if not path.isdir(picturesDirName):
            # If the directory doesn't already exist, there was an error on creation
            print 'Error create directory', picturesDirName
            picturesDirExist = False

    if picturesDirExist:
        cameraIndex = 0
        for camera in cfg.data['cameras-list']:
            print 'Get image from', camera['source']
            pictureFileFullName = '{0:s}/CS{1:%Y%m%d%H%M}_{2:02d}.jpg'.format(picturesDirName, now, cameraIndex)
            if imageCapture(camera, pictureFileFullName) is False:
                print '---> Fail'
            cameraIndex = cameraIndex + 1
