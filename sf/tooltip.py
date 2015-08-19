# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

class LookupTooltip(QtGui.QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.ToolTip)
        add_button = IconButton('c', 'add.png', self.tr('&Add This Word'), self.addWord)
        add_button.setStyleSheet('''QPushButton{border: none;margin: 3px;padding:5px}
        QPushButton:pressed {
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 rgba(0, 0, 0, 50), stop: 1 rgba(255,255,255,50));
        border: 1px solid rgba(255,255,255,50);
        border-radius: 3px;
        }
        QPushButton:hover:!pressed {
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 rgba(255,255,255,60), stop: 1 rgba(0,0,0,20));
        border: 1px solid rgba(255,255,255,50);
        border-radius: 3px;
        }
        ''')

        self.description_browser = QtGui.QTextBrowser()
        self.description_browser.setFrameShape(QtGui.QFrame.NoFrame)

        layout = QtGui.QVBoxLayout()
        layout.setMargin(1)
        layout.setSpacing(0)
        layout.addWidget(add_button)
        layout.addWidget(self.description_browser)
        self.setLayout(layout)
        self.adjustSize()
        self.setStyleSheet('''QDialog{border: 1px solid rgba(255, 255, 255, 50);}''')

        # Auto close() when mouse move out of tooltip
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.checkMousePosition)
        self.timer.start(300)

    def lookupAndShow(self, word):
        self.word = word
        self.description_browser.setText("Lookup...")
        self.move(QtGui.QCursor().pos().x() + 10, QtGui.QCursor().pos().y() + 10) # <= abs pos
        self.show()
        self.description_browser.setHtml(sdcv(word))

    def addWord(self):
        with open(FLASHCARD_PATH, 'a') as file:
            file.write(self.word + "\t0\n")
        self.parentWidget().statusBar().showMessage("New word added!")
        QtCore.QTimer.singleShot(1000, lambda: self.parentWidget().statusBar().clearMessage())
        self.close()

    def checkMousePosition(self):
        pos = self.pos()
        size = self.size()
        x = pos.x()
        y = pos.y()
        h = size.height()
        w = size.width()
        mouse = QtGui.QCursor.pos()
        if (mouse.x() > x + w + 20 or mouse.x() < x - 20 or
            mouse.y() > y + h + 20 or mouse.y() < y - 20):
            self.close()
