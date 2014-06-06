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
from time import sleep
from subprocess32 import call
from os import geteuid
from sys import stderr


def hasPrivilegesToShutdown():
    if geteuid() != 0:
        return False
    return True

def suspend(waitSeconds, onResume=None):
    if waitSeconds <= 0:
        return
    print 'Put the system in suspend mode and awakened between %d seconds' % waitSeconds
    suspendCmd = 'rtcwake -m mem -s %d' % (waitSeconds)
    suspendFail = True
    try:
        retcode = call(suspendCmd, shell=True)
        if retcode < 0:
            print >>stderr, "suspend: rtcwake was terminated by signal", -retcode
        elif retcode > 0:
            print >>stderr, "suspend: rtcwake returned error code", retcode
        else:
            suspendFail = False
    except OSError as e:
        print >>stderr, "suspend: rtcwake execution failed:", e
    if suspendFail:
        print 'System suspend failed: sleeping...'
        sleep(waitSeconds)

if __name__ == "__main__":
    print 'suspend test'
    if hasPrivilegesToShutdown():
        suspend(10)
        print 'awakened from suspend'
    else:
        print 'You need to have root privileges to run this script!'

