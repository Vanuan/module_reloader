import sys
import os
import time

global_modules_timestamps = {}


def updateTimeStamps():
    for modulename in sys.modules:
        module = sys.modules[modulename]
        if None != module and modulename not in sys.builtin_module_names and \
            modulename != '__main__':
            moduleFileName = os.path.abspath(module.__file__)
            if '__pyclasspath__' in module.__file__:
                raise Exception(module.__file__ + ' contains __pyclasspath__')
            elif not os.path.exists(moduleFileName):
                # file is probably in an egg or jar
                pass
            else:
                modifiedTimeStamp = time.ctime(os.path.getmtime(moduleFileName))
                global_modules_timestamps[modulename] = (moduleFileName,
                                                         modifiedTimeStamp)
                global_modules_timestamps


def addMissingTimeStamps():
    for modulename in sys.modules:
        module = sys.modules[modulename]
        if None != module and modulename not in sys.builtin_module_names and \
            modulename != '__main__':
            moduleFileName = os.path.abspath(module.__file__)
            if '__pyclasspath__' in module.__file__:
                raise Exception(module.__file__ + ' contains __pyclasspath__')
            elif not os.path.exists(moduleFileName):
                # file is probably in an egg or jar
                pass
            else:
                modifiedTimeStamp = time.ctime(os.path.getmtime(moduleFileName))
                global_modules_timestamps[modulename] = (moduleFileName,
                                                         modifiedTimeStamp)
                global_modules_timestamps


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


class Hook():
    def __call__(self, _):
        updateTimeStamps()


def setupHook():
    sys.path_hooks.append(Hook())


setupHook()  # make sure to call this only once
