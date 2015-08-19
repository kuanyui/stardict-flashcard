#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, math, re, configparser, subprocess
from PyQt4 import QtCore, QtGui

from .tooltip import *
from .config_file import *
from .io import *
from .archive_manager import *
from .help_window import *
from .config_window import *

def sdcv(word):
    cmd = subprocess.Popen(['sdcv', '-n', word], stdout=subprocess.PIPE)
    output = cmd.stdout.read()
    output = output.decode('utf-8')
    formattedOut = re.sub(r'(.+)\n', r'\1<br>\n', output)
    formattedOut = re.sub(r'-->(.+)<br>\n-->(.+)<br>',
                          r'''
<h5 style='background-color:#666; color:#88bbff; margin:0;'>\1</h5>
<h3 style='background-color:#666; color:#fff; margin:0;'>\2</h3>
                                  '''
                          , formattedOut)
            # print(formattedOut)
    return formattedOut
        

class IconButton(QtGui.QPushButton):
    def __init__(self, align, iconFilename, text, function):
        super().__init__()
        self.setIcon(QtGui.QIcon(ACT_ICON_DIR + iconFilename))
        self.setText(text)
        if align == 'l':
            self.setStyleSheet("text-align:left")
        elif align == 'r':
            self.setStyleSheet("text-align:right")
        self.clicked.connect(function)
        
