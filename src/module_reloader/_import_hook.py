'''
Do never reload this module.
Import only once.

@author: Vanuan
'''

import imp, os, time, sys

global_modules_timestamps = {}

class Finder(object):
    def __init__(self):
        pass
    
    def find_module(self, moduleFullname, path=None):
        try:
            moduleFileName = imp.find_module(moduleFullname, path)[1]
            moduleModifiedTimeStamp = time.ctime(os.path.getmtime(moduleFileName))
            global_modules_timestamps[moduleFullname] = (moduleFileName,
                                                         moduleModifiedTimeStamp)
        except ImportError:
            return None
        return None
    
    def isInstanceOfFinder(self):
        return True

    def __eq__(self, other):
        print other
        print "instance"
        return other.isInstanceOfFinder()
    
def setupHook():
        sys.meta_path.append(Finder())

setupHook() # make sure to call this only once
