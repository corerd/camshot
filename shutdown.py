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

# How to Make Your Linux PC Wake From Sleep Automatically
# Link http://www.howtogeek.com/121241/how-to-make-your-linux-pc-wake-from-sleep-automatically/
#
from time import time 
from os import geteuid
from sys import stderr
from camshotlog import logAppend
from shell import callExt, ShellError


class SuspendError(Exception):
    def __init__(self, etype, emesg):
        self.etype = etype
        self.emesg = emesg
    def __str__(self):
        return "{0}('{1}')".format(self.etype, self.emesg)

def hasPrivilegesToShutdown():
    if geteuid() != 0:
        return False
    return True

def screenPowerSave(on):
    if on:
        callExt('vbetool dpms off')
    else:
        callExt('vbetool dpms on')

def syncDiskWithMemory():
    print 'Sync Disk With Memory'
    try:
        retcode, output = callExt('sync')
        if len(output) > 0:
            #print the output of the external command
            for outLine in output.splitlines():
                logAppend("sync: {0}".format(outLine))
        if retcode < 0:
            raise SuspendError("sync", "sync was terminated with failure code {0}".format(-retcode))
    except ShellError as e:
        raise SuspendError("OSError", "sync execution failed: {0}".format(e))
 

def suspend(waitSeconds, onResume=None):
    if waitSeconds <= 0:
        return
    suspendCmd = 'rtcwake -m mem -s %d' % (waitSeconds)
    if onResume is not None:
        suspendCmd = '{0} && {1}'.format(suspendCmd, onResume)
    suspendStartTime = time()
    syncDiskWithMemory()
    try:
        retcode, output = callExt(suspendCmd)
        if len(output) > 0:
            #print the output of the external command
            for outLine in output.splitlines():
                logAppend("callExt: {0}".format(outLine))
        if retcode < 0:
            raise SuspendError("rtc", "suspend: rtcwake was terminated by signal {0}".format(-retcode))
        if retcode > 0:
            raise SuspendError("rtc", "suspend: rtcwake returned error code {0}".format(retcode))
    except ShellError as e:
        raise SuspendError("OSError", "suspend: rtcwake execution failed: {0}".format(e))
    # Resume from suspend
    if time() - suspendStartTime < waitSeconds:
        # Resume from suspend was not caused by the rtc, such as power button or keyboard
        return False 
    return True

def shutdown():
    retcode, output = callExt('shutdown -h now')
    if len(output) > 0:
        #print the output of the external command
        for outLine in output.splitlines():
            logAppend("callExt: {0}".format(outLine))
 
if __name__ == "__main__":
    print 'suspend test'
    if hasPrivilegesToShutdown():
        try:
            #resumeFromRTC = suspend(10, 'vbetool dpms off')
            resumeFromRTC = suspend(10)
        except SuspendError as e:
            print '{0}'.format(e)
        else:
            if resumeFromRTC:
                print 'awakened from suspend'
            else:
                print 'Resume from suspend was not caused by the rtc'
    else:
        print 'You need to have root privileges to run this script!'

