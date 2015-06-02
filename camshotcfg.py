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

"""Get configuration parameters
"""

import json


class ConfigDataLoad:
    def __init__(self, loadFile):
        json_data = open(loadFile)
        self.data = json.load(json_data)
        json_data.close()


if __name__ == "__main__":
    json_file = 'camshotcfg_template.json'
    cfg = ConfigDataLoad(json_file)

    print cfg.data['camshot-datastore']
    print cfg.data['camshot-schedule']['start-time']
    print cfg.data['camshot-schedule']['end-time']
    print cfg.data['camshot-schedule']['seconds-to-wait']
    print cfg.data['camshot-schedule']['suspend']
    for camera in cfg.data['cameras-list']:
        print camera['source']
        try:
            print camera['optional-auth']['user-name']
            print camera['optional-auth']['password']
        except KeyError:
            # auth is not given
            pass
    print 'Done'
