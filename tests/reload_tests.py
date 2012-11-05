'''
Created on Oct 31, 2012

@author: iyani
'''

import unittest
import shutil

import test_utils


class TestReloading(test_utils.TestBase):
    def importHello(self):
        module_name = '%s.hello' % self.tests_module
        code = 'import %s' % module_name
        result = self.executor.runCode(code)
        self.assertRunCodeOutEqual(module_name + '\n', result)

    def importHelloAgain(self):
        module_name = '%s.hello' % self.tests_module
        code = 'import %s' % module_name
        result = self.executor.runCode(code)
        self.assertRunCodeOutEqual('', result)

    def getActualTimeStamps(self):
        code = ('import module_reloader.reloader\n'
                'print module_reloader.reloader.getTimeStamps()')
        errCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, errCode, err)
        return eval(out)

    def testReloadShouldNotEmptyDict2(self):
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.reloadModifiedModules()')
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        self.assertEqual('Reloading modules...\n[\n\n]\nDone in 0.0 seconds.\n', out)

        code = 'import sys; print sys.modules[\'module_reloader.reloader\']._import_hook.global_modules_timestamps'
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        modules_timestamps = eval(out)
        self.assertEqual(modules_timestamps, {})

        code = 'import hello '
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        self.assertEqual(out, 'hello\n')

        code = 'import hello'
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        self.assertEqual(out, '')

        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.reloadModifiedModules()')
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        self.assertEqual('Reloading modules...\n[\n\n]\nDone in 0.0 seconds.\n', out)

        code = 'import sys; print sys.modules[\'module_reloader.reloader\']._import_hook.global_modules_timestamps'
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        modules_timestamps = eval(out)
        self.assertTrue('hello' in modules_timestamps)
        self.assertEqual(modules_timestamps['hello'][0], ('hello.py'))

    def testDictionaryChangedSize(self):

        self.reloadModifiedModules()
        #self.unloadAllModules()
#        self.executor.runCode('import test')
#        #self.reloadModifiedModules()
#        self.unloadAllModules()

#        code = ('import module_reloader.reloader;'
#                ' module_reloader.reloader.reloadModifiedModules()')
#        exitCode, _, err = self.executor.runCode(code)
#        self.assertEqual(0, exitCode, err)

        test_name = self.test_scripts_module_dir + 'test.py'
        without_import_name = self.test_scripts_module_dir + 'new_import_added/test_without_import_new.py'
        with_import_name = self.test_scripts_module_dir + 'new_import_added/test_with_import_new.py'
        # cp new_import_added/test_without_import.py to test.py
        shutil.copy(without_import_name, test_name)

        # import test
        self.executor.runCode('import nailgun_reloader.test')
        # cp new_import_added/test_with_impoirt.py to test.py
        shutil.copy(with_import_name, test_name)

        _, out, _ = self.executor.runCode('import sys; print sys.modules[\'nailgun_reloader.test\']')
        print out

        _, out, _ = self.executor.runCode('import sys; print sys.modules[\'module_reloader._import_hook\'].global_modules_timestamps')
        print out

        self.touch(test_name)

        # reloadModified should succeed
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.reloadModifiedModules()')
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        self.assertTrue('test' in out, out)

        #self.unloadAllModules()

    def testModulesShouldNotBeReloadedIfNotChanged(self):
        # First import (set up)
        exitCode, out, err = self.executor.runScript(self.test_scripts_dir + 'main.py')
        self.assertEqual(0, exitCode, err)
        self.assertEqual(out, self.import_string)
        self.assertEqual(err, '')

        # Reload modified modules (exercise)
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.reloadModifiedModules()')
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode)
        self.assertEqual(out, 'Reloading modules...\n'
                         '[\n\n]\nDone in 0.0 seconds.\n')
        self.assertEqual(err, '')

        # Next imports should not re-import modules (verify)
        exitCode, out, err = self.executor.runScript(self.test_scripts_dir + 'main.py')
        self.assertEqual(0, exitCode)
        self.assertEqual(out, '')
        self.assertEqual(err, '')

    def testModulesShouldBeReloadedIfChanged1(self):
        # First import and change (set up)
        exitCode, out, err = self.executor.runScript(
                                self.test_scripts_module_dir + 'main.py')
        self.assertEqual(0, exitCode, err)
        self.assertEqual(out, 'imported_from_imported\nfrom_module_import\nimported_module\n')
        self.assertEqual(err, '')

        self.touch(self.test_scripts_module_dir + 'imported_module.py')
        self.touch(self.test_scripts_module_dir + 'from_module_import.py')

        # Reload modified modules (exercise)
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.reloadModifiedModules()')
        exitCode, out, err = self.executor.runCode(code)

        # Modules should be reloaded (verify)
        self.assertEqual(0, exitCode, err)
        self.assertTrue('Reloading modules...\n'
                            '[\n'
                            '... reloading '
                            '\'from_module_import\' from_module_import\n'
                            '... reloading '
                            '\'imported_module\' imported_module\n'
                            '\n]\n'
                            'Done in 0.0' in out, out)
        self.assertEqual(err, '')

    def testUseWithoutImport(self):
        # First import (set up)
        exitCode, out, err = self.runScript(self.test_scripts_dir + 'main.py')
        self.assertEqual(0, exitCode, err)
        self.assertEqual(out, self.import_string)
        self.assertEqual(err, '')

        # use module without import
        exitCode, out, err = self.runScript(self.test_scripts_dir +
                                            'use_module_without_import.py')
        self.assertEqual(0, exitCode, out + err)
        self.assertEqual(out, '')
        self.assertEqual(err, '')

    def testModulesShouldBeReloadedIfChanged2(self):
        # First import and change (set up)
        code = 'import module_reloader.reloader'
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, out + err)

        code = 'import nailgun_reloader.hello'
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        self.assertEqual(out, 'nailgun_reloader.hello\n')

        self.touch(self.test_scripts_module_dir + 'hello.py')

        # Reload modified modules (exercise)
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.reloadModifiedModules()')
        exitCode, out, err = self.executor.runCode(code)

        # Modules should be reloaded (verify)
        self.assertEqual(0, exitCode, out + err)
        self.assertTrue('Reloading modules...\n'
                            '[\n'
                            '... reloading '
                            '\'hello\' hello\n'
                            '\n]\n'
                            'Done in 0.0' in out, out)
        self.assertEqual(err, '')

    def testTimestams(self):
        code = ('import sys\n'
                'print sys.modules[\'module_reloader.reloader\']'
                '._import_hook.global_modules_timestamps')
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        self.assertEqual(eval(out), {})


class TestServer(test_utils.TestBase):
    def testServerStartStop(self):
        self.assertEqual((0, 'Hello\n', ''),
                         self.executor.runCode('print "Hello"'))

if __name__ == "__main__":
    import sys
    sys.argv = ['', 'TestReloading.testReloadShouldNotClearTimeStamps']
    #sys.argv = ['', 'TestWithUnloading.testModulesShouldBeReloadedIfChanged3']
    #sys.argv = ['', 'TestWithoutUnloading.testDictionaryChangedSize']
    unittest.main()
