# -*- coding: utf-8 -*-
from distutils.core import setup

import packages
setup(
    name='stardict-flashcard',
    version=puddlestuff.version_string,
    author='kuanyui',
    author_email='azazabc123@gmail.com',
    url='http://github.com/kuanyui/stardict-flashcard',
    download_url='http://github.com/kuanyui/stardict-flashcard',
    description='A Flashcard For StarDict. (Based on sdcv)',
    packages = ['packages'],

    keywords=['stardict', 'dictionary', 'flashcard', 'learning', 'language'],
    license='GNU General Public License v3',
    classifiers=[
        'Development Status :: 2 - Unstable',
        'Intended Audience :: End Users/Desktop',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Education',
        'Natural Language :: English',
        'Operating System :: GNU/Linux',
        'Programming Language :: Python :: 3.3',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Topic :: Education',
             ],
        
    scripts = ['stardict-flashcard'],
    data_files=[('share/pixmaps/stardict-flashcard', ('16.png',
                                                      '22.png',
                                                      '32.png',
                                                      '48.png',
                                                      '256.png',)),
                ('share/applications/', ('stardict-flashcard.desktop',)),]
     )
