#!/usr/bin/python
#
# This module depends on dropbox.py that is the Dropbox Command Line Interface.
# A copy of this script has been downloaded from the official site:
# https://www.dropbox.com/download?dl=packages/dropbox.py
#
# You can find an overview of the Dropbox CLI below:
# http://www.dropboxwiki.com/tips-and-tricks/using-the-official-dropbox-command-line-interface-cli
#
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
#
from __future__ import with_statement

from camshotlog import logAppend
from shell import callExt
from time import sleep
from contextlib import closing
from dropbox import DropboxCommand, is_dropbox_running, start_dropbox


class CloudError(Exception):
    def __init__(self, etype, emesg):
        self.etype = etype
        self.emesg = emesg
    def __str__(self):
        return "{0}('{1}')".format(self.etype, self.emesg)

# Function Decorator
# See: http://www.artima.com/weblogs/viewpost.jsp?thread=240808
def requires_sync_daemon_running(decomethod):
    def newmethod(*n, **kw):
        if is_dropbox_running():
            return decomethod(*n, **kw)
        else:
            raise CloudError("DaemonNotRunningError", "Dropbox isn't running!")
    newmethod.func_name = decomethod.func_name
    newmethod.__doc__ = decomethod.__doc__
    return newmethod

@requires_sync_daemon_running
def syncStatus():
    """get current status of the dropboxd daemon"""
    lines = None
    try:
        with closing(DropboxCommand()) as dc:
            try:
                lines = dc.get_dropbox_status()[u'status']
            except KeyError:
                raise CloudError("DaemonUnresponsiveError", "Dropbox daemon isn't responding")
            except DropboxCommand.CommandError as e:
                raise CloudError("CommandError", u"Couldn't get status: " + str(e))
            except DropboxCommand.BadConnectionError as e:
                raise CloudError("BadConnectionError", "Dropbox isn't responding!")
            except DropboxCommand.EOFError:
                raise CloudError("DaemonStoppedError", "Dropbox daemon stopped.")
    except DropboxCommand.CouldntConnectError as e:
        raise CloudError("DaemonNotRunningError", "Dropbox isn't running!")
    return lines

def sync_with_cloud(stimeout):
    print 'Wait cloud syncing for {0} seconds...'.format(stimeout)
    SLEEP_SECONDS = 5
    daemonNotRunningErrorAlreadyGet = False 
    nsec = 0
    while nsec < stimeout:
        statusLines = None
        try:
            statusLines = syncStatus()
        except CloudError as e:
            if e.etype == 'DaemonNotRunningError' and not daemonNotRunningErrorAlreadyGet:
                daemonNotRunningErrorAlreadyGet = True
                logAppend('dropbox: start daemon')
                if not start_dropbox():
                    raise CloudError("DaemonNotInstalledError", "The Dropbox daemon is not installed!")
            else:
                raise
        if statusLines is not None:
            if len(statusLines) > 0:
                if statusLines[0] == 'Up to date':
                    return
        sleep(SLEEP_SECONDS)
        nsec = nsec + SLEEP_SECONDS
    if statusLines is not None:
        for statusLine in statusLines:
            logAppend('dropbox: {0}'.format(statusLine))
    # raise CloudError("SyncingTimeoutError", "Syncing timeout")
    logAppend('dropbox: Syncing timeout')
 
def syncWaitFake():
    SYNC_TIME = 1 #seconds
    print 'File synced in %d seconds...' % SYNC_TIME
    sleep(SYNC_TIME)

def isConnectionOn():
    retcode, output = callExt('ping -c 1 goole.com')
    if retcode == 0:
        return True
    for i in range(2):
        sleep(3)
        retcode, output = callExt('ping -c 1 goole.com')
        if retcode == 0:
            return True
    return False

def check_and_reset_network_connection():
    '''Require DNS servers setting.
    See: http://askubuntu.com/a/465759 '''
    print 'Check network connection'
    if not isConnectionOn():
        logAppend('network:reset connection')
        # Require root permissions
        # See: http://ubuntuforums.org/showthread.php?t=1829796
        retcode, output = callExt('service network-manager restart')
        if len(output) > 0:
            #print the output of the external command
            for outLine in output.splitlines():
                logAppend("{0}".format(outLine))
        if not isConnectionOn():
            # The connection is lost
            # raise CloudError("network", "ping error")
            logAppend('network:ping error')
 

def tb_check_and_reset_network_connection():
    check_and_reset_network_connection()


def tb_sync_with_cloud():
    try:
        sync_with_cloud(30)
    except CloudError as e:
        print "Couldn't sync"
        print 'Cloud Exception: {0}'.format(e)
    else:
        print 'Synced'


if __name__ == "__main__":
    tb_check_and_reset_network_connection()
