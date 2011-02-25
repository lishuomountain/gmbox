pyuic=pyuic4
pyrcc=pyrcc4

all: qrc mui aui

qrc: icons/*
	${pyrcc} icons/icons.qrc -o icons_rc.py

mui: gmbox-qt.ui
	${pyuic} gmbox-qt.ui -o main_ui.py

aui: about.ui
	${pyuic} about.ui -o about.py
