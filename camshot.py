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

from camgrab import imageCapture
from cloud import syncWait
from shutdown import suspend, hasPrivilegesToShutdown
from time import time
from datetime import datetime
from sys import argv, exit
from os import makedirs, path

APPLICATION_NAME = 'Camera Shot'
MAIN_SCRIPT_NAME = None
MAIN_SCRIPT_DIR = None

ELAPSED_TIME_BETWEEN_SHOTS = 15*60  #seconds

def grab(picturesBaseDir):
    cameraIndex = 0

    # Make the grabbed picture file path
    now = datetime.now()
    picturesDirName = '{0:s}/CAMSHOT_{1:%Y%m%d}'.format(picturesBaseDir, now)
    pictureFileFullName = '{0:s}/CS{1:%Y%m%d%H%M}_{2:02d}'.format(picturesDirName, now, cameraIndex)
    try:
        makedirs(picturesDirName)
        print '%s: create directory %s' % (MAIN_SCRIPT_NAME, picturesDirName)
    except OSError, e:
        if not path.isdir(picturesDirName):
            # If the directory doesn't already exist, there was an error on creation
            print "{0}: create directory {1} [OS errno {2}]: {3}".format(MAIN_SCRIPT_NAME, picturesDirName, e.errno, e.strerror)
            return
    print '%s: grab in file %s' % (MAIN_SCRIPT_NAME, pictureFileFullName)

    # Grab a picture from the first camera
    if imageCapture(cameraIndex, pictureFileFullName):
        print '%s: grab picture error' % (MAIN_SCRIPT_NAME)

def grabLoop(workingDir):
    while True:
        tBegin = time()
        syncWait(120)
        grab(workingDir)
        syncWait(120)
        isResumedFromRTC = suspend(ELAPSED_TIME_BETWEEN_SHOTS - (time() - tBegin))
        if not isResumedFromRTC:
            return 1 
    return 0

def usage():
    print '%s usage:' % (APPLICATION_NAME)
    print ' %s [working_directory]' % (MAIN_SCRIPT_NAME)

def main(argc, argv):
    global MAIN_SCRIPT_NAME, MAIN_SCRIPT_DIR
    MAIN_SCRIPT_NAME = path.basename(argv[0])
    MAIN_SCRIPT_DIR = path.dirname(path.realpath(argv[0]))
    if argc > 2:
        usage()
        return 1
    workingDir = MAIN_SCRIPT_DIR
    if argc == 2:
        workingDir = argv[1]
    if not hasPrivilegesToShutdown():
        print '%s: You need to have root privileges to run this script!' % (MAIN_SCRIPT_NAME)
        return 1
    if grabLoop(workingDir) == 1:
        print 'Stopped by the User'
    return 0

if __name__ == "__main__":
    ret = main(len(argv), argv)
    if ret is not None:
        exit(ret)
