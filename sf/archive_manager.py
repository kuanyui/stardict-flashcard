# -*- coding: utf-8 -*-
import sys, os, math
from PyQt4 import QtCore, QtGui
class ArchiveFileManager(QtGui.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.tree = QtGui.QTreeWidget()
        self.tree.setHeaderLabels([self.tr("Current"),
                                   self.tr("Filename"),
                                   self.tr("Words")])

        self.reloadArchiveFiles()
        
        self.tree.setColumnWidth(0, 24)
        self.tree.setColumnWidth(1, 300)
        self.tree.setColumnWidth(2, 24)
        self.tree.setRootIsDecorated(False)

        self.tree.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tree.itemClicked.connect(self.updateButtonState)
        
        # buttons
        self.b_new              = IconButton('l', 'new.png', self.tr('&New'), self.new)
        self.b_rename           = IconButton('l', 'rename.png', self.tr('&Rename'), self.rename)
        self.b_edit             = IconButton('l', 'edit.png', self.tr('&Edit'), self.edit)
        self.b_merge            = IconButton('l', 'merge.png', self.tr('&Merge'), self.merge)
        self.b_delete           = IconButton('l', 'delete.png', self.tr('&Delete'), self.delete)
        self.b_remove_duplicate = IconButton('l', 'remove_duplicated.png', self.tr('Remove Duplicated'), self.removeDuplicated)
        self.b_import_to_dict   = IconButton('l', 'import.png', self.tr('&Import to Flashcard'), self.importToFlashcard)
        self.b_set_as_default   = IconButton('l', 'star.png', self.tr('&Set As Current'), self.setAsDefault)
        close                   = IconButton('l', 'exit.png', self.tr('&Close'), self.close)

        
        button_layout = QtGui.QVBoxLayout()
        button_layout.addWidget(self.b_new)
        button_layout.addWidget(self.b_rename)
        button_layout.addWidget(self.b_edit)
        button_layout.addWidget(self.b_merge)
        button_layout.addWidget(self.b_delete)
        button_layout.addSpacing(16)
        button_layout.addWidget(self.b_remove_duplicate)
        button_layout.addSpacing(16)
        button_layout.addWidget(self.b_import_to_dict)
        button_layout.addWidget(self.b_set_as_default)
        button_layout.addStretch()
        button_layout.addWidget(close)

        #layout
        main_layout = QtGui.QHBoxLayout()
        main_layout.addWidget(self.tree)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        self.resize(550, 300)
        # make main window uncontrollable.
        self.setWindowModality(QtCore.Qt.WindowModal)

        # for dialog retry
        self.userInput = ""

    def updateButtonState(self):
        if len(self.tree.selectedItems()) > 1:
            self.b_new.setEnabled(False)
            self.b_rename.setEnabled(False)
            self.b_edit.setEnabled(False)
            self.b_delete.setEnabled(False)
            self.b_remove_duplicate.setEnabled(False)
            self.b_import_to_dict.setEnabled(False)
            self.b_set_as_default.setEnabled(False)
        else:
            self.b_new.setEnabled(True)
            self.b_rename.setEnabled(True)
            self.b_edit.setEnabled(True)
            self.b_delete.setEnabled(True)
            self.b_remove_duplicate.setEnabled(True)
            self.b_import_to_dict.setEnabled(True)
            self.b_set_as_default.setEnabled(True)
            
    def reloadArchiveFiles(self):
        global ARCHIVE_FILE_NAME
        self.tree.clear()
        itemList = []
        for fileName in os.listdir(ARCHIVE_DIR):
            filePath = os.path.join(ARCHIVE_DIR, fileName)
            wordsAmount = sum(1 for line in open(filePath))
            item = QtGui.QTreeWidgetItem()
            item.setData(0, 0, "")
            item.setData(1, 0, fileName)
            item.setData(2, 0, str(wordsAmount))
            itemList.append(item)
            
        self.tree.addTopLevelItems(itemList)

        # Check Symbol for Default Archive File
        # Find current archive file, and add a "check symbol" into column 0.
        # If not exist, set the first item as current archive file.
        current_archive_item = self.tree.findItems(ARCHIVE_FILE_NAME,
                                                   QtCore.Qt.MatchExactly, 1)
        # The return value of findItems() is a list, which contains all matched items.
        if len(current_archive_item) > 0:
            current_archive_item[0].setData(0, 0, "\u2713")
        else:
            first_item = self.tree.itemAt(0, 0) # First item
            self.tree.setCurrentItem(first_item)
            ARCHIVE_FILE_NAME = first_item.data(1, 0)
            first_item.setData(0, 0, "\u2713")
            config_file = config.ConfigFile()
            config_file.writeConfigFile()
            self.parent.status_current_archive.setText(ARCHIVE_FILE_NAME)

    def setAsDefault(self):
        global ARCHIVE_FILE_NAME, ARCHIVE_FILE_FULLNAME
        if self.tree.currentItem():
            filename = self.tree.currentItem().data(1, 0)
            ARCHIVE_FILE_NAME = filename
            ARCHIVE_FILE_FULLNAME = os.path.join(ARCHIVE_DIR, filename)
            self.parent.config.writeConfigFile()
            self.reloadArchiveFiles()
            self.parent.status_current_archive.setText(ARCHIVE_FILE_NAME)
            
    def new(self):
        filename, ok = QtGui.QInputDialog.getText(self,
                                                  self.tr("Create a new archive"),
                                                  self.tr("Please input a name for new archive file :"),
                                                  QtGui.QLineEdit.Normal,
                                                  self.userInput)
        if ok and filename != '':
            if filename in os.listdir(ARCHIVE_DIR):
                msg = QtGui.QMessageBox()
                msg.setText(self.tr("Filename has already existed, please retry."))
                msg.setIcon(QtGui.QMessageBox.Information)
                msg.exec_()
                self.userInput = filename
                self.new()
            else:
                open(os.path.join(ARCHIVE_DIR, filename), 'a').close()
                self.reloadArchiveFiles()
                self.userInput = ""
        else:
            self.userInput = ""

    def rename(self):
        global ARCHIVE_FILE_NAME
        if self.tree.currentItem() == None:
            return None
        oldFilename = self.tree.currentItem().data(1, 0)
        newFilename, ok = QtGui.QInputDialog.getText(self,
                                                     self.tr("Rename the archive file"),
                                                     self.tr("Please input a new name for this archive file :"),
                                                     QtGui.QLineEdit.Normal,
                                                     oldFilename)
        if ok and newFilename != '':
            if newFilename in os.listdir(ARCHIVE_DIR):
                msg = QtGui.QMessageBox()
                msg.setText(self.tr("Filename has already existed, please retry."))
                msg.setIcon(QtGui.QMessageBox.Information)
                msg.exec_()
                self.rename()
            else:
                os.rename(os.path.join(ARCHIVE_DIR, oldFilename),
                          os.path.join(ARCHIVE_DIR, newFilename))
                ARCHIVE_FILE_NAME = newFilename
                self.reloadArchiveFiles()

    def edit(self):
        io.FileIO().editWithSystemEditor(self.tree.currentItem().data(1, 0))
        self.reloadArchiveFiles()


    def merge(self):
        if len(self.tree.selectedItems()) <= 1:
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Information)
            msg.setText(self.tr("Please press Ctrl and click to select multiple items first."))
            msg.exec_()
        else:
            filenameList = []
            for item in self.tree.selectedItems():
                filenameList.append(item.data(1, 0))
                
            formatedFilenameList = ""
            for filename in filenameList:
                formatedFilenameList = formatedFilenameList + "<li><i>{0}</i></li>".format(filename)
                
            mergedFilename, ok = QtGui.QInputDialog.getText(self,
                                                         self.tr("Merge"),
                                                            self.tr(
"""You are about merging the following files:<br>
<ol>{0}</ol>
Please input new file name for merged file:
(You cannot use an existed file name)
""").format(formatedFilenameList),
                                                         QtGui.QLineEdit.Normal,
                                                         filenameList[0])
            # Merge file
            if ok and mergedFilename != '':
                if mergedFilename in os.listdir(ARCHIVE_DIR):
                    msg = QtGui.QMessageBox()
                    msg.setIcon(QtGui.QMessageBox.Information)
                    msg.setText(self.tr("Filename has existed, please input another one."))
                    msg.exec_()
                    self.merge()
                else:
                    with open(os.path.join(ARCHIVE_DIR, mergedFilename), 'a') as mergedFile:
                        for x in filenameList:
                            with open(os.path.join(ARCHIVE_DIR, x), 'r') as file:
                                fileContent = file.read()
                                mergedFile.write(fileContent)
                    self.reloadArchiveFiles()
                    msg = QtGui.QMessageBox()
                    msg.setIcon(QtGui.QMessageBox.Information)
                    msg.setText(self.tr("File merged!"))
                    msg.exec_()

    def removeDuplicated(self):
        selected_item = self.tree.currentItem()
        if selected_item == None:
            return None         # Jump out of function
        filename = selected_item.data(1, 0)
        reply = QtGui.QMessageBox.question(self, self.tr('Remove Duplicated Words'),
                                           self.tr(
"""This action will remove all duplicated words in <b>{0}</b>.<br>
This action cannot be undone, continue?""").format(filename),
                                           QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        
        if reply == QtGui.QMessageBox.No:
            return None         # Jump out of function
        seenWords = set()
        lineList = []
        newLinesList = []
        duplicatedCount = 0
        with open(os.path.join(ARCHIVE_DIR, filename), 'r') as file:
            linesList = file.readlines()
            for line in linesList:
                word = line.partition('\t')[0] # Get only word (get rid of count num)
                if word not in seenWords:
                    newLinesList.append(line)
                else:
                    duplicatedCount += 1
                seenWords.add(word)
        with open(os.path.join(ARCHIVE_DIR, filename), 'w') as file:
            file.writelines(newLinesList)
        self.reloadArchiveFiles()
        msg = QtGui.QMessageBox()
        msg.setWindowTitle(self.tr('Remove Duplicated Words'))
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText(self.tr('Done! {0} duplicated word removed.').format(duplicatedCount))
        msg.exec_()
            
    def delete(self):
        if len(os.listdir(ARCHIVE_DIR)) <= 1:
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Information)
            msg.setText(self.tr("You have to reserve at least one archive file."))
            msg.exec_()
        else:

            if self.tree.currentItem():
                filename = self.tree.currentItem().data(1, 0)
                reply = QtGui.QMessageBox.question(self, self.tr('Delete File'),
                                                   self.tr("""Are you sure to delete <b>{0}</b>?<br>
                                                   (This action cannot be undone!)""").format(filename),
                                                   QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
    
                if reply == QtGui.QMessageBox.Yes:
                    os.remove(os.path.join(ARCHIVE_DIR, self.tree.currentItem().data(1, 0)))
                    self.reloadArchiveFiles()

    def importToFlashcard(self):
        selectedItem = self.tree.currentItem()
        if selectedItem == None:
            return None         # Jump out of function
        filename = selectedItem.data(1, 0)
        words = str(selectedItem.data(2, 0))
        reply = QtGui.QMessageBox.question(self, self.tr('Message'),
             self.tr("Are you sure to import <b>{0} ({1} words)</b>?").format(filename, words),
             QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            
            self.parent.io.importArchivedFile(filename)
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Information)
            msg.setText(self.tr("Done! {0} words imported.").format(words))
            msg.exec_()
            self.parent.refresh() # parent should be main window