class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.config = ConfigFile(self)
        self._createActions()
        self._createMenus()
        self.setWindowTitle("Stardict Flashcard")

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

        self.description_browser = QtGui.QTextBrowser(self)
        self.description_browser.setStyleSheet("font-size:12pt;")
        self.description_browser.selectionChanged.connect(self.lookupSelection)

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

        if REMEMBER_INDEX >= 0:
            self.index = REMEMBER_INDEX
        else:
            self.index = 0
            
        self.refresh()
        self.show()
        if OPEN_FIRST_TIME_HELP == True:
            self.openHelpWindow()

        # Lookup tooltip
        self.lookup_tooltip = LookupTooltip(self)
        self.__selectedText = ""                        
            
    def refresh(self):
        self.io.checkIfFileUpdated()
        word, count = self.io.getItem(self.index)
        if self.io.length() == 0:
            self.allWordsFinished()
            return None         # jump out of function
        else:
            self.archiveFlashcardAct.setEnabled(True)
        if count >= MEMORIZED_COUNT:
            self.archiveCurrentWord()
        else:
            self.word = word
            self.word_label.setText(self.word)
            self.formattedDescription = sdcv(self.word)
            self.description_browser.setText("")
            self.now = 'unanswered'
        self.refreshStatusBar()

    def lookupSelection(self):
        cursor = self.description_browser.textCursor()
        if app.mouseButtons() == QtCore.Qt.NoButton:
            if cursor.hasSelection() and cursor.selectedText() != self.__selectedText:
                self.__selectedText = cursor.selectedText()
                # self is Important! or cannot get global position of
                # tooltip. I don't know why.
                self.lookup_tooltip.lookupAndShow(self.__selectedText)

    def refreshStatusBar(self):
        wordsTotal = self.io.length()
        index = self.index + 1
        if wordsTotal > 1:
            self.status_index.setText("{0}/{1}".format(index, wordsTotal))

    def showDescription(self):
        self.description_browser.setHtml(self.formattedDescription)
        self.now = 'answered'

    def allWordsFinished(self):
        self.now = None
        self.archiveFlashcardAct.setEnabled(False)
        self.word_label.setText("Cleared!")
        self.description_browser.setText(self.tr('''No word remains in Flashcard file now.
Now you can add new word via StarDict (Alt + e).
You also can import an archived file to start another reviewing.'''))
        
    def correctIndex(self):
        '''If no word remains in wordList, call allWordsFinished().
        If index is out of list, set it to 0.
        Finally, refresh()'''
        if self.io.length() == 0:
            self.allWordsFinished()
        else:
            if self.index >= self.io.length():
                self.index = 0
            elif self.index < 0:
                self.index = self.io.length() - 1
                
            self.refresh()

    # [FIXME] index and the whole function should be totally in IO
    def archiveCurrentWord(self):
        self.io.archiveWord(self.index)
        self.correctIndex()

    def removeCurrentWord(self):
        reply = QtGui.QMessageBox.question(
            self, self.tr('Message'),
            self.tr("Are you exactly sure to remove this word?"),
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.io.checkIfFileUpdated()
            self.io.removeWord(self.index)
            self.correctIndex()
            self.statusBar().showMessage("Word removed.")
            QtCore.QTimer.singleShot(1000, lambda: self.statusBar().clearMessage())
        
    def incfIndex(self):
        '''next word, but without +1 count num'''
        self.index += 1
        self.correctIndex()

    def bingo(self):
        if self.now == 'unanswered':
            None
        else:
            count = self.io.increaseItemCount(self.index)
            if count >= MEMORIZED_COUNT:
                self.archiveCurrentWord()
            else:
                self.incfIndex()
            self.statusBar().showMessage("Bingo!")
            QtCore.QTimer.singleShot(1000, lambda: self.statusBar().clearMessage())

    def goOn(self):
        '''After press space, decide to bingo() or just incfIndex()'''
        if self.now == 'unanswered':
            self.showDescription()
        elif self.now == 'answered':
            self.incfIndex()

    def back(self):
        self.index -= 1
        self.correctIndex()

    def setCurrentItemCountToZero(self):
        self.io.setItemCountToZero(self.index)
        self.statusBar().showMessage("Done; the count of this word has been reset to 0.")
        QtCore.QTimer.singleShot(3000, lambda: self.statusBar().clearMessage())

    def closeEvent(self, event):
        global REMEMBER_INDEX
        self.io.checkIfFileUpdated()
        self.io.writeLineListIntoFile()
        if REMEMBER_INDEX >= 0:
            REMEMBER_INDEX = int(self.index)
        self.config.writeConfigFile()

    def archiveFlashcard(self):
        '''Archive all words in Flashcard.'''
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

    def openFlashcardFile(self):
        io.FileIO().editWithSystemEditor(FLASHCARD_PATH)
        self.io.initializeFile()
        self.refresh()

    def openJumpToNumberWindow(self):
        self.jump_to_number_window = JumpToNumberWindow(self)

    def _createActions(self):
        self.configAct = QtGui.QAction(
            QtGui.QIcon(ACT_ICON_DIR + "config.png"),
            self.tr("&Configuration"), self,
            shortcut = QtGui.QKeySequence("Ctrl+P"),
            statusTip = self.tr("Open configuration window."),
            triggered = self.openConfigWindow
        )
        self.openArchiveFileManagerAct = QtGui.QAction(
            QtGui.QIcon(ACT_ICON_DIR + "star.png"),
            self.tr("&Manage"), self,
            shortcut = QtGui.QKeySequence("Ctrl+M"),
            statusTip = self.tr("Create, import, rename, edit, delete archive file."),
            triggered = self.openArchiveFileManager
        )
        self.openHelpWindowAct = QtGui.QAction(
            QtGui.QIcon(ACT_ICON_DIR + "help.png"),
            self.tr("&Help"), self,
            shortcut = QtGui.QKeySequence.HelpContents,
            statusTip = self.tr("Open help window."),
            triggered = self.openHelpWindow
        )
        self.archiveFlashcardAct = QtGui.QAction(
            QtGui.QIcon(ACT_ICON_DIR + "archive.png"),
            self.tr("&Archive Whole Flashcard"), self,
            statusTip = self.tr("Archive all words in Flashcard, then you can import the other archive file."),
            triggered = self.archiveFlashcard
        )
        self.openFlashcardFileAct = QtGui.QAction(
            QtGui.QIcon(ACT_ICON_DIR + "edit.png"),
            self.tr("&Open Flashcard File"), self,
            statusTip = self.tr("Open Flashcard file with system default editor."),
            triggered = self.openFlashcardFile
        )
        self.openArchiveDirectoryAct = QtGui.QAction(
            QtGui.QIcon(ACT_ICON_DIR + "browse.png"),
            self.tr("&Open Archive Directory"), self,
            statusTip = self.tr("Open archive directory with external file manager."),
            triggered = self.openArchiveDirectory
        )
        self.openJumpToNumberWindowAct = QtGui.QAction(
            QtGui.QIcon(ACT_ICON_DIR + "jump.png"),
            self.tr("&Jump To Number"), self,
            shortcut = QtGui.QKeySequence("J"),
            statusTip = self.tr("Jump to number directly."),
            triggered = self.openJumpToNumberWindow
        )
        self.removeCurrentWordAct = QtGui.QAction(
            QtGui.QIcon(ACT_ICON_DIR + "remove.png"),
            self.tr("&Remove Current Word"), self,
            shortcut = QtGui.QKeySequence("Delete"),
            statusTip = self.tr("Remove current word directly."),
            triggered = self.removeCurrentWord
        )
        self.setCurrentItemCountToZeroAct = QtGui.QAction(
            QtGui.QIcon(ACT_ICON_DIR + "reset.png"),
            self.tr("Reset &Count of This Word"), self,
            shortcut = QtGui.QKeySequence("0"),
            statusTip = self.tr("Reset count of this word to zero."),
            triggered = self.setCurrentItemCountToZero
        )
        self.backAct = QtGui.QAction(
            QtGui.QIcon(ACT_ICON_DIR + "back.png"),
            self.tr("&Previous Word"), self,
            shortcut = QtGui.QKeySequence("Backspace"),
            statusTip = self.tr("Go back to previous word."),
            triggered = self.back
        )
        

    def _createMenus(self):
        self.menu_bar = self.menuBar().addMenu(self.tr("&File"))
        self.menu_bar.addAction(self.openFlashcardFileAct)
        self.menu_bar.addAction(self.configAct)
        self.menu_bar = self.menuBar().addMenu(self.tr("&Word"))
        self.menu_bar.addAction(self.backAct)
        self.menu_bar.addAction(self.openJumpToNumberWindowAct)
        self.menu_bar.addSeparator()
        self.menu_bar.addAction(self.setCurrentItemCountToZeroAct)
        self.menu_bar.addAction(self.removeCurrentWordAct)
        self.menu_bar = self.menuBar().addMenu(self.tr("&Archive"))
        self.menu_bar.addAction(self.openArchiveFileManagerAct)
        self.menu_bar.addAction(self.archiveFlashcardAct)
        self.menu_bar.addAction(self.openArchiveDirectoryAct)
        self.menu_bar = self.menuBar().addMenu(self.tr("&Help"))
        self.menu_bar.addAction(self.openHelpWindowAct)

class JumpToNumberWindow(QtGui.QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(self.tr("Jump to..."))

        maxRange = parent.io.length()
        self.spin_box = QtGui.QSpinBox()
        self.spin_box.setRange(1, maxRange)
        
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(1, maxRange)

        self.spin_box.valueChanged.connect(self.slider.setValue)
        self.slider.valueChanged.connect(self.spin_box.setValue)
        
        button_box = QtGui.QDialogButtonBox(
        QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.apply)
        button_box.rejected.connect(self.close)

        # Layout
        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel(self.tr("Input Number:")), 0, 0)
        layout.addWidget(self.spin_box, 0, 1)
        layout.addWidget(self.slider, 1, 0, 1, 2)
        layout.addWidget(button_box, 2, 0, 1, 2)

        self.setLayout(layout)
        self.show()
    
    def apply(self):
        self.parent.index = self.spin_box.value() - 1
        self.parent.refresh()
        self.close()

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
        layout.addWidget(QtGui.QLabel(self.tr("Please input filename for archiving Flashcard,\nor select an existed one:")))
        layout.addWidget(self.line_edit)
        layout.addWidget(list_widget)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.setWindowTitle(self.tr("Input archive file"))
        
    def setLineEditText(self, item):
        self.line_edit.setText(item.text())

    def apply(self):
        filename = self.line_edit.text()
        if filename in os.listdir(ARCHIVE_DIR):
            reply = QtGui.QMessageBox.question(
                self, self.tr('Message'),
                self.tr("Are you sure to overwrite file <b>{0}</b>?").format(filename),
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.parent.io.archiveWholeFlashcard(filename)
                self.parent.allWordsFinished()
                self.parent.openArchiveFileManager()
                self.close()

