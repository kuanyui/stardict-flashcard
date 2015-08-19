# -*- coding: utf-8 -*-
import sys, os, math
from PyQt4 import QtCore, QtGui

from .config_window import *

class ConfigWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.line_dict_path = QtGui.QLineEdit()
        self.line_dict_path.setText(FLASHCARD_PATH)
        button_dict_path = IconButton('c', 'browse.png', '&Browse...', self.browseFlashcardPath)
        self.spin_box = QtGui.QSpinBox()
        self.spin_box.setRange(1, 100)
        self.spin_box.setValue(MEMORIZED_COUNT)

        button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.applyAndWriteConfigFile)
        button_box.rejected.connect(self.close)

        self.remember_index_checkbox = QtGui.QCheckBox("&Remember Index After Quit")
        if REMEMBER_INDEX >= 0:
            self.remember_index_checkbox.setChecked(True)
        
        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel(self.tr("Flashcard file path:")), 0, 0)
        layout.addWidget(self.line_dict_path, 0, 1)
        layout.addWidget(button_dict_path, 0, 2)
        layout.addWidget(QtGui.QLabel(self.tr("Memorized count:")), 1, 0)
        layout.addWidget(self.spin_box, 1, 1, 1, 1)
        layout.addWidget(self.remember_index_checkbox, 2, 0)
        layout.addWidget(button_box, 3, 1, 1, 2)


        self.setLayout(layout)
        self.adjustSize()
        self.resize(700, self.height())

    def browseFlashcardPath(self):
        path = QtGui.QFileDialog.getOpenFileName(self, self.tr("Select Flashcard File Path"),
                                                 os.path.expanduser("~/"))
        if path:
            self.line_dict_path.setText(path)

    def applyAndWriteConfigFile(self):
        global FLASHCARD_PATH, MEMORIZED_COUNT, REMEMBER_INDEX
        FLASHCARD_PATH  = str(self.line_dict_path.text())
        MEMORIZED_COUNT = int(self.spin_box.value())
        if self.remember_index_checkbox.checkState() == QtCore.Qt.Checked:
            REMEMBER_INDEX = 0
        else:
            REMEMBER_INDEX = -1

        self.parent.config.writeConfigFile()
        self.close()

