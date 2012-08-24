#=======================================================
# Project: LocalAnalysis
#              SUSY Same Sign Dilepton Analysis
#
# File: messageLogger.py
#
# Author: Daniel Sprenger
#         daniel.sprenger@cern.ch
#=======================================================

class messageLogger(object):
    '''
    classdocs
    '''
    outputLevel = 5 # print all log messages
    warningCounter = 0
    errorCounter = 0


    def __init__(self):
        '''
        Constructor
        '''

    def __log(message, priority):
        if (messageLogger.outputLevel >= priority):
            print message
        return

    def logDebug(cls, message):
        cls.__log(message, 5)
        return

    def logInfo(cls, message):
        cls.__log(message, 4)
        return

    def logHighlighted(cls, message):
        cls.__log("\033[1;34mInfo: " + message + "\033[0m", 3)
        return

    def logWarning(cls, message):
        cls.__log("\033[1;33mWarning: " + message + "\033[0m", 2)
        cls.warningCounter += 1
        return

    def logError(cls, message):
        cls.__log("\033[1;31mError: " + message + "\033[0m", 1)
        cls.errorCounter += 1
        return

    def logZimLink(cls, path, width=400):
        cls.logHighlighted("Zim link to plot:\n{{file://%s?width=%d}}" % (path, width))
        return

    def logOpenCommand(cls, path):
        cls.logInfo("Command to open plot:\nopen /%s" % (path))
        return

    def printSummary(cls):
        if (cls.warningCounter > 0):
            cls.__log("\033[1;34mSummary: There have been \033[1;33m%d warnings!\033[1;m" % cls.warningCounter, 2)
        if (cls.errorCounter > 0):
            cls.__log("\033[1;34mSummary: There have been \033[1;31m%d errors!\033[1;m" % cls.errorCounter, 1)


    __log = staticmethod(__log)

    logDebug = classmethod(logDebug)
    logInfo = classmethod(logInfo)
    logHighlighted = classmethod(logHighlighted)
    logWarning = classmethod(logWarning)
    logError = classmethod(logError)
    logZimLink = classmethod(logZimLink)
    logOpenCommand = classmethod(logOpenCommand)

    printSummary = classmethod(printSummary)


