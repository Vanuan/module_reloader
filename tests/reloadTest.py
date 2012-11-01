'''
Created on Oct 31, 2012

@author: iyani
'''

import unittest
import shutil

import test_utils


class TestWithoutUnloading(test_utils.TestBase):

    def testImportFromMain(self):
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.reloadModifiedModules()')
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        self.assertEqual('Reloading modules...\n[\n\n]\nDone in 0.0 seconds.\n', out)

        code = 'import sys; print sys.modules[\'module_reloader.reloader\']._import_hook.global_modules_timestamps'
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        modules_timestamps = eval(out)
        self.assertFalse(modules_timestamps, 'dict should be empty')
        self.assertEqual(modules_timestamps, {})
        self.assertTrue('hello' not in modules_timestamps,
                        'dict should not contain hello: ' + str(modules_timestamps))

        code = 'import hello'
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        self.assertEqual(out, 'hello\n')

        code = 'import hello'
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        self.assertEqual(out, '')

        code = 'import sys; print sys.modules[\'module_reloader.reloader\']._import_hook.global_modules_timestamps'
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        modules_timestamps = eval(out)
        self.assertTrue('hello' in modules_timestamps)
        self.assertEqual(modules_timestamps['hello'][0], ('hello.py'))

    def testReloadShouldNotEmptyDict1(self):
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

        code = 'import hello1'
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        self.assertEqual(out, 'hello1\n')

        code = 'import hello1'
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        self.assertEqual(out, '')

        code = 'import hello1'
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
        self.assertNotEqual(modules_timestamps, {})

        self.assertTrue('hello' in modules_timestamps)
        self.assertEqual(modules_timestamps['hello'][0], ('hello.py'))

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

        test_name = self.test_scripts_dir + 'test.py'
        without_import_name = self.test_scripts_dir + 'new_import_added/test_without_import_new.py'
        with_import_name = self.test_scripts_dir + 'new_import_added/test_with_import_new.py'
        # cp new_import_added/test_without_import.py to test.py
        shutil.copy(without_import_name, test_name)

        # import test
        self.executor.runCode('import test')
        # cp new_import_added/test_with_impoirt.py to test.py
        shutil.copy(with_import_name, test_name)

        _, out, _ = self.executor.runCode('import sys; print sys.modules[\'test\']')
        print out

        self.touch(test_name)

        # reloadModified should succeed
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.reloadModifiedModules()')
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        self.assertTrue('test' in out, out)

        #self.unloadAllModules()


class TestWithUnloading(test_utils.TestBase):

    def setUp(self):
        test_utils.TestBase.setUp(self)

        # prerequisites:
        # running nailgun server
        self.reloadModifiedModules()

    def tearDown(self):
        self.unloadAllModules()

    def testModulesShouldNotBeReloadedIfNotChanged(self):
        # First import (set up)
        exitCode, out, err = self.executor.runScript(self.test_scripts_dir + 'main.py')
        self.assertEqual(0, exitCode, err)
        self.assertEqual(out, 'imported_from_imported\nimported_module\n')
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
        exitCode, out, err = self.executor.runScript(self.test_scripts_dir + 'main.py')
        self.assertEqual(0, exitCode, err)
        self.assertEqual(out, 'imported_from_imported\nimported_module\n')
        self.assertEqual(err, '')

        self.touch(self.test_scripts_dir + 'imported_module.py')

        # Reload modified modules (exercise)
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.reloadModifiedModules()')
        exitCode, out, err = self.executor.runCode(code)

        # Modules should be reloaded (verify)
        self.assertEqual(0, exitCode, err)
        self.assertTrue('Reloading modules...\n'
                            '[\n'
                            '... reloading '
                            '\'imported_module\' imported_module\n'
                            '\n]\n'
                            'Done in 0.0' in out, out)
        self.assertEqual(err, '')

    def testModulesShouldBeReloadedIfChanged2(self):
        self.unloadAllModules()
        self.reloadModifiedModules()

        # First import and change (set up)
        exitCode, out, err = self.executor.runCode('import hello')
        self.assertEqual(0, exitCode, err)
        self.assertEqual(out, 'hello\n')

        self.touch(self.test_scripts_dir + 'hello.py')

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

    def testModulesShouldBeReloadedIfChanged3(self):
        # First import and change (set up)
        exitCode, out, err = self.executor.runScript(self.test_scripts_dir + 'test_cmdlineutils.py')
        self.assertEqual(0, exitCode, err)
        self.assertEqual(out, 'hello\n')
        #self.assertEqual(err, '----------------------------------------------------------------------\nRan 15 tests in 0.019s\n\nOK\n')
        self.touch(self.test_scripts_dir + 'cmdlineutils.py')

        # Reload modified modules (exercise)
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.reloadModifiedModules()')
#        code = ('from module_reloader import reloader;'
#                ' reloader.reloadModifiedModules()')
        exitCode, out, err = self.executor.runCode(code)

        # Modules should be reloaded (verify)
        self.assertEqual(0, exitCode, out + err)
        self.assertTrue('Reloading modules...\n'
                            '[\n'
                            '... reloading '
                            '\'cmdlineutils\' hello\n'
                            '\n]\n'
                            'Done in 0.0' in out, out)
        self.assertEqual(err, '')

    def testTimestams(self):
        code = 'import sys; print sys.modules[\'module_reloader.reloader\']._import_hook.global_modules_timestamps'
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        self.assertEqual(eval(out), {})


if __name__ == "__main__":
    import sys
    sys.argv = ['', 'TestWithoutUnloading.testDictionaryChangedSize']
    #sys.argv = ['', 'TestWithUnloading.testModulesShouldBeReloadedIfChanged3']
    unittest.main()
