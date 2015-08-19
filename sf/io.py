# -*- coding: utf-8 -*-
import sys, os, math
from PyQt4 import QtCore, QtGui

class FileIO():
    def __init__(self, parent=None):
        self.linePattern=re.compile(r'([^\t]+)\t([0-9]+)\n')

    def initializeFile(self):
        '''Read Flashcard file and add count numbers,
        then create/update lineList'''
        with open(FLASHCARD_PATH, 'r') as file:
            lineList = file.readlines()
        # Check each line in dict file if count num exist. if not, add it.
        for index, line in enumerate(lineList):
            if not self.linePattern.match(line):
                lineList[index] = re.search('([^\t]+)\n', line).group(1) + '\t' + '0' + '\n'
        self.lineList = lineList     # lineList = ['噂\t2\n','納得\t0\n']
        self.writeLineListIntoFile()

    def writeLineListIntoFile(self):
        with open(FLASHCARD_PATH, 'w') as file:
            file.writelines(self.lineList)

    def checkIfFileUpdated(self):
        newAmount = sum(1 for line in open(FLASHCARD_PATH))
        if newAmount > len(self.lineList):
            self.initializeFile()

    def setItemCountToZero(self, index):
        self.checkIfFileUpdated()
        word, count = self.getItem(index)
        self.lineList[index] = "{0}\t{1}\n".format(word, 0)
        self.writeLineListIntoFile()
        
    def increaseItemCount(self, index):
        self.checkIfFileUpdated()
        word, count = self.getItem(index)
        count += 1
        self.lineList[index] = "{0}\t{1}\n".format(word, count)
        self.writeLineListIntoFile()
        return count

    def getItem(self, index):
        item = self.linePattern.search(self.lineList[index])
        word = item.group(1)
        count = int(item.group(2))
        return word, count

    def length(self):
        return len(self.lineList)

    def archiveWord(self, index):
        self.checkIfFileUpdated()
        with open(ARCHIVE_FILE_FULLNAME, 'a') as file:
            file.write(self.lineList[index].partition('\t')[0] + '\n')
        # Delete word from list (but not write list into dict file yet)
        del self.lineList[index]
        self.writeLineListIntoFile()

    def removeWord(self, index):
        self.checkIfFileUpdated()
        del self.lineList[index]
        self.writeLineListIntoFile()

    def importArchivedFile(self, archiveFilename):
        with open(os.path.join(ARCHIVE_DIR, archiveFilename), 'r') as archiveFile:
            archive_content = archiveFile.read() # [FIXME] May I must to use self in here?
        with open(FLASHCARD_PATH, 'a') as flashcardFile:
            flashcardFileFile.write(archive_content)
        self.initializeFile()

    def archiveWholeFlashcard(self, archiveFilename):
        with open(FLASHCARD_PATH, 'r') as file:
            wholeFlashcardContent = file.read()
        with open(os.path.join(ARCHIVE_DIR, archiveFilename), 'w') as file:
            file.write(wholeFlashcardContent)
        # Clear Flashcard file.
        self.initializeFile()
        
    def editWithSystemEditor(self, filePath):
        editor = os.getenv('EDITOR')
        if editor == '':
            editor = 'vi'
        subprocess.call([editor,
                         os.path.join(ARCHIVE_DIR, filePath)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
