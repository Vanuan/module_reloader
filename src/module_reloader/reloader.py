'''
The purpose of this module is to reload modules that were modified
after the last reload.

It uses import hook to determine a module file timestamp during import/reload

reloadModifiedModules function determines current timestamp
and reloads a module it is was changed

== Usage:

from module_reloader import reloader
reloader.reloadModifiedModules()

@author: Vanuan
'''
import os, time, types, sys

import _import_hook # import only once, do not reload

def reloadModifiedModules():
    '''
    Call this every time you run a Jython script.

    Reloads only modules that are modified.
    '''
    reloadModulesWhere(condition=__isModified)


def reloadAllModules():
    reloadModulesWhere(condition=lambda moduleName: True)

def reloadModulesWhere(condition=lambda moduleName: True):
    reload(sys.modules[__name__])
    start = time.time()
    print "Reloading modules...\n[\n",
    for modulename in sys.modules:
        if (modulename == '__main__' or
            modulename == 're' or modulename == '__builtin__' or
            modulename == 'sre_constants' # raises exception if it is reloaded
                                          # and re.compile was used
            ):
            pass
        elif condition(modulename):
            reload(sys.modules[modulename])
        else:
            pass
    print "\n]\nDone in", round(time.time() - start, 2), "seconds."


def __none(moduleName):
    return False

def __isModified(moduleName):
    '''
    Determines whether a module was modified after the last reload
    '''
    if moduleName in _import_hook.global_modules_timestamps:
        moduleFileName, oldModuleMtime = \
                _import_hook.global_modules_timestamps[moduleName]
        currentModuleMtime = time.ctime(os.path.getmtime(moduleFileName))
        condition = oldModuleMtime != currentModuleMtime
        if condition:
            print "... reloading '" + moduleName + "'",
        return condition
    else:
        return False
