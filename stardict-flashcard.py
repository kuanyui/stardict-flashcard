# -*- coding: utf-8 -*-
import sys, os, math, re, configparser, subprocess
from PyQt4 import QtCore, QtGui

ROOT = os.path.expanduser('~/.stardict-flashcard/')
CONFIG_PATH = os.path.join(ROOT, 'rc.ini')
ARCHIVE_DIR = os.path.join(ROOT, 'archive')

OPEN_FIRST_TIME_HELP = False

class ConfigFile():
    def __init__(self, parent=None):
        if not os.path.isdir(ROOT):
            os.makedirs(ROOT)
        if not os.path.isfile(CONFIG_PATH):
            global OPEN_FIRST_TIME_HELP
            OPEN_FIRST_TIME_HELP = True
            with open(CONFIG_PATH, 'w') as file:
                file.write('''[Path]
DictPath = ~/dic.txt
ArchiveFileName = default-archive

[Main]
MemorizedCount = 5

[Other]
FirstTimeHelp = True
''')
        # Config
        self.parser = configparser.ConfigParser()
        self.parser.optionxform = str # Preserve cases of keys.
        self.parser.read(CONFIG_PATH)
        
    def initializeGlobalVar(self):
        global DICT_PATH, ARCHIVE_FILE_NAME, ARCHIVE_FILE_FULLNAME, MEMORIZED_COUNT
        DICT_PATH             = os.path.expanduser(self.parser['Path']['DictPath'])
        ARCHIVE_FILE_NAME     = self.parser['Path']['ArchiveFileName']
        ARCHIVE_FILE_FULLNAME = os.path.join(ARCHIVE_DIR, ARCHIVE_FILE_NAME)
        MEMORIZED_COUNT       = int(self.parser['Main']['MemorizedCount'])
        # if Archive dir & file not exist, create
        if not os.path.isdir(ARCHIVE_DIR):
            os.makedirs(ARCHIVE_DIR)
        if not os.path.exists(ARCHIVE_FILE_FULLNAME):
            open(ARCHIVE_FILE_FULLNAME, 'a').close() # touch current archive file


    def writeConfigFile(self):
        self.parser['Path']['DictPath']           = DICT_PATH
        self.parser['Path']['ArchiveFileName']    = ARCHIVE_FILE_NAME
        self.parser['Main']['MemorizedCount']     = str(MEMORIZED_COUNT)
        with open(CONFIG_PATH, 'w') as file:
            self.parser.write(file)

