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
import time
import sys

#import _import_hook  # import only once, do not reload
import _time_stamps  # import only once, do not reload
import __builtin__


class RollbackImporter:
    '''
    This is good for making sys.modules exactly like it was before
    '''
    def __init__(self):
        "Creates an instance and installs as the global importer"
        self.previousModules = sys.modules.copy()
        self.realImport = __builtin__.__import__
        __builtin__.__import__ = self._import
        self.newModules = {}

    # pep8-ignore: E241
    def _import(self, name, globals_=None, locals_=None, fromlist=[]):
        result = apply(self.realImport, (name, globals_, locals_, fromlist))
        self.newModules[name] = 1
        print '_import', name, result
        return result

    def uninstall(self):
        for modname in self.newModules.keys():
            if modname not in self.previousModules:
                # Force reload when modname next imported
                print 'there was no ' + modname
                if modname in sys.modules:
                    print 'deleting ' + modname
                    del(sys.modules[modname])
        __builtin__.__import__ = self.realImport


#rollbackImporter = RollbackImporter()

def removePythonModules():
    for module in filter(lambda name: _time_stamps.isJavaPackage(name), sys.modules):
        del sys.modules[module]

def reloadModifiedModules():
    removePythonModules()
    return None
    '''
    Call this every time you run a Jython script.

    Reloads only modules that are modified.
    '''
    reloadModulesWhere(condition=_time_stamps.isModified)


def reloadAllModules():
    reloadModulesWhere(condition=lambda moduleName: True)


def reloadModulesWhere(condition=lambda moduleName: True):
    start = time.time()
    print "Reloading modules...\n[\n",
    _time_stamps.addMissingTimeStamps()

    #global rollbackImporter

    for modulename in sys.modules:
        if (modulename == '__main__' or
            modulename == 're' or modulename == '__builtin__' or
            modulename == 'sre_constants'  # raises exception if it is reloaded
                                           # and re.compile was used
            ):
            pass
        elif condition(modulename):
            module = sys.modules[modulename]
            reloadWithDependants(module)
            _time_stamps.updateTimeStamp(module, modulename)
            #rollbackImporter = RollbackImporter()
        else:
            pass
    print "\n]\nDone in", round(time.time() - start, 2), "seconds."

    #if rollbackImporter:
    #   rollbackImporter.uninstall()
#    rollbackImporter = RollbackImporter()


def reloadWithDependants(module):
    """Reload an existing module.

    Any known dependencies of the module will also be reloaded."""
    _time_stamps._reload(module, set())


#def unloadAllModules():
#    exceptions = sys.builtin_module_names + ('_import_hook', 'reloader',
#                                             'module_reloader', '__main__')
#    moduleNames = filter(lambda x: x not in exceptions, sys.modules.keys())
#    for modulename in moduleNames:
#        del(sys.modules[modulename])


def __none(moduleName):
    return False


def getTimeStamps():
    return _time_stamps.global_modules_timestamps


def getDependencies(name):
    return _time_stamps.getDependencies(name)


def getDependants(name):
    return _time_stamps.getDependants(name)
