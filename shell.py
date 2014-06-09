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
from subprocess32 import check_output, CalledProcessError, STDOUT

class ShellError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "{0}".format(self.value)

def callExt(cmd):
    retcode = 0
    cmdOutput = ''
    try:
        cmdOutput = check_output(cmd, stderr=STDOUT, shell=True)
    except OSError as e:
        raise ShellError(e)
    except CalledProcessError as e:
        # Exception raised when a process returns a non-zero exit status
        retcode = e.returncode
        cmdOutput = e.output
    return retcode, cmdOutput


if __name__ == "__main__":
    print 'callExt with normal process termination'
    exitStatus, output = callExt("ls")
    print exitStatus
    print output
    print 'callExt when a process returns a non-zero exit status'
    exitStatus, output = callExt("ls non_existent_file")
    print exitStatus
    print output
    print 'callExt with non existent command'
    exitStatus, output = callExt('non_existent_command')
    print exitStatus
    print output
    print 'callExt reporting ShellError'
    exitStatus, output = callExt('cd some_non_existing_dir')
    print exitStatus
    print output