class FileIO():
    def __init__(self, parent=None):
        self.linePattern=re.compile(r'([^\t]+)\t([0-9]+)\n')

    def initializeFile(self):
        '''Read dict file and add count numbers, and read into self.lineList,
        then parsed into self.wordList.'''
        with open(DICT_PATH, 'r') as file:
            lineList = file.readlines()
        # Check each line in dict file if count num exist. if not, add it.
        for index, line in enumerate(lineList):
            if not self.linePattern.match(line):
                lineList[index] = re.search('([^\t]+)\n', line).group(1) + '\t' + '0' + '\n'

        self.lineList = lineList     # lineList = ['噂\t2\n','納得\t0\n']
        self._writeLineListIntoFile()
        self.readFileIntoWordList()

    def _writeLineListIntoFile(self):
        with open(DICT_PATH, 'w') as file:
            file.writelines(self.lineList)

    def readFileIntoWordList(self):
        # read lines into a list [('噂', 2), ('納得', 0), ...]
        linePattern = self.linePattern
        self.wordList = []
        for x in self.lineList:
            match = linePattern.search(x)
            self.wordList.append((match.group(1), int(match.group(2))))

    def formatWordListAndWriteIntoFile(self):
        self.lineList = []
        for word, count in self.wordList:
            self.lineList.append('{0}\t{1}\n'.format(word, count))
        self._writeLineListIntoFile()

    def archiveWord(self, index):
        with open(ARCHIVE_FILE_FULLNAME, 'a') as file:
            file.write(self.wordList[index][0] + '\n')
        # Delete word from list (but not write list into dict file yet)
        del self.wordList[index]
        self.formatWordListAndWriteIntoFile()

    def removeWord(self, index):
        del self.wordList[index]
        self.formatWordListAndWriteIntoFile()

    def importArchivedFile(self, archiveFilename):
        with open(os.path.join(ARCHIVE_DIR, archiveFilename), 'r') as archiveFile:
            archive_content = archiveFile.read() # [FIXME] May I must to use self in here?
        with open(DICT_PATH, 'a') as dictFile:
            dictFile.write(archive_content)
        self.initializeFile()

    def archiveWholeDict(self, archiveFilename):
        with open(DICT_PATH, 'r') as file:
            wholeDictContent = file.read()
        with open(os.path.join(ARCHIVE_DIR, archiveFilename), 'w') as file:
            file.write(wholeDictContent)
        # Clear dict file.
        self.wordList = []
        self.formatWordListAndWriteIntoFile()
        
    def editWithSystemEditor(self, filePath):
        editor = os.getenv('EDITOR')
        if editor == '':
            editor = 'vi'
        subprocess.call([editor,
                         os.path.join(ARCHIVE_DIR, filePath)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.config = ConfigFile()
        self.config.initializeGlobalVar()
        self._createActions()
        self._createMenus()
        self.setWindowTitle("Flashcard")

        # StatusBar
        self.statusBar()        # So Easy!

        self.vertical_spliter = QtGui.QFrame()
        self.vertical_spliter.setGeometry(20,20,50,20)
        self.vertical_spliter.setFrameShape(QtGui.QFrame.VLine)
        self.vertical_spliter.setFrameShadow(QtGui.QFrame.Sunken)
        self.status_index = QtGui.QLabel()
        self.status_current_archive = QtGui.QLabel()
        self.statusBar().insertPermanentWidget(0, self.status_current_archive)
        self.statusBar().insertPermanentWidget(1, self.vertical_spliter)
        self.statusBar().insertPermanentWidget(2, self.status_index)
        self.status_current_archive.setText(ARCHIVE_FILE_NAME)

        # Layout
        self.word_label = QtGui.QLabel()
        self.word_label.setAlignment(QtCore.Qt.AlignCenter)
        self.word_label.setStyleSheet("font-size:30px;")
        
        self.description_browser = QtGui.QTextBrowser()
        self.description_browser.setStyleSheet("font-size:12pt;")
        central_widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.word_label)
        layout.addWidget(self.description_browser)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.resize(600, 500)
        
        # Centering window
        self.move(QtGui.QDesktopWidget().availableGeometry().center() - self.frameGeometry().center())
        
        # Key Binding
        QtGui.QShortcut(QtGui.QKeySequence('Space'), self, self.goOn)
        QtGui.QShortcut(QtGui.QKeySequence('Return'), self, self.bingo)
        
        # Initilize word list
        self.io = FileIO()
        self.io.initializeFile()

        self.index = 0
        self.refresh()
        self.show()
        if OPEN_FIRST_TIME_HELP == True:
            self.openHelpWindow()

    def refresh(self):
        if len(self.io.wordList) == 0:
            self.allWordsFinished()
            return None         # jump out of function
        else:
            self.archiveDictAct.setEnabled(True)
        if self.io.wordList[self.index][1] >= MEMORIZED_COUNT:
            self.archiveCurrentWord()
        else:
            self.word = self.io.wordList[self.index][0]
            self.word_label.setText(self.word)
            cmd = subprocess.Popen(['sdcv', self.word], stdout=subprocess.PIPE)
            output = cmd.stdout.read()
            output = output.decode('utf-8')
            formattedOut = re.sub(r'(.+)\n', r'\1<br>\n', output)
            formattedOut = re.sub(r'-->(.+)<br>\n-->(.+)<br>',
                                  r'''
<h5 style='background-color:#184880; color:#88bbff; margin:0;'>\1</h5>
<h3 style='background-color:#184880; color:#fff; margin:0;'>\2</h3>
                                  '''
                                  , formattedOut)
            # print(formattedOut)
            self.formattedOut = formattedOut
            self.description_browser.setText("")
            self.now = 'unanswered'
        self.refreshStatusBar()

    def refreshStatusBar(self):
        wordsTotal = len(self.io.wordList)
        index = self.index + 1
        if wordsTotal > 1:
            self.status_index.setText("{0}/{1}".format(index, wordsTotal))

    def showDescription(self):
        self.description_browser.setHtml(self.formattedOut)
        self.now = 'answered'

    def allWordsFinished(self):
        self.now = None
        self.archiveDictAct.setEnabled(False)
        self.word_label.setText("Cleared!")
        self.description_browser.setText('''No word remains in dict file now.
Now you can add new word via StarDict (Alt + e).
You also can import an archived file to start another reviewing.''')
        
    def correctIndex(self):
        '''If no word remains in wordList, call allWordsFinished().
        If index is out of list, set it to 0.
        Finally, refresh()'''
        if len(self.io.wordList) == 0:
            self.allWordsFinished()
        else:
            if self.index >= len(self.io.wordList):
                self.index = 0
            self.refresh()

    def archiveCurrentWord(self):
        self.io.archiveWord(self.index)
        self.correctIndex()
        
    def incfIndex(self):
        '''next word, but without +1 count num'''
        self.index += 1
        self.correctIndex()

    def bingo(self):
        if self.now == 'unanswered':
            None
        else:
            self.io.wordList[self.index] = (self.io.wordList[self.index][0],
                                         self.io.wordList[self.index][1] + 1)
            if self.io.wordList[self.index][1] >= MEMORIZED_COUNT:
                self.archiveCurrentWord()
            else:
                self.incfIndex()
            self.io.formatWordListAndWriteIntoFile()
            self.statusBar().showMessage("Bingo!")
            QtCore.QTimer.singleShot(1000, lambda: self.statusBar().clearMessage())

    def goOn(self):
        '''After press space, decide to bingo() or just incfIndex()'''
        if self.now == 'unanswered':
            self.showDescription()
        elif self.now == 'answered':
            self.incfIndex()
         

    def closeEvent(self, event):
        self.io.formatWordListAndWriteIntoFile()
        #reply = QtGui.QMessageBox.question(self, 'Message',
        #    "Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        #if reply == QtGui.QMessageBox.Yes:
        #    self.io.formatWordListAndWriteIntoFile()
        #    event.accept()
        #else:
        #    event.ignore()

    def archiveDict(self):
        '''Archive all words in dict.'''
        self.archive_list = ArchiveList(self)
        self.archive_list.show()
    
    # Windows
    def openConfigWindow(self):
        self.config_window=ConfigWindow(self)
        self.config_window.show()

    def openArchiveFileManager(self):
        self.archive_file_manager = ArchiveFileManager(self)
        self.archive_file_manager.show()

    def openHelpWindow(self):
        self.help_window = HelpWindow(self)

    def openArchiveDirectory(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(ARCHIVE_DIR))

    def openDictFile(self):
        FileIO().editWithSystemEditor(DICT_PATH)
        self.io.initializeFile()
        self.refresh()

    def _createActions(self):
        self.configAct = QtGui.QAction(
            "&Configuration", self,
            shortcut = QtGui.QKeySequence("Ctrl+P"),
            statusTip = "Open configuration window.",
            triggered = self.openConfigWindow
        )
        self.openArchiveFileManagerAct = QtGui.QAction(
            "&Manage", self,
            shortcut = QtGui.QKeySequence("Ctrl+M"),
            statusTip = "Create, import, rename, edit, delete archive file.",
            triggered = self.openArchiveFileManager
        )
        self.openHelpWindowAct = QtGui.QAction(
            "&Help", self,
            shortcut = QtGui.QKeySequence.HelpContents,
            statusTip = "Open help window.",
            triggered = self.openHelpWindow
        )
        self.archiveDictAct = QtGui.QAction(
            "&Archive Whole Dict", self,
            statusTip = "Archive all words in dict, then you can import the other archive file.",
            triggered = self.archiveDict
        )
        self.openDictFileAct = QtGui.QAction(
            "&Open Dict File", self,
            statusTip = "Open Dict file with default editor on system.",
            triggered = self.openDictFile
        )
        self.openArchiveDirectoryAct = QtGui.QAction(
            "&Open Archive Directory", self,
            statusTip = "Open archive directory with file manager.",
            triggered = self.openArchiveDirectory
        )

    def _createMenus(self):
        self.menu_bar = self.menuBar().addMenu("&File")
        self.menu_bar.addAction(self.openDictFileAct)
        self.menu_bar.addAction(self.configAct)
        self.menu_bar = self.menuBar().addMenu("&Archive")
        self.menu_bar.addAction(self.openArchiveFileManagerAct)
        self.menu_bar.addAction(self.archiveDictAct)
        self.menu_bar.addAction(self.openArchiveDirectoryAct)
        self.menu_bar = self.menuBar().addMenu("&Help")
        self.menu_bar.addAction(self.openHelpWindowAct)
        

class ArchiveList(QtGui.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.line_edit = QtGui.QLineEdit()
        list_widget = QtGui.QListWidget()
        for filename in os.listdir(ARCHIVE_DIR):
            list_widget.addItem(filename)

        list_widget.itemClicked.connect(self.setLineEditText)

        button_box = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.apply)
        button_box.rejected.connect(self.close)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel("Please input filename for archiving the dict,\n"
                                      "or select an existed one:"))
        layout.addWidget(self.line_edit)
        layout.addWidget(list_widget)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.setWindowTitle("Input archive file")
        
    def setLineEditText(self, item):
        self.line_edit.setText(item.text())

    def apply(self):
        filename = self.line_edit.text()
        if filename in os.listdir(ARCHIVE_DIR):
            reply = QtGui.QMessageBox.question(
                self, 'Message',
                "Are you sure to overwrite file <b>{0}</b>?".format(filename),
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.parent.io.archiveWholeDict(filename)
                self.parent.allWordsFinished()
                self.parent.openArchiveFileManager()
                self.close()
        

class ConfigWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.line_dict_path = QtGui.QLineEdit()
        self.line_dict_path.setText(DICT_PATH)
        button_dict_path = QtGui.QPushButton("Browse Dict...")
        button_dict_path.clicked.connect(self.browseDictPath)
        
        self.spin_box = QtGui.QSpinBox()
        self.spin_box.setRange(1, 100)
        self.spin_box.setValue(MEMORIZED_COUNT)

        button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.applyAndWriteConfigFile)
        button_box.rejected.connect(self.close)
        
        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel("Dict file path:"), 0, 0)
        layout.addWidget(self.line_dict_path, 0, 1)
        layout.addWidget(button_dict_path, 0, 2)
        layout.addWidget(QtGui.QLabel("Memorized count:"), 1, 0)
        layout.addWidget(self.spin_box, 1, 1, 1, 1)
        layout.addWidget(button_box, 2, 1, 1, 2)

        self.setLayout(layout)
        self.adjustSize()
        self.resize(700, self.height())

    def browseDictPath(self):
        path = QtGui.QFileDialog.getOpenFileName(self, "Select Dictionary File Path",
                                                 os.path.expanduser("~/"))
        if path:
            self.line_dict_path.setText(path)

    def applyAndWriteConfigFile(self):
        global DICT_PATH, MEMORIZED_COUNT
        DICT_PATH             = str(self.line_dict_path.text())
        MEMORIZED_COUNT       = int(self.spin_box.value())

        self.parent.config.writeConfigFile()
        self.close()

