'''
Created on Oct 31, 2012

@author: iyani
'''

import unittest
import os
import time
import re

import test_utils


class UnitTest(test_utils.TestBase):

    def buildFilename(self, moduleName):
        filename = (self.test_scripts_module_dir +
                    moduleName + '.py')
        return filename

    def buildExpectedTimeStamps(self, names):
        expected_timestamps = {}
        for name in names:
            moduleName = self.tests_module
            if '__init__' != name:
                moduleName += '.' + name
            module_filename = self.buildFilename(name)
            module_timestamp = time.ctime(
                os.path.getmtime(module_filename))
            expected_timestamps[moduleName] = (
                (module_filename, module_timestamp))
        return expected_timestamps

    def getActualTimeStamps(self):
        code = ('import module_reloader.reloader\n'
                'print module_reloader.reloader.getTimeStamps()')
        errCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, errCode, err)
        return eval(out)

    def setUpReloader(self):
        code = ('import module_reloader.reloader')
        result = self.executor.runCode(code)
        self.assertRunCodeOutEqual('', result)

    def addMissingTimeStamps(self):
        code = ('import module_reloader.reloader\n'
                'module_reloader.reloader._time_stamps.addMissingTimeStamps()')
        (exitcode, out, err) = self.executor.runCode(code)
        pattern2 = re.compile('addMissingTimeStamps: 0.\d* s\n')
        out = pattern2.sub('', out)
        self.assertRunCodeOutEqual('', (exitcode, out, err))

    def importHello(self):
        '''
        We can import module from package in different ways:
        1) import package.module
        2) from package import module

        In both cases sys.modules would be equal

        1) in the first case current module will contain
        package object with module attribute
        2) in the second case current module will contain only module symbol

        We can't use module just importing the package, i.e.
        "import package; package.module" would fail.
        '''
        module_name = '%s.hello' % self.tests_module
        code = 'import %s' % module_name
        result = self.executor.runCode(code)
        self.assertRunCodeOutEqual(module_name + '\n', result)

    def importHelloAgain(self):
        module_name = '%s.hello' % self.tests_module
        code = 'import %s' % module_name
        result = self.executor.runCode(code)
        self.assertRunCodeOutEqual('', result)

    def importWithDependency(self):
        dependant_module = '%s.dependant' % self.tests_module
        dependency_module = '%s.dependency' % self.tests_module
        code = 'import %s' % dependant_module
        result = self.executor.runCode(code)
        self.assertRunCodeOutEqual(dependency_module + '\n' +
                                   dependant_module + '\n', result)

    def importWithDependencyAgain(self):
        dependant_module = '%s.dependant' % self.tests_module
        code = 'import %s' % dependant_module
        result = self.executor.runCode(code)
        self.assertRunCodeOutEqual('', result)

    def buildExpectedReloading(self, modulenames):
        reloadingString = 'Reloading modules...\n[\n'
        for name in modulenames:
            modulename = self.tests_module + '.' + name
            reloadingString += ('... reloading \'' + modulename + '\' ' +
                                modulename + '\n')
        reloadingString += '\n]\nDone in 0.0 seconds.\n'
        return reloadingString

    def reloadModified(self, modulenames=[]):
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.reloadModifiedModules()')
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, out + err)
        pattern1 = re.compile('0.0[1,2]? seconds.')
        out = pattern1.sub('', out)
        pattern2 = re.compile('addMissingTimeStamps: 0.\d* s\n')
        out = pattern2.sub('', out)
        expected = pattern1.sub('', self.buildExpectedReloading(modulenames))
        self.assertEqual(expected, out)

    def getDependencies(self, dependant):
        code = ('import module_reloader.reloader\n'
                'print module_reloader.reloader.getDependencies(\'' +
                self.tests_module + '.' + dependant + '\')')
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        dependencies = eval(out)
        return dependencies

    def getDependants(self, dependency):
        code = ('import module_reloader.reloader\n'
                'print module_reloader.reloader.getDependants(\'' +
                self.tests_module + '.' + dependency + '\')')
        exitCode, out, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)
        dependencies = eval(out)
        return dependencies

    def testImportShouldSaveTimeStamps(self):
        '''
        import should result in time stamps being saved
        '''
        # setup reloader, verify preconditions
        self.setUpReloader()
        modules_timestamps = self.getActualTimeStamps()
        self.assertEqual(modules_timestamps, {})

        # exercise import statement
        self.importHello()
        self.addMissingTimeStamps()

        # verify that module time stamps are saved
        expected_timestamps = self.buildExpectedTimeStamps(['__init__',
                                                            'hello'])
        actual_timestamps = self.getActualTimeStamps()
        self.assertEqual(expected_timestamps, actual_timestamps)

    def testImportShouldNotRewriteTimeStamps(self):
        '''
        import should not result in time stamps being rewritten by new ones
        '''
        # setup
        self.setUpReloader()
        self.importHello()
        self.addMissingTimeStamps()
        expected_timestamps = self.buildExpectedTimeStamps(['__init__',
                                                            'hello'])
        # modify real time stamp
        self.touch(self.buildFilename('hello'))

        # exercise import statement
        self.importHelloAgain()
        self.addMissingTimeStamps()

        # verify that time stamps are the same
        actual_timestamps = self.getActualTimeStamps()
        self.assertEqual(expected_timestamps, actual_timestamps)

    def testReloadShouldNotRewriteTimeStampsIfNotChanged(self):
        # setup
        self.setUpReloader()
        self.importHello()
        self.addMissingTimeStamps()

        prev_modules_timestamps = self.getActualTimeStamps()

        # exercise
        self.reloadModified()

        # verify
        cur_modules_timestamps = self.getActualTimeStamps()
        self.assertEqual(prev_modules_timestamps, cur_modules_timestamps)

    def testReloadShouldRewriteTimeStampsIfChanged(self):
        # setup
        self.setUpReloader()
        self.importHello()
        self.addMissingTimeStamps()

        # modify real time stamp
        self.touch(self.buildFilename('hello'))
        expected_timestamps = self.buildExpectedTimeStamps(['__init__',
                                                            'hello'])

        # exercise
        self.reloadModified(['hello'])

        # verify
        actual_timestamps = self.getActualTimeStamps()
        self.assertEqual(expected_timestamps, actual_timestamps)

    def testGetHelloDependency(self):
        # setup
        self.setUpReloader()
        self.importHello()

        # exercise
        dependencies = self.getDependencies('hello')

        # verify
        expectedDependencies = None
        self.assertEqual(expectedDependencies, dependencies)

    def testGetDependantDependency(self):
        # setup
        self.setUpReloader()
        self.importWithDependency()

        # exercise
        dependencies = self.getDependencies('dependant')

        # verify
        expectedDependencies = [self.tests_module + '.dependency']
        self.assertEqual(expectedDependencies, dependencies)

    def testGetDependencyDependants(self):
        # setup
        self.setUpReloader()
        self.importWithDependency()

        # exercise
        dependants = self.getDependants('dependency')

        # verify
        expectedDependants = [self.tests_module + '.dependant']
        self.assertEqual(expectedDependants, dependants)

    def testReloadDependantIfDependencyChanged(self):
        # setup
        self.setUpReloader()
        self.importWithDependency()
        self.addMissingTimeStamps()

        # exercise & verify
        self.touch(self.buildFilename('dependency'))

        self.reloadModified(['dependency', 'dependant'])

        self.importWithDependencyAgain()

    def testDoNotReloadDependenciesIfDependantChanged(self):
        # setup
        self.setUpReloader()
        self.importWithDependency()
        self.addMissingTimeStamps()

        # exercise & verify
        self.touch(self.buildFilename('dependant'))

        self.reloadModified(['dependant'])

        self.importWithDependencyAgain()


if __name__ == "__main__":
    unittest.main()
