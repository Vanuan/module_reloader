import test_utils
import unittest
import re


class UnitTest(test_utils.TestBase):

    def setUpReloader(self):
        code = ('import module_reloader.reloader')
        result = self.executor.runCode(code)
        self.assertRunCodeOutEqual('', result)

    def importModule(self, module_name):
        module_name = '%s.%s' % (self.tests_module, module_name)
        code = 'import %s' % module_name
        result = self.executor.runCode(code)
        self.assertRunCodeOutEqual('', result)

    def addMissingTimeStamps(self):
        code = ('import module_reloader.reloader\n'
                'module_reloader.reloader._time_stamps.addMissingTimeStamps()')
        result = self.executor.runCode(code)
        return result

    def testAddMissingTimeStampsPerformance(self):
        self.setUpReloader()
        for i in range(1, 100):
            self.importModule("performance" + str(i))

        result = self.addMissingTimeStamps()
        print result
        m = re.search('addMissingTimeStamps: (0.\d*)', result[1])
        self.assertTrue(float(m.group(1)) < 0.060, str(float(m.group(1)))
                         + " should be less than 0.060")


if __name__ == "__main__":
    unittest.main()
