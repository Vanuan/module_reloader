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
_dependants = {}


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
    if not hasattr(module, '__file__') or module.__file__ is None:
        return None
    if '__pyclasspath__' in module.__file__:
        #raise Exception(module.__file__ + ' contains __pyclasspath__')
        print "warning: " + module.__file__ + ' contains __pyclasspath__'
        return None
    moduleFileName = os.path.abspath(module.__file__)
    if moduleFileName.endswith('$py.class'):
        moduleFileName = moduleFileName[:-len('$py.class')] + '.py'
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


def deleteDependencies(name):
    try:
        del _dependencies[name]
    except KeyError:
        pass


def deleteDependants(name):
    try:
        del _dependants[name]
    except KeyError:
        pass


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
        self._dependant = None

    def _import(self, name, globals_=None, locals_=None, fromlist=[]):
        dependant = self._dependant
        self._dependant = name

        module = apply(self.realImport, (name, globals_, locals_, fromlist))

        # If we have a parent (i.e. this is a nested import) and this is a
        # reloadable (source-based) module, we append ourself to our parent's
        # dependency list.
        if dependant is not None and hasattr(module, '__file__'):
            dependencies = _dependencies.setdefault(dependant, [])
            dependency_name = module.__name__
            dependencies.append(dependency_name)

            dependant_m = sys.modules.get(dependant, None)
            if dependant_m is not None and hasattr(dependant_m, '__file__'):
                dependants = _dependants.setdefault(dependency_name, [])
                dependants.append(dependant_m.__name__)

        # Lastly, we always restore our global _parent pointer.
        self._dependant = dependant

        return module


#setupHook()  # make sure to call this only once
importer = Importer()


def _reload(m, visited):
    """Internal module reloading routine."""
    name = m.__name__

    # Start by adding this module to our set of visited modules.  We use
    # this set to avoid running into infinite recursion while walking the
    # module dependency graph.
    visited.add(name)

    # Clear this module's list of dependencies.  Some import statements
    # may have been removed.  We'll rebuild the dependency list as part
    # of the reload operation below.
    deleteDependencies(name)
    #deleteDependants(name)

    # Because we're triggering a reload and not an import, the module
    # itself won't run through our _import hook.  In order for this
    # module's dependencies (which will pass through the _import hook) to
    # be associated with this module, we need to set our parent pointer
    # beforehand.
    importer._dependant = name

    # Perform the reload operation.
    print "... reloading '" + name + "'",
    reload(m)

    # now reload dependants of this module
    dependants = getDependants(name)
    if dependants is not None:
        for dependant in reversed(dependants):
            if dependant not in visited:
                _reload(sys.modules[dependant], visited)

    # Reset our parent pointer.
    importer._dependant = None


def getDependencies(name):
    return _dependencies.get(name, None)


def getDependants(name):
    return _dependants.get(name, None)
