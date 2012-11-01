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
        print 'searching', moduleFullname, 'in', path
        moduleFile = None
        try:
            if '.' in moduleFullname:
                package = moduleFullname.split('.')[0]
                (moduleFile,
                 moduleFileName,
                 _) = imp.find_module(moduleFullname, path)
                imp.load_module(package, path)


            # This function does not handle hierarchical module names
            # (names containing dots).
            (moduleFile,
             moduleFileName,
             _) = imp.find_module(moduleFullname, path)
            print 'found', moduleFileName
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
