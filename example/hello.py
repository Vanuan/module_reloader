from module_reloader import reloader
reloader.reloadModifiedModules()

import module_to_be_reloaded
module_to_be_reloaded.test()


import jython_reloader
jython_reloader.reloader.initJython(["hello"], "path/to/hello", {'ENV': 'VAL'})

import sys
import os
print sys.argv
print os.environ
print sys.getCurrentWorkingDir()
