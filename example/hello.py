from module_reloader import reloader
reloader.reloadModifiedModules()

import module_to_be_reloaded
module_to_be_reloaded.test()
