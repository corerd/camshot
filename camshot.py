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

from camshotcfg import ConfigDataLoad
from camgrab import imageCapture
from camshotlog import logInit, logAppend
from cloud import sync_with_cloud, check_and_reset_network_connection
from shutdown import shutdown, suspend, hasPrivilegesToShutdown
from daylight import DaylightRepeatingEvent
from time import time, sleep
from datetime import datetime
from sys import argv, exit
from os import makedirs, path

# Globals
DEFAULT_CONFIG_FILE = 'camshotcfg.json'
APPLICATION_NAME = 'Camera Shot'
MAIN_SCRIPT_NAME = 'camshot.py'

# Configuration parameter defaults
WORKING_DIR = '.'
TIME_BEFORE_SHUTDOWN = 1  #minutes
TIME_ELAPSED_BETWEEN_SHOTS = 5*60  #seconds
TIME_DAYLIGHT_BEGIN = '0 8 * * 1-5'    # cron like format: 08:00 from Monday to Friday
TIME_DAYLIGHT_END   = '30 18 * * 1-5'  # cron like format: 18:30 from Monday to Friday
SUSPEND_TO_MEMORY = False
CAMERAS_LIST = []


class CamShotError(Exception):
    def __init__(self, emesg):
        self.emesg = emesg
    def __str__(self):
        return "{0}".format(self.emesg)

def configUpdate(cfgFile):
    global TIME_ELAPSED_BETWEEN_SHOTS, TIME_DAYLIGHT_BEGIN, TIME_DAYLIGHT_END
    global WORKING_DIR, SUSPEND_TO_MEMORY, CAMERAS_LIST
    cfg = ConfigDataLoad(cfgFile)
    WORKING_DIR = cfg.data['camshot-datastore']
    TIME_ELAPSED_BETWEEN_SHOTS = eval(cfg.data['camshot-schedule']['seconds-to-wait'])
    TIME_DAYLIGHT_BEGIN = cfg.data['camshot-schedule']['start-time']
    TIME_DAYLIGHT_END = cfg.data['camshot-schedule']['end-time']
    SUSPEND_TO_MEMORY = (cfg.data['camshot-schedule']['suspend'] == 'YES')
    CAMERAS_LIST = cfg.data['cameras-list']

def get_delay_between_shots():
    wakeup_datetime = DaylightRepeatingEvent(TIME_ELAPSED_BETWEEN_SHOTS, TIME_DAYLIGHT_BEGIN, TIME_DAYLIGHT_END)
    now = datetime.now()
    next_datetime = wakeup_datetime.next_occurrence(now)
    logAppend('{0}: will resume at {1}'.format(MAIN_SCRIPT_NAME, next_datetime))
    return int( (next_datetime-now).total_seconds() )

def grab(picturesBaseDir, cameraList):
    # Make the grabbed picture file path
    now = datetime.now()
    picturesDirName = '{0:s}/CAMSHOT_{1:%Y%m%d}'.format(picturesBaseDir, now)
    try:
        makedirs(picturesDirName)
        logAppend('%s: create directory %s' % (MAIN_SCRIPT_NAME, picturesDirName))
    except OSError, e:
        if not path.isdir(picturesDirName):
            # If the directory doesn't already exist, there was an error on creation
            raise CamShotError("{0}: create directory {1} [OS errno {2}]: {3}".format(MAIN_SCRIPT_NAME, picturesDirName, e.errno, e.strerror))

    # Grab a picture from cameras
    cameraIndex = 0
    for camera in cameraList:
        pictureFileFullName = '{0:s}/CS{1:%Y%m%d%H%M}_{2:02d}.jpg'.format(picturesDirName, now, cameraIndex)
        logAppend('%s: grab in file %s' % (MAIN_SCRIPT_NAME, pictureFileFullName))
        imageCaptureTries = 0
        while imageCaptureTries < 3:
            if imageCapture(camera, pictureFileFullName):
                break;
            sleep(3)
            imageCaptureTries = imageCaptureTries + 1
        if imageCaptureTries >= 3:
            logAppend('%s: grab picture error' % (MAIN_SCRIPT_NAME))
        cameraIndex = cameraIndex + 1

def grabLoop(workingDir, cameraList, suspendToMemory):
    while True:
        tBegin = time()
        check_and_reset_network_connection()
        sync_with_cloud(120)
        # configUpdate(workingDir)
        grab(workingDir, cameraList)
        isResumedFromRTC = suspend(suspendToMemory, get_delay_between_shots() - (time()-tBegin))
        if not isResumedFromRTC:
            return 1 
    return 0

def usage():
    print '%s usage:' % (APPLICATION_NAME)
    print ' %s [configuration_file]' % (MAIN_SCRIPT_NAME)

def main(argc, argv):
    global MAIN_SCRIPT_NAME
    MAIN_SCRIPT_NAME = path.basename(argv[0])

    configurationFile = DEFAULT_CONFIG_FILE
    if argc > 2:
        usage()
        return 1
    if argc == 2:
        configurationFile = argv[1]

    configUpdate(configurationFile)

    if SUSPEND_TO_MEMORY:
        if not hasPrivilegesToShutdown():
            print '%s: You need to have root privileges to run this script!' % (MAIN_SCRIPT_NAME)
            return 1

    logInit('{0}/{1}-log.txt'.format(WORKING_DIR, path.splitext(MAIN_SCRIPT_NAME)[0]))
    grabLoopExitStatus = 0
    try:
        grabLoopExitStatus = grabLoop(WORKING_DIR, CAMERAS_LIST, SUSPEND_TO_MEMORY)
    except Exception as e:
        #catch ANY exception
        logAppend('{0}: unrecovable exception {1}'.format(MAIN_SCRIPT_NAME, e))
        return 2  #severe error
    if grabLoopExitStatus == 1:
        logAppend('%s: stopped by the User' % (MAIN_SCRIPT_NAME))
    return grabLoopExitStatus

if __name__ == "__main__":
    ret = main(len(argv), argv)
    if ret is not None:
        if ret == 2 and SUSPEND_TO_MEMORY:
            logAppend('%s: system will shut down in %d minutes' % (MAIN_SCRIPT_NAME, TIME_BEFORE_SHUTDOWN))
            shutdown(TIME_BEFORE_SHUTDOWN)
        exit(ret)
