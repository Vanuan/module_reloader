from __future__ import with_statement

import os
import ConfigParser
import unittest
import subprocess
import time


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


class Executor():

    def __init__(self, path_to_nailgun_client):
        self.path_to_nailgun_client = path_to_nailgun_client

    def executeNgClient(self, args):
        result = execute([self.path_to_nailgun_client] + args)
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


def execute(args):
    p = subprocess.Popen(args, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exitCode = p.wait()
    (out, err) = p.communicate()

    return (exitCode, out, err)


class TestBase(unittest.TestCase):

    def unloadAllModules(self):
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.unloadAllModules()')
        exitCode, _, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)

    def reloadModifiedModules(self):
        code = ('import module_reloader.reloader;'
                ' module_reloader.reloader.reloadModifiedModules()')
        exitCode, _, err = self.executor.runCode(code)
        self.assertEqual(0, exitCode, err)

    def touch(self, fname, times=None):
        with file(fname, 'a'):
            os.utime(fname, times)
        # wait 1 second to make sure that current time would be greater than
        # file modification time
        time.sleep(1)

    def dictdiff(self, d1, d2):
        return dict(set(d2.iteritems()) - set(d1.iteritems()))

    def setUp(self):
        settings = Settings()
        self.executor = Executor(settings.getPathToNgClient())
        self.path_to_jython = settings.getPathToJython()
        self.path_to_jython_lib = settings.getPathToJythonLib()
        self.reloader_path = os.path.dirname(__file__) + '/../src'
        self.test_scripts_dir = os.path.dirname(__file__) + '/testScripts/'
        # add folder to classpath
        exitCode, _, err = self.executor.addToClassPath(self.path_to_jython)
        self.assertEqual(0, exitCode, err)
        exitCode, _, err = self.executor.addToClassPath(self.path_to_jython_lib)
        self.assertEqual(0, exitCode, err)
        exitCode, _, err = self.executor.addToClassPath(self.reloader_path)
        self.assertEqual(0, exitCode, err)
        exitCode, _, err = self.executor.addToClassPath(self.test_scripts_dir)
        self.assertEqual(0, exitCode, err)
        self.executor.addToClassPath('/home/iyani/.m2/repository/commons-cli/commons-cli/1.2/commons-cli-1.2.jar')
