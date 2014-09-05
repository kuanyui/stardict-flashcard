PREFIX=/usr
ICON_DIR=${PREFIX}/share/icons/hicolor
PWD=`pwd`
all:
	@echo "You can run Stardict-Flashcard with ./runanki"
	@echo "If you wish to install it system wide, type 'sudo make install'"
	@echo "Uninstall with 'sudo make uninstall'"

install:
	rm -rf ${PREFIX}/share/stardict-flashcard
	mkdir -p ${PREFIX}/share/stardict-flashcard
	cp -av *[^~] ${PREFIX}/share/stardict-flashcard/
	cd ${PREFIX}/share/stardict-flashcard; \
		mv run ${PREFIX}/local/bin/stardict-flashcard; \
		mv stardict-flashcard.desktop ${PREFIX}/share/applications; \
		cp -v ${PWD}/icons/256.png /usr/share/pixmaps/stardict-flashcard.png; \
		ln -s ${PWD}/icons/16.png ${ICON_DIR}/16x16/apps/stardict-flashcard.png; \
		ln -s ${PWD}/icons/22.png ${ICON_DIR}/22x22/apps/stardict-flashcard.png; \
		ln -s ${PWD}/icons/32.png ${ICON_DIR}/32x32/apps/stardict-flashcard.png; \
		ln -s ${PWD}/icons/48.png ${ICON_DIR}/48x48/apps/stardict-flashcard.png; \
		ln -s ${PWD}/icons/256.png ${ICON_DIR}/256x256/apps/stardict-flashcard.png;
	@echo
	@echo "Install complete!"

uninstall:
	rm -rf ${PREFIX}/share/stardict-flashcard/
	rm -rf ${PREFIX}/local/bin/stardict-flashcard
	rm -rf ${PREFIX}/share/applications/stardict-flashcard.desktop
	rm -f /usr/share/pixmaps/stardict-flashcard.png
	rm -f ${ICON_DIR}/16x16/apps/stardict-flashcard.png
	rm -f ${ICON_DIR}/22x22/apps/stardict-flashcard.png
	rm -f ${ICON_DIR}/32x32/apps/stardict-flashcard.png
	rm -f ${ICON_DIR}/48x48/apps/stardict-flashcard.png
	rm -f ${ICON_DIR}/256x256/apps/stardict-flashcard.png
	@echo
	@echo "Stardict-flashcard has been uninstalled from your system."


compile-qm:
	lrelease translate/*.ts

generate-ts:
	pylupdate4 main.py -ts translate/*.ts

remove-obsolete:
	pylupdate4 main.py -ts -noobsolete translate/*.ts

clean:
	@echo ${PWD}
	rm -f *~
