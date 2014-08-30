# -*- coding: utf-8 -*-
import sys, os, math, re, configparser, subprocess
from PyQt4 import QtCore, QtGui

ROOT = os.path.expanduser('~/.stardict-flashcard/')
CONFIG_PATH = os.path.join(ROOT, 'rc.ini')
ARCHIVE_DIR = os.path.join(ROOT, 'archive')

class ConfigFile():
    def __init__(self, parent=None):
        if not os.path.isdir(ROOT):
            os.makedirs(ROOT)
        if not os.path.isfile(CONFIG_PATH):
            with open(CONFIG_PATH, 'w') as file:
                file.write('''[Path]
DictPath = ~/dic.txt
ArchiveFileName = default-archive

[Main]
MemorizedCount = 5
''')
        # Config
        self.parser = configparser.ConfigParser()
        self.parser.optionxform = str # Preserve cases of keys.
        self.parser.read(CONFIG_PATH)
        global DICT_PATH, ARCHIVE_FILE_NAME, ARCHIVE_FILE_FULLNAME, MEMORIZED_COUNT
        DICT_PATH             = os.path.expanduser(self.parser['Path']['DictPath'])
        ARCHIVE_FILE_NAME     = self.parser['Path']['ArchiveFileName']
        ARCHIVE_FILE_FULLNAME = os.path.join(ARCHIVE_DIR, ARCHIVE_FILE_NAME)
        MEMORIZED_COUNT       = int(self.parser['Main']['MemorizedCount'])
        
        # Archive
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
        with open(DICT_PATH, 'r') as file:
            lineList = file.readlines()
        # Check each line in dict file if count num exist. if not, add it.
        for index, line in enumerate(lineList):
            if not self.linePattern.match(line):
                lineList[index] = re.search('([^\t]+)\n', line).group(1) + '\t' + '0' + '\n'

        self.lineList = lineList     # lineList = ['噂\t2\n','納得\t0\n']
        self.writeListIntoFile()
        self.readFileIntoList()

    def writeListIntoFile(self):
        with open(DICT_PATH, 'w') as file:
            file.writelines(self.lineList)

    def readFileIntoList(self):
        # read lines into a list [('噂', 2), ('納得', 0), ...]
        linePattern = self.linePattern
        self.wordList = []
        for x in self.lineList:
            match = linePattern.search(x)
            self.wordList.append((match.group(1), match.group(2)))
        print(self.wordList)

    def formatListAndWriteIntoFile(self):
        self.lineList = []
        for word, count in self.wordList:
            self.lineList.append('{0}\t{1}\n'.format(word, count))
        self.writeListIntoFile()

    def archiveWord(self, index):
        with open(ARCHIVE_FILE_FULLNAME, 'a') as file:
            file.write(self.wordList[index][0] + '\n')
        # Delete word from list (but not write list into file yet)
        del self.wordList[index]

    def importArchivedFile(self, archiveFilePath):
        with open(archiveFilePath, 'r') as file:
            self.archive_content = file.read() # [FIXME] May I must to use self in here?

        with open(DICT_PATH, 'a') as file:
            file.write(self.archive_content)

        self.archive_content = ''
        self.initializeFile()

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.io = FileIO()
        self.config = ConfigFile()
        self._createActions()
        self._createMenus()
        self.setWindowTitle("Flashcard")

        # Layout
        self.word_label = QtGui.QLabel()
        self.word_label.setAlignment(QtCore.Qt.AlignCenter)
        self.word_label.setStyleSheet("font-size:30px;")
        
        self.description_browser = QtGui.QTextBrowser()
        central_widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.word_label)
        layout.addWidget(self.description_browser)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Initilize word list
        self.io.initializeFile()
        self.wordList = self.io.wordList
        
        self.index = 0
        self.refresh()


    def refresh(self):
        self.word = self.wordList[self.index][0]
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
        formattedOut = re.sub(r'', r'', formattedOut)
        print(formattedOut)
        self.description = formattedOut
        self.showDescription()

    def showDescription(self):
        self.description_browser.setHtml(self.description)

        
    def configWindow(self):
        self.config_window=ConfigWindow(self)
        self.config_window.show()

    def importArchivedFile(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                     os.path.expanduser('~/stardict-flashcard/archive'))
        print(filename)
        # self.io.importArchivedFile(filename)
    def _createActions(self):
        self.configAct = QtGui.QAction(
            "&Configuration", self,
            shortcut = QtGui.QKeySequence.New,
            statusTip = "Open configuration window.",
            triggered = self.configWindow
        )
        self.importArchivedFileAct = QtGui.QAction(
            "&Import Archived File", self,
            shortcut = QtGui.QKeySequence.Open,
            statusTip = "Import archived file into dictionary list",
            triggered = self.importArchivedFile
        )
        

    def _createMenus(self):
        self.dict_menu = self.menuBar().addMenu("&File")
        self.dict_menu.addAction(self.importArchivedFileAct)
        self.dict_menu.addAction(self.configAct)
        

class ConfigWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.line_dict_path = QtGui.QLineEdit()
        self.line_dict_path.setText(DICT_PATH)
        button_dict_path = QtGui.QPushButton("Browse Dict...")
        button_dict_path.clicked.connect(self.browseDictPath)
        
        self.line_archive_path = QtGui.QLineEdit()
        self.line_archive_path.setText(ARCHIVE_FILE_FULLNAME)
        button_archive_path = QtGui.QPushButton("Browse Archive...")
        button_archive_path.clicked.connect(self.browseArchivePath)

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
        layout.addWidget(QtGui.QLabel("Current archive file path:"), 1, 0)
        layout.addWidget(self.line_archive_path, 1, 1)
        layout.addWidget(button_archive_path, 1, 2)
        layout.addWidget(QtGui.QLabel("Word count:"), 2, 0)
        layout.addWidget(self.spin_box, 2, 1, 1, 3)
        layout.addWidget(button_box, 3, 2, 1, 2)

        self.setLayout(layout)
        self.adjustSize()
        self.resize(700, self.height())

    def browseDictPath(self):
        path = QtGui.QFileDialog.getOpenFileName(self, "Select Dictionary File Path",
                                                 os.path.expanduser("~/"))
        if path:
            self.line_dict_path.setText(path)

    def browseArchivePath(self):
        path = QtGui.QFileDialog.getOpenFileName(self, "Select Archive File Path",
                                                 ARCHIVE_DIR)
        if path:
            self.line_archive_path.setText(path)

    def applyAndWriteConfigFile(self):
        global DICT_PATH, ARCHIVE_FILE_NAME, ARCHIVE_FILE_FULLNAME, MEMORIZED_COUNT
        DICT_PATH             = str(self.line_dict_path.text())
        ARCHIVE_FILE_FULLNAME = str(self.line_archive_path.text())
        ARCHIVE_FILE_NAME     = os.path.basename(ARCHIVE_FILE_FULLNAME)
        MEMORIZED_COUNT       = int(self.spin_box.value())

        self.parent.config.writeConfigFile()
        self.close()
    
        
app = QtGui.QApplication(sys.argv)

# t = FileIO().initializeFile()
main_window = MainWindow()
main_window.show()

app.exec_()
