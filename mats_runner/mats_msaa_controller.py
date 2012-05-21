# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from mats_base_controller import MatsBaseController
import winutils
import winconstants
import datetime
from time import sleep
from threading import Event, Lock, Condition

from collections import defaultdict

class MatsMsaaController(MatsBaseController):
    def __init__(self, pid):
        MatsBaseController.__init__(self, pid)
        self._active = Event()
        
        self._eventQueue = []
        self._eventQueueLock = Lock() #this locks now both _eventQueue and _listeners TODO: add another lock, and do proof of correctness
        self._listeners = defaultdict(set) # event_id -> [callables]
        
    def run(self):
        print 'Controller is waiting for window (HWND) to appear'
        self.hwnd = self.wait_and_get_firefox_hwnd_from_pid()
        print 'Controller got the HWND, and it is ' + str(self.hwnd)
        
        #just some shortcuts
        self.IAccessible = winutils.loadIAccessible()
        self.AccessibleObject = winutils.getAccessibleObjectFromWindow(hwnd = self.hwnd)
        
        print 'Accessible object is: ' + str(self.AccessibleObject)
        
        #starting listener
        self.listenerThread = winutils.ListenerThread(controller = self, hwnd = self.hwnd, pid = self.pid)
        self.listenerThread.start()
        self.listenerThread.wait_for_ready()
        self._active.set()
        
        while self._active.is_set():
            self._dispatch_events()
            sleep(1) #TODO change this to condition, since there is no point of looping until new messages arrive
        
        self.listenerThread.stop()
        
    def register_event_listener(self, event_string, callable):
        with self._eventQueueLock:
            self._listeners[winconstants.eventNameToInt[event_string]].add(callable)
        
    def deregister_event_listener(self, event_string, callable):
        with self._eventQueueLock:
            self._listeners[winconstants.eventNameToInt[event_string]].remove(callable)
            
    def clear_event_queue(self):
        with self._eventQueueLock:
            self._eventQueue = []
    
    def _inject_events(self, events):
        '''
        method to be called solely by ListenerThread from winutils
        '''
        if len(events) > 0:
            with self._eventQueueLock:
                self._eventQueue.append(events)
            
    def _dispatch_events(self):
        with self._eventQueueLock:
            for pack in self._eventQueue:
                for event in pack:
                    for callable in self._listeners[event.get_id()]:
                        callable(event)
    
    def wait_for_ready(self, timeout = None):
        self._active.wait(timeout)
    
    def stop(self):
        '''
        To be called by external thread. Stops Controller and sub-threads.
        '''
        
        self._active.clear()
        self.join()
    
    def wait_and_get_firefox_hwnd_from_pid(self, timeout = 60):
        '''
        This method blocks controller thread until Firefox/Nightly window HWND is available.
        TODO : this method sucks, but I really need it in order for MATS to be
        reliable. Fix active waiting with something civilized. 
        '''
        
        starttime = datetime.datetime.now()
        while datetime.datetime.now() - starttime < datetime.timedelta(seconds=timeout):
            Nightlies = winutils.getNightliesByPID(self.pid)
            if len(Nightlies) > 0:
                break
            sleep(1)
        
        if len(Nightlies) == 0:
            raise Exception("Nightly window not found - HWND wait timeout")
        
        if len(Nightlies) > 1:
            print 'WARNING: more than one instance of Nightly found, using first one.'
            print Nightlies
        return Nightlies[0][0]

    