PREFIX=/usr

all:
	@echo "You can run Stardict-Flashcard with ./runanki"
	@echo "If you wish to install it system wide, type 'sudo make install'"
	@echo "Uninstall with 'sudo make uninstall'"

install:
	rm -rf ${PREFIX}/share/stardict-flashcard
	mkdir -p ${PREFIX}/share/stardict-flashcard
	cp -av * ${PREFIX}/share/stardict-flashcard/
	cd ${PREFIX}/share/stardict-flashcard; \
		mv run ${PREFIX}/local/bin/stardict-flashcard; \
		mkdir -p ${PREFIX}/share/pixmaps/stardict-flashcard; \
		cp -v icons/16.png icons/22.png icons/32.png icons/48.png icons/256.png ${PREFIX}/share/pixmaps/ ;\
		mv stardict-flashcard.desktop ${PREFIX}/share/applications;

	@echo
	@echo "Install complete!"

uninstall:
	rm -rf ${PREFIX}/share/stardict-flashcard/
	rm -rf ${PREFIX}/local/bin/stardict-flashcard
	rm -rf ${PREFIX}/share/pixmaps/stardict-flashcard/
	rm -rf ${PREFIX}/share/applications/stardict-flashcard.desktop

	@echo
	@echo "Stardict-flashcard has been uninstalled from your system."


compile-qm:
	lrelease translate/*.ts

generate-ts:
	pylupdate4 main.py -ts translate/*.ts

remove-obsolete:
	pylupdate4 main.py -ts -noobsolete translate/*.ts