class ArchiveFileManager(QtGui.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.tree = QtGui.QTreeWidget()
        self.tree.setHeaderLabels(["Current", "Filename", "Words"])

        self.reloadArchiveFiles()
        
        self.tree.setColumnWidth(0, 24)
        self.tree.setColumnWidth(1, 300)
        self.tree.setColumnWidth(2, 24)
        self.tree.setRootIsDecorated(False)

        self.tree.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tree.itemClicked.connect(self.updateButtonState)
        
        # buttons
        self.b_new              = QtGui.QPushButton("&New")
        self.b_new.clicked.connect(self.new)
        self.b_rename           = QtGui.QPushButton("&Rename")
        self.b_rename.clicked.connect(self.rename)
        self.b_edit             = QtGui.QPushButton("&Edit")
        self.b_edit.clicked.connect(self.edit)
        self.b_merge            = QtGui.QPushButton("&Merge")
        self.b_merge.clicked.connect(self.merge)
        self.b_delete           = QtGui.QPushButton("&Delete")
        self.b_delete.clicked.connect(self.delete)
        self.b_remove_duplicate = QtGui.QPushButton("Remove Duplicated")
        self.b_remove_duplicate.clicked.connect(self.removeDuplicated)
        self.b_import_to_dict   = QtGui.QPushButton("&Import to Dict")
        self.b_import_to_dict.clicked.connect(self.importToDict)
        self.b_set_as_default   = QtGui.QPushButton("&Set As Default\nArchive File")
        self.b_set_as_default.clicked.connect(self.setAsDefault)
        close                   = QtGui.QPushButton("&Close")
        close.clicked.connect(self.close)

        
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
            config_file = ConfigFile()
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
                                                  "Create a new archive",
                                                  "Please input a name for new archive file :",
                                                  QtGui.QLineEdit.Normal,
                                                  self.userInput)
        if ok and filename != '':
            if filename in os.listdir(ARCHIVE_DIR):
                msg = QtGui.QMessageBox()
                msg.setText("Filename has already existed, please retry.")
                msg.show()
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
        if self.tree.currentItem() == None:
            return None
        oldFilename = self.tree.currentItem().data(1, 0)
        newFilename, ok = QtGui.QInputDialog.getText(self,
                                                     "Rename the archive file",
                                                     "Please input a new name for this archive file :",
                                                     QtGui.QLineEdit.Normal,
                                                     oldFilename)
        if ok and newFilename != '':
            if newFilename in os.listdir(ARCHIVE_DIR):
                msg = QtGui.QMessageBox()
                msg.setText("Filename has already existed, please retry.")
                msg.show()
                msg.exec_()
                self.rename()
            else:
                os.rename(os.path.join(ARCHIVE_DIR, oldFilename),
                          os.path.join(ARCHIVE_DIR, newFilename))
                self.reloadArchiveFiles()

    def edit(self):
        FileIO().editWithSystemEditor(self.tree.currentItem().data(1, 0))
        self.reloadArchiveFiles()


    def merge(self):
        if len(self.tree.selectedItems()) <= 1:
            msg = QtGui.QMessageBox()
            msg.setText("Please press Ctrl and click to select multiple items first.")
            msg.exec_()
        else:
            filenameList = []
            for item in self.tree.selectedItems():
                filenameList.append(item.data(1, 0))
                
            formatedFilenameList = ""
            for filename in filenameList:
                formatedFilenameList = formatedFilenameList + "<li>{0}</li>".format(filename)
                
            mergedFilename, ok = QtGui.QInputDialog.getText(self,
                                                         "Merge",
"""You are about merging the following files:<br>
<ol>{0}</ol>
Please input new file name for merged file:
(You cannot use an existed file name)
""".format(formatedFilenameList),
                                                         QtGui.QLineEdit.Normal,
                                                         filenameList[0])
            # Merge file
            if ok and mergedFilename != '':
                if mergedFilename in os.listdir(ARCHIVE_DIR):
                    msg = QtGui.QMessageBox()
                    msg.setText("Filename has existed, please input another one.")
                    msg.exec_()
                    self.merge()
                else:
                    with open(os.path.join(ARCHIVE_DIR, mergedFilename), 'a') as mergedFile:
                        for x in filenameList:
                            with open(os.path.join(ARCHIVE_DIR, x), 'r') as file:
                                fileContent = file.read()
                                mergedFile.write(fileContent)
                    msg = QtGui.QMessageBox()
                    msg.setText("File merged!")
                    msg.exec_()
                    self.reloadArchiveFiles()

    def removeDuplicated(self):
        None
        
    def delete(self):
        if len(os.listdir(ARCHIVE_DIR)) <= 1:
            msg = QtGui.QMessageBox()
            msg.setText("You have to reserve at least one archive file.")
            msg.exec_()
        else:

            if self.tree.currentItem():
                filename = self.tree.currentItem().data(1, 0)
                reply = QtGui.QMessageBox.question(self, 'Message',
                                                   """Are you sure to delete <b>{0}</b>?<br>
                                                   (This action cannot be undone!)""".format(filename),
                                                   QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
    
                if reply == QtGui.QMessageBox.Yes:
                    os.remove(os.path.join(ARCHIVE_DIR, self.tree.currentItem().data(1, 0)))
                    self.reloadArchiveFiles()

    def importToDict(self):
        selectedItem = self.tree.currentItem()
        if selectedItem == None:
            return None         # Jump out of function
        filename = selectedItem.data(1, 0)
        words = str(selectedItem.data(2, 0))
        reply = QtGui.QMessageBox.question(self, 'Message',
             "Are you sure to import <b>{0} ({1} words)</b>?".format(filename, words),
             QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            
            self.parent.io.importArchivedFile(filename)
            msg = QtGui.QMessageBox()
            msg.setText("Done! {0} words imported.".format(words))
            msg.exec_()
            self.parent.refresh() # parent should be main window
        

class HelpWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        text_browser = QtGui.QTextBrowser()
        text_browser.setStyleSheet("font-size:12px;")
        text_browser.setHtml(
'''
<h1>Welcome to <i>Stardict Flashcard</i>!</h1>
You can add new word into flashcard via Stardict with <b style='background-color: #ddd; color: #333;'>Alt+e</b>.<br>
(The words will be added into <i>~/dic.txt</i> by default)<by>
Then open <i>Stardict Flashcard</i>:
<ol>
<li>Press <b>Space</b> to display answer.</li>
<li>Then press <b>Enter</b> means you can recite this word.</li>
<li>Or if you can't think of the word and recite it, press <b>Space</b> to go on instead.</li>
<li>After a word can be recited up to 5 times, the word will be archived into current archive file automatically.<li>
</ol>

After finishing all words, you still can review them again by <b>importing archive file</b>.<br>
You can manage archive file in <i>File/Manage Archive File</i>.
''')
        button = QtGui.QPushButton("&Ok")
        button.clicked.connect(self.close)
        button.setDefault(True)
        button.setAutoDefault(True)
        button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        button_box.accepted.connect(self.close)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(text_browser)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)
        self.resize(600, 300)
        # make main window uncontrollable.
        self.setWindowModality(QtCore.Qt.WindowModal)
        
        self.show()
        

        
app = QtGui.QApplication(sys.argv)


main_window = MainWindow()

app.exec_()
