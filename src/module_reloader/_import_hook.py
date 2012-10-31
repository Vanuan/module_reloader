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
        moduleFile = None
        try:
            (moduleFile,
             moduleFileName,
             moduleDescription) = imp.find_module(moduleFullname, path)
            moduleModifiedTimeStamp = time.ctime(os.path.getmtime(moduleFileName))
            global_modules_timestamps[moduleFullname] = (moduleFileName,
                                                         moduleModifiedTimeStamp)
        except (ImportError):
            pass
        finally:
            if moduleFile != None:
                moduleFile.close()
        return None

    def isInstanceOfFinder(self):
        return True


def setupHook():
        sys.meta_path.append(Finder())


setupHook() # make sure to call this only once
