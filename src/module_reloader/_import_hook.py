'''
Do never reload this module.
Import only once.

@author: Vanuan
'''

import imp
import os
import time
import sys

global_modules_timestamps = {}


class Finder(object):

    def find_module(self, moduleFullname, path=None):
        #print 'searching', moduleFullname, 'in', path
        moduleFile = None
        try:
            # This function does not handle hierarchical module names
            # (names containing dots).
            if '.' in moduleFullname:
                print ('warning: hierarchical module names are not supported',
                       moduleFullname)

            (moduleFile,
             moduleFileName,
             _) = imp.find_module(moduleFullname, path)
            modifiedTimeStamp = time.ctime(os.path.getmtime(moduleFileName))
            if moduleFullname not in sys.builtin_module_names:
                global_modules_timestamps[moduleFullname] = (moduleFileName,
                                                             modifiedTimeStamp)
        except (ImportError, OSError):
            print 'not found', moduleFullname
            pass
        finally:
            if moduleFile != None:
                moduleFile.close()
        return None


def setupHook():
    sys.meta_path.append(Finder())


setupHook()  # make sure to call this only once
