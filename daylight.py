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

from croniter import croniter
from datetime import datetime, timedelta

class DaylightRepeatingEvent:
    '''Defines a time period repeating over a day.'''
    
    def __init__(self, time_period, time_daylight_begin, time_daylight_end):
        '''Initializes time period and day length.
        
        :param int time_period: Time delay in seconds
        :param str time_daylight_begin: cron like format daylight begin time
        :param str time_daylight_end: cron like format daylight end time
        '''
        self.time_period = time_period
        self.time_daylight_begin = time_daylight_begin
        self.time_daylight_end = time_daylight_end

    def next_occurrence(self, start_datetime):
        '''Gets the next date-time occurrence starting from start_datetime
        according to the crontab style rules.

        :param start_datetime: Current date-time
        :type start_datetime: datetime.datetime
        :return: The next date-time occurrence
        :rtype: datetime.datetime
        '''
        today = start_datetime.replace(hour=0, minute=0)
        iter = croniter(self.time_daylight_end, today)
        if start_datetime < iter.get_next(datetime):
            return start_datetime + timedelta(seconds=self.time_period)
        else:
            nextday = today + timedelta(days=1)
            iter = croniter(self.time_daylight_begin, nextday)
            return iter.get_next(datetime)


def ut_rtcSetWakeup():
    # timeIntervalSleep: 10*60 seconds = 10 minutes
    # timeDaylightBegin: 08:00 from Monday to Friday
    # timeDaylightEnd:   08:30 from Monday to Friday
    wakeup_datetime = DaylightRepeatingEvent(10*60, '0 8 * * 1-5', '30 8 * * 1-5')
    
    now = datetime(2014, 6, 2, 8, 0) # Monday, 6 June 2014 at 08:00
    end_datetime = now
    for cnt in range(4):
        end_datetime = end_datetime + timedelta(days=7) # next Monday
        while now != end_datetime:
            before = now
            now = wakeup_datetime.next_occurrence(now)
            print 'wakeup time: {0} - delta: {1} seconds'.format( now, int((now-before).total_seconds()) )
        print

    
if __name__ == "__main__":
    ut_rtcSetWakeup()
