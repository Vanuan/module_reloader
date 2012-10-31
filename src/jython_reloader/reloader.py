from org.python.core import Py
import os


def initJython(args, cwd, env):
    Py.defaultSystemState.argv = args
    Py.defaultSystemState.setCurrentWorkingDir(cwd)
    os.env = env
