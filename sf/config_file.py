# -*- coding: utf-8 -*-
import sys, os, math, configparser
from PyQt4 import QtCore, QtGui
from .main import *

class ConfigFile():
    ROOT = os.path.expanduser('~/.stardict-flashcard/')
    CONFIG_PATH = os.path.join(ROOT, 'rc.ini')
    ARCHIVE_DIR = os.path.join(ROOT, 'archive')
    ACT_ICON_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons/actions/')
    OPEN_FIRST_TIME_HELP = False
    
    def __init__(self, parent=None):
        if not os.path.isdir(ROOT):
            os.makedirs(ROOT)
        if not os.path.isfile(CONFIG_PATH):
            self.OPEN_FIRST_TIME_HELP = True
            with open(CONFIG_PATH, 'w') as file:
                file.write('''[Path]
FlashcardPath = ~/dic.txt
ArchiveFileName = default-archive

[Main]
MemorizedCount = 5
RememberIndex = 0

[Other]
FirstTimeHelp = True
''')
        # Config
        self.parser = configparser.ConfigParser()
        self.parser.optionxform = str # Preserve cases of keys.
        self.parser.read(CONFIG_PATH)
        try:
            self.initializeGlobalVar()
        except KeyError: # if the format of config file has been changed.
            os.remove(CONFIG_PATH)
            self.__init__()
            
    def initializeGlobalVar(self):
        self.FLASHCARD_PATH        = os.path.expanduser(self.parser['Path']['FlashcardPath'])
        self.ARCHIVE_FILE_NAME     = self.parser['Path']['ArchiveFileName']
        self.ARCHIVE_FILE_FULLNAME = os.path.join(self.ARCHIVE_DIR, self.ARCHIVE_FILE_NAME)
        self.MEMORIZED_COUNT       = int(self.parser['Main']['MemorizedCount'])
        self.REMEMBER_INDEX        = int(self.parser['Main']['RememberIndex'])
        # if Archive dir & file not exist, create
        if not os.path.isdir(self.ARCHIVE_DIR):
            os.makedirs(self.ARCHIVE_DIR)
        if not os.path.exists(ARCHIVE_FILE_FULLNAME):
            open(ARCHIVE_FILE_FULLNAME, 'a').close() # touch current archive file

    def writeConfigFile(self):
        self.parser['Path']['FlashcardPath']   = self.FLASHCARD_PATH
        self.parser['Path']['ArchiveFileName'] = self.ARCHIVE_FILE_NAME
        self.parser['Main']['MemorizedCount']  = str(self.MEMORIZED_COUNT)
        self.parser['Main']['RememberIndex']   = str(self.REMEMBER_INDEX)
        with open(CONFIG_PATH, 'w') as file:
            self.parser.write(file)


