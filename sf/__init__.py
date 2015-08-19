# -*- coding: utf-8 -*-
import sys, os, math

from .main import *

from PyQt4 import QtCore, QtGui

def run():
    app = QtGui.QApplication(sys.argv)

    # Icon
    app_icon = QtGui.QIcon()
    app_icon.addFile('icons/16.png', QtCore.QSize(16,16))
    app_icon.addFile('icons/22.png', QtCore.QSize(22,22))
    app_icon.addFile('icons/32.png', QtCore.QSize(32,32))
    app_icon.addFile('icons/48.png', QtCore.QSize(48,48))
    app_icon.addFile('icons/256.png', QtCore.QSize(256,256))
    app.setWindowIcon(app_icon)
    
    # Internationalization
    LOCALE = QtCore.QLocale.system().name()
    translator = QtCore.QTranslator()
    if translator.load(LOCALE + '.qm', 'translate'): # name, dir
        print('Found localization file for ' + LOCALE)
    else:
        print('Not found localization file for ' + LOCALE)
    
    app.installTranslator(translator)
    
    main_window = MainWindow()
    
    
    app.exec_()

