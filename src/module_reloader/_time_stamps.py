import sys
import os
import time

global_modules_timestamps = {}
exceptions = [__name__,
              'stat',
              'os',
              'os.path',
              'posixpath',
              'site',
              'module_reloader',
              'module_reloader.reloader',
              ] + list(sys.builtin_module_names)
_dependencies = {}


def __always(modulename, module):
    return True


def shouldSaveModule(module):
    modulename = module.__name__
    return (modulename not in exceptions
            and modulename != '__main__')


def moduleIsMissing(module):
    modulename = module.__name__
    return modulename not in global_modules_timestamps


def updateTimeStamp(module):
    moduleFileName = getFileName(module)
    if moduleFileName is not None:
        modulename = module.__name__
        modifiedTimeStamp = time.ctime(os.path.getmtime(moduleFileName))
        global_modules_timestamps[modulename] = (moduleFileName,
                                                 modifiedTimeStamp)


def getFileName(module):
    moduleFileName = os.path.abspath(module.__file__)
    if moduleFileName.endswith('$py.class'):
        moduleFileName = moduleFileName[:-len('$py.class')] + '.py'
    if '__pyclasspath__' in module.__file__:
        raise Exception(module.__file__ + ' contains __pyclasspath__')
    if not os.path.exists(moduleFileName):
        # file is probably in an egg or jar
        return None
    return moduleFileName


def updateTimeStampsWhere(updateCondition=__always):
    for module in filter(lambda m: m is not None, sys.modules.values()):
        if shouldSaveModule(module):
            if updateCondition(module):
                updateTimeStamp(module)


def addMissingTimeStamps():
    updateTimeStampsWhere(updateCondition=moduleIsMissing)


def isModified(moduleName):
    '''
    Determines whether a module was modified after the last reload
    '''
    if moduleName in global_modules_timestamps:
        moduleFileName, oldModuleMtime = \
                global_modules_timestamps[moduleName]
        currentModuleMtime = time.ctime(os.path.getmtime(moduleFileName))
        condition = oldModuleMtime != currentModuleMtime
        return condition
    else:
        return False


import __builtin__


class Importer:
    def __init__(self):
        "Creates an instance and installs as the global importer"
        self.realImport = __builtin__.__import__
        __builtin__.__import__ = self._import
        self._parent = None

    def _import(self, name, globals_=None, locals_=None, fromlist=[]):
        parent = self._parent
        self._parent = name

        module = apply(self.realImport, (name, globals_, locals_, fromlist))
        addMissingTimeStamps()

        if parent is not None and hasattr(module, '__file__'):
            l = _dependencies.setdefault(parent, [])
            l.append(module.__name__)

        return module

#setupHook()  # make sure to call this only once
imorter = Importer()
