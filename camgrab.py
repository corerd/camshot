#!/usr/bin/python
#
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

# See: Capturing a single image from my webcam in Java or Python
# Link: http://stackoverflow.com/a/11094891
#
from cv2 import *

def imageCapture(cameraIndex, imageName):
    # initialize the camera
    cam = VideoCapture(cameraIndex)
    s, img = cam.read()
    if not s:
        # frame captured returns errors
        return False
    imwrite(imageName+'.jpg',img) #save JPG image
    return True

if __name__ == "__main__":
    picture = "camshot"
    if not imageCapture(0, picture):
        print 'Camera grab picture error'
    else:
        print 'Picture save in', picture
