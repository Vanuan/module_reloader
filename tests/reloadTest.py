'''
Created on Oct 31, 2012

@author: iyani
'''
from __future__ import with_statement
import unittest
import os
import subprocess
import time
import ConfigParser


class Settings():
    def __init__(self):
        filename = os.path.dirname(__file__) + '/config.ini'
        self.config = ConfigParser.RawConfigParser()
        self.config.optionxform = str
        self.config.read(filename)

    def getPathToNgClient(self):
        return self.config.get('nailgun', 'path_to_client')

    def getPathToJython(self):
        return self.config.get('jython', 'path_to_jython')

    def getPathToJythonLib(self):
        return self.config.get('jython', 'path_to_jython_lib')


class Test(unittest.TestCase):

    def setUp(self):
        settings = Settings()
        self.path_to_nailgun_client = settings.getPathToNgClient()
        self.path_to_jython = settings.getPathToJython()
        self.path_to_jython_lib = settings.getPathToJythonLib()
        self.reloader_path = os.path.dirname(__file__) + '/../src'
        self.test_scripts_dir = os.path.dirname(__file__) + '/testScripts/'
        # add folder to classpath
        exitCode, _, err = self.addToClassPath(self.path_to_jython)
        self.assertEqual(0, exitCode, err)
        exitCode, _, err = self.addToClassPath(self.path_to_jython_lib)
        self.assertEqual(0, exitCode, err)
        exitCode, _, err = self.addToClassPath(self.reloader_path)
        self.assertEqual(0, exitCode, err)
        # prerequisites:
        # running nailgun server
        self.setUpModules()

    def setUpModules(self):
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.unloadAllModules()')
        exitCode, _, err = self.runCode(code)
        self.assertEqual(0, exitCode, err)
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.reloadModifiedModules()')
        exitCode, _, err = self.runCode(code)
        self.assertEqual(0, exitCode, err)

    def execute(self, args):
        p = subprocess.Popen(args, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exitCode = p.wait()
        (out, err) = p.communicate()

        return (exitCode, out, err)

    def executeNgClient(self, args):
        result = self.execute([self.path_to_nailgun_client] + args)
        return result

    def addToClassPath(self, path):
        result = self.executeNgClient(['ng-cp', path])
        return result

    def runCode(self, code):
        result = self.executeNgClient(['org.python.util.jython', '-c', code])
        return result

    def runScript(self, path):
        result = self.executeNgClient(['org.python.util.jython', path])
        return result

    def touch(self, fname, times=None):
        with file(fname, 'a'):
            os.utime(fname, times)
        # wait 1 second to make sure that current time would be greater than
        # file modification time
        time.sleep(1)

    def testModulesShouldNotBeReloadedIfNotChanged(self):
        # First import (set up)
        exitCode, out, err = self.runScript(self.test_scripts_dir + 'main.py')
        self.assertEqual(0, exitCode, err)
        self.assertEqual(out, 'imported_from_imported\nimported_module\n')
        self.assertEqual(err, '')

        # Reload modified modules (exercise)
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.reloadModifiedModules()')
        exitCode, out, err = self.runCode(code)
        self.assertEqual(0, exitCode)
        self.assertEqual(out, 'Reloading modules...\n'
                         '[\n\n]\nDone in 0.0 seconds.\n')
        self.assertEqual(err, '')

        # Next imports should not re-import modules (verify)
        exitCode, out, err = self.runScript(self.test_scripts_dir + 'main.py')
        self.assertEqual(0, exitCode)
        self.assertEqual(out, '')
        self.assertEqual(err, '')

    def testModulesShouldBeReloadedIfChanged(self):
        # First import and change (set up)
        exitCode, out, err = self.runScript(self.test_scripts_dir + 'main.py')
        self.assertEqual(0, exitCode, err)
        self.assertEqual(out, 'imported_from_imported\nimported_module\n')
        self.assertEqual(err, '')
        self.touch(self.test_scripts_dir + 'imported_module.py')

        # Reload modified modules (exercise)
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.reloadModifiedModules()')
        exitCode, out, err = self.runCode(code)

        # Modules should be reloaded (verify)
        self.assertEqual(0, exitCode, err)
        self.assertTrue('Reloading modules...\n'
                            '[\n'
                            '... reloading '
                            '\'imported_module\' imported_module\n'
                            '\n]\n'
                            'Done in 0.0' in out, out)
        self.assertEqual(err, '')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testReload']
    unittest.main()
