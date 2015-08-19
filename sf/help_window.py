# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
class HelpWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        text_browser = QtGui.QTextBrowser()
        text_browser.setStyleSheet("font-size:12px;")
        text_browser.setOpenExternalLinks(True)
        text_browser.setHtml(
            self.tr(
'''
<h1>Welcome to <i>Stardict Flashcard</i>!</h1>
You can add new word into Flashcard file within Stardict with <span style='background-color: #afd7ff; color: #005f87; white-space:pre;'> Alt+e </span>.<br>
(The words will be added into <i>~/dic.txt</i> by default, that is just so-called "Flashcard file")<br>
After adding some word into Flashcard file, it's time to startup <i>Stardict Flashcard</i>:
<ol>
<li>Press <span style='background-color: #afd7ff; color: #005f87; white-space:pre;'> Space </span> to display answer.</li>
<li>Then press <span style='background-color: #afd7ff; color: #005f87; white-space:pre;'> Enter </span> means you can recite this word.</li>
<li>Or if you can't think of the word and recite it, press <span style='background-color: #afd7ff; color: #005f87; white-space:pre;'> Space </span> to go on instead.</li>
<li>After a word can be recited up to 5 times, the word will be archived into current archive file automatically.</li>
<li>If a word was added by accident, you can press <span style='background-color: #afd7ff; color: #005f87; white-space:pre;'> Delete </span> to remove it.</li>
</ol>

After finishing all words, you still can review them again by <b>importing archive file</b> back to Flashcard file.<br>
You can manage archive file in <i>File/Manage Archive File</i>.
<h2> Need Help? </h2>
If you still have problem, you can visit our <a href="http://www.github.com/kuanyui/stardict-flashcard/">GitHub</a> and open an issue. (If ok, please use English.)
<h2> Contribution </h2>
Stardict Flashcard is a free software. So if you wish, your contribution is always welcome! Visit <a href="http://www.github.com/kuanyui/stardict-flashcard/">GitHub</a> to see what things can do.

'''))
        button = QtGui.QPushButton(self.tr("&Ok"))
        button.clicked.connect(self.close)
        button.setDefault(True)
        button.setAutoDefault(True)
        button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        button_box.accepted.connect(self.close)
        label = QtGui.QLabel(self.tr("Thanks for using Stardict Flashcard!"))
        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(label)
        main_layout.addWidget(text_browser)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)
        self.resize(600, 300)
        # make main window uncontrollable.
        self.setWindowModality(QtCore.Qt.WindowModal)
        
        self.show()
