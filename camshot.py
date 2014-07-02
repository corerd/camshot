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
from camshotlog import logInit, logAppend
from cloud import syncWait
from shutdown import shutdown, suspend, hasPrivilegesToShutdown
from daylight import DaylightRepeatingEvent
from ConfigParser import RawConfigParser
from time import time, sleep
from datetime import datetime
from sys import argv, exit
from os import makedirs, path

# Globals
APPLICATION_NAME = 'Camera Shot'
MAIN_SCRIPT_NAME = 'camshot.py'
MAIN_SCRIPT_DIR = '.'

# Configuration parameter defaults
TIME_BEFORE_SHUTDOWN = 1  #minutes
TIME_ELAPSED_BETWEEN_SHOTS = 15*60  #seconds
TIME_DAYLIGHT_BEGIN = '0 8 * * 1-5'    # cron like format: 08:00 from Monday to Friday
TIME_DAYLIGHT_END   = '30 18 * * 1-5'  # cron like format: 18:30 from Monday to Friday


class CamShotError(Exception):
    def __init__(self, emesg):
        self.emesg = emesg
    def __str__(self):
        return "{0}".format(self.emesg)

def configUpdate():
    global TIME_ELAPSED_BETWEEN_SHOTS, TIME_DAYLIGHT_BEGIN, TIME_DAYLIGHT_END
    cfgFileName = '{0}/{1}.cfg'.format(MAIN_SCRIPT_DIR, path.splitext(MAIN_SCRIPT_NAME)[0])
    config = RawConfigParser()
    try:
        config.read(cfgFileName)
        sleepTimeValue = eval( config.get("rtc-setup", "sleep-time") )
        daylightBegin = config.get("rtc-setup", "daylight-begin")
        daylightEnd = config.get("rtc-setup", "daylight-end")
    except:
        # config file errors
        return
    TIME_ELAPSED_BETWEEN_SHOTS = sleepTimeValue
    TIME_DAYLIGHT_BEGIN = daylightBegin
    TIME_DAYLIGHT_END = daylightEnd

def get_delay_between_shots():
    wakeup_datetime = DaylightRepeatingEvent(TIME_ELAPSED_BETWEEN_SHOTS, TIME_DAYLIGHT_BEGIN, TIME_DAYLIGHT_END)
    now = datetime.now()
    next_datetime = wakeup_datetime.next_occurrence(now)
    return int( (next_datetime-now).total_seconds() )

def grab(picturesBaseDir):
    cameraIndex = 0

    # Make the grabbed picture file path
    now = datetime.now()
    picturesDirName = '{0:s}/CAMSHOT_{1:%Y%m%d}'.format(picturesBaseDir, now)
    pictureFileFullName = '{0:s}/CS{1:%Y%m%d%H%M}_{2:02d}'.format(picturesDirName, now, cameraIndex)
    try:
        makedirs(picturesDirName)
        logAppend('%s: create directory %s' % (MAIN_SCRIPT_NAME, picturesDirName))
    except OSError, e:
        if not path.isdir(picturesDirName):
            # If the directory doesn't already exist, there was an error on creation
            raise CamShotError("{0}: create directory {1} [OS errno {2}]: {3}".format(MAIN_SCRIPT_NAME, picturesDirName, e.errno, e.strerror))
    logAppend('%s: grab in file %s' % (MAIN_SCRIPT_NAME, pictureFileFullName))

    # Grab a picture from the first camera
    imageCaptureTries = 0
    while imageCaptureTries < 3:
        if imageCapture(cameraIndex, pictureFileFullName):
            break;
        sleep(3)
        imageCaptureTries = imageCaptureTries + 1
    if imageCaptureTries >= 3:
        raise CamShotError('%s: grab picture error' % (MAIN_SCRIPT_NAME))

def grabLoop(workingDir):
    while True:
        tBegin = time()
        syncWait(120)
        configUpdate()
        grab(workingDir)
        syncWait(120)
        isResumedFromRTC = suspend(get_delay_between_shots() - (time()-tBegin))
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
    logInit('{0}/{1}-log.txt'.format(workingDir, path.splitext(MAIN_SCRIPT_NAME)[0]))
    try:
        if grabLoop(workingDir) == 1:
            logAppend('%s: stopped by the User' % (MAIN_SCRIPT_NAME))
    except Exception as e:
        #catch ANY exception
        logAppend('{0}: unrecovable exception {1}'.format(MAIN_SCRIPT_NAME, e))
        return 2  #severe error
    return 0

if __name__ == "__main__":
    ret = main(len(argv), argv)
    if ret is not None:
        if ret == 2:
            logAppend('%s: system will shut down in %d minutes' % (MAIN_SCRIPT_NAME, TIME_BEFORE_SHUTDOWN))
            shutdown(TIME_BEFORE_SHUTDOWN)
        exit(ret)
