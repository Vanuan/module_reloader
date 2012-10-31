'''
Created on Oct 31, 2012

@author: iyani
'''
from __future__ import with_statement
import unittest
import os
import subprocess
import time

class Test(unittest.TestCase):

    def setUp(self):
        self.path_to_nailgun_client = '/home/iyani/Downloads/nailgun-0.7.1/ng'
        self.path_to_jython = '/opt/jython/jython-2.5.3/jython.jar'
        self.reloader_path = os.path.dirname(__file__) + '/../src'
        self.test_scripts_dir = os.path.dirname(__file__) + '/testScripts/'
        # add folder to classpath
        exitCode, out, err = self.addToClassPath(self.path_to_jython)
        self.assertEqual(0, exitCode, err)
        exitCode, out, err = self.addToClassPath(self.reloader_path)
        self.assertEqual(0, exitCode, err)
        # prerequisites:
        # running nailgun server
        self.setUpModules()


    def setUpModules(self):
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.unloadAllModules()')
        exitCode, out, err = self.runCode(code)
        self.assertEqual(0, exitCode, err)
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.reloadModifiedModules()')
        exitCode, out, err = self.runCode(code)
        self.assertEqual(0, exitCode, err)


    def execute(self, args):
        p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exitCode = p.wait()
        (out, err) = p.communicate()

        return (exitCode, out, err)

    def executeNgClient(self, args):
        tuple = self.execute([self.path_to_nailgun_client] + args)
        return tuple

    def addToClassPath(self, path):
        tuple = self.executeNgClient(['ng-cp', path])
        return tuple

    def runCode(self, code):
        tuple = self.executeNgClient(['org.python.util.jython', '-c', code])
        return tuple

    def runScript(self, path):
        tuple = self.executeNgClient(['org.python.util.jython', path])
        return tuple

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
        self.assertEqual(out, 'Reloading modules...\n[\n\n]\nDone in 0.0 seconds.\n')
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
                            '... reloading \'imported_module\' imported_module\n'
                            '\n]\n'
                            'Done in 0.0' in out, out)
        self.assertEqual(err, '')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testReload']
    unittest.main()