#!/usr/bin/python2
# -*- coding: utf-8 -*-
# Name:     player.py
# Author:   xiooli <xioooli[at]yahoo.com.cn>
# Licence:  GPLv3
# Version:  110225

import sys
from PyQt4 import QtCore, QtGui

try:
    from PyQt4.phonon import Phonon
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "Music Player",
            "Your Qt installation does not have Phonon support.",
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
            QtGui.QMessageBox.NoButton)
    sys.exit(1)


class Player(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.mediaObject = Phonon.MediaObject(self)
        self.metaInformationResolver = Phonon.MediaObject(self)

        self.mediaObject.setTickInterval(1000)

        self.connect(self.mediaObject, QtCore.SIGNAL('tick(qint64)'),
                self.tick)
        self.connect(self.mediaObject,
                QtCore.SIGNAL('stateChanged(Phonon::State, Phonon::State)'),
                self.stateChanged)
        self.connect(self.metaInformationResolver,
                QtCore.SIGNAL('stateChanged(Phonon::State, Phonon::State)'),
                self.metaStateChanged)
        self.connect(self.mediaObject,
                QtCore.SIGNAL('currentSourceChanged(Phonon::MediaSource)'),
                self.sourceChanged)
        self.connect(self.mediaObject, QtCore.SIGNAL('aboutToFinish()'),
                self.aboutToFinish)

        Phonon.createPath(self.mediaObject, self.audioOutput)

        self.setupActions()
        self.setupUi()
        self.show()
        self.sources = []

    def addFiles(self):
        files = QtGui.QFileDialog.getOpenFileNames(self,
                  u"选择音乐文件",
                  QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.MusicLocation))

        if files=="":
            return

        index = len(self.sources)

        for string in files:
            self.sources.append(Phonon.MediaSource(string))

        if self.sources:
            self.metaInformationResolver.setCurrentSource(self.sources[index])

    def stateChanged(self, newState, oldState):
        if newState == Phonon.ErrorState:
            if self.mediaObject.errorType() == Phonon.FatalError:
                QtGui.QMessageBox.warning(self, u"致命错误",
                        self.mediaObject.errorString())
            else:
                QtGui.QMessageBox.warning(self, u"错误",
                        self.mediaObject.errorString())

        elif newState == Phonon.PlayingState:
            self.playAction.setEnabled(False)
            self.pauseAction.setEnabled(True)
            self.stopAction.setEnabled(True)

        elif newState == Phonon.StoppedState:
            self.stopAction.setEnabled(False)
            self.playAction.setEnabled(True)
            self.pauseAction.setEnabled(False)
            self.timeLcd.display("00:00")

        elif newState == Phonon.PausedState:
            self.pauseAction.setEnabled(False)
            self.stopAction.setEnabled(True)
            self.playAction.setEnabled(True)

    def tick(self, time):
        displayTime = QtCore.QTime(0, (time / 60000) % 60, (time / 1000) % 60)
        self.timeLcd.display(displayTime.toString('mm:ss'))

    def tableClicked(self, row, column):
        oldState = self.mediaObject.state()

        self.mediaObject.stop()
        self.mediaObject.clearQueue()

        self.mediaObject.setCurrentSource(self.sources[row])

        if oldState == Phonon.PlayingState:
            self.mediaObject.play()

    def sourceChanged(self, source):
        self.musicTable.selectRow(self.sources.index(source))
        self.timeLcd.display("00:00")

    def metaStateChanged(self, newState, oldState):
        if newState == Phonon.ErrorState:
            QtGui.QMessageBox.warning(self, u"打开文件失败！",
                    self.metaInformationResolver.errorString())

            while self.sources and self.sources.pop() != self.metaInformationResolver.currentSource():
                pass

            return

        if newState != Phonon.StoppedState and newState != Phonon.PausedState:
            return

        if self.metaInformationResolver.currentSource().type() == Phonon.MediaSource.Invalid:
            return

        metaData = self.metaInformationResolver.metaData()

        title = metaData.get(QtCore.QString(u'TITLE'), [""])[0]
        if title=="":
            title = self.metaInformationResolver.currentSource().fileName()

        titleItem = QtGui.QTableWidgetItem(title)
        titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)

        artist = metaData.get(QtCore.QString(u'ARTIST'), [""])[0]
        artistItem = QtGui.QTableWidgetItem(artist)
        artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)

        album = metaData.get(QtCore.QString(u'ALBUM'), [""])[0]
        albumItem = QtGui.QTableWidgetItem(album)
        albumItem.setFlags(albumItem.flags() ^ QtCore.Qt.ItemIsEditable)

        year = metaData.get(QtCore.QString(u'DATE'), [""])[0]
        yearItem = QtGui.QTableWidgetItem(year)
        yearItem.setFlags(yearItem.flags() ^ QtCore.Qt.ItemIsEditable)

        currentRow = self.musicTable.rowCount()
        self.musicTable.insertRow(currentRow)
        self.musicTable.setRowHeight(currentRow, 20)
        self.musicTable.setItem(currentRow, 0, titleItem)
        self.musicTable.setItem(currentRow, 1, artistItem)
        self.musicTable.setItem(currentRow, 2, albumItem)
        self.musicTable.setItem(currentRow, 3, yearItem)

        if not self.musicTable.selectedItems():
            self.musicTable.selectRow(0)
            self.mediaObject.setCurrentSource(self.metaInformationResolver.currentSource())

        source = self.metaInformationResolver.currentSource()
        index = self.sources.index(self.metaInformationResolver.currentSource()) + 1

        if len(self.sources) > index:
            self.metaInformationResolver.setCurrentSource(self.sources[index])

    def aboutToFinish(self):
        index = self.sources.index(self.mediaObject.currentSource()) + 1
        if len(self.sources) > index:
            self.mediaObject.enqueue(self.sources[index])

    def setupActions(self):
        self.playAction = QtGui.QAction(self)
        self.playAction.setText(u"播放")
        self.playAction.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MediaPlay))
        self.playAction.setShortcut("Crl+P")
        self.playAction.setDisabled(True)

        self.pauseAction = QtGui.QAction(self)
        self.pauseAction.setText(u"暂停")
        self.pauseAction.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MediaPause))
        self.pauseAction.setShortcut("Ctrl+A")
        self.pauseAction.setDisabled(True)

        self.stopAction = QtGui.QAction(self)
        self.stopAction.setText(u"停止")
        self.stopAction.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MediaStop))
        self.stopAction.setShortcut("Ctrl+S")
        self.stopAction.setDisabled(True)

        self.nextAction = QtGui.QAction(self)
        self.nextAction.setText(u"下一首")
        self.nextAction.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MediaSkipForward))
        self.nextAction.setShortcut("Ctrl+N")

        self.previousAction = QtGui.QAction(self)
        self.previousAction.setText(u"上一首")
        self.previousAction.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MediaSkipBackward))
        self.previousAction.setShortcut("Ctrl+R")

        self.connect(self.playAction, QtCore.SIGNAL('triggered()'),
                self.mediaObject, QtCore.SLOT('play()'))
        self.connect(self.pauseAction, QtCore.SIGNAL('triggered()'),
                self.mediaObject, QtCore.SLOT('pause()'))
        self.connect(self.stopAction, QtCore.SIGNAL('triggered()'),
                self.mediaObject, QtCore.SLOT('stop()'))

    def setupUi(self):
        bar = QtGui.QToolBar()

        bar.addAction(self.playAction)
        bar.addAction(self.pauseAction)
        bar.addAction(self.stopAction)

        self.seekSlider = Phonon.SeekSlider(self)
        self.seekSlider.setMediaObject(self.mediaObject)

        self.volumeSlider = Phonon.VolumeSlider(self)
        self.volumeSlider.setAudioOutput(self.audioOutput)
        self.volumeSlider.setSizePolicy(QtGui.QSizePolicy.Maximum,
                QtGui.QSizePolicy.Maximum)

        volumeLabel = QtGui.QLabel()
        volumeLabel.setPixmap(QtGui.QPixmap('images/volume.png'))

        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Light, QtCore.Qt.darkGray)

        self.timeLcd = QtGui.QLCDNumber()
        self.timeLcd.setPalette(palette)
        self.timeLcd.display("00:00")

        headers = [u"标题", u"艺人", u"专辑", u"年份"]

        self.musicTable = QtGui.QTableWidget(0, len(headers))
        for i in range(len(headers)):
            self.musicTable.setColumnWidth(i, 198)
        self.musicTable.setHorizontalHeaderLabels(headers)
        self.musicTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.musicTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.connect(self.musicTable, QtCore.SIGNAL('cellPressed(int, int)'),
                self.tableClicked)

        seekerLayout = QtGui.QHBoxLayout()
        seekerLayout.addWidget(self.seekSlider)
        seekerLayout.addWidget(self.timeLcd)

        playbackLayout = QtGui.QHBoxLayout()
        playbackLayout.addWidget(bar)
        playbackLayout.addStretch()
        playbackLayout.addWidget(volumeLabel)
        playbackLayout.addWidget(self.volumeSlider)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.musicTable)
        mainLayout.addLayout(seekerLayout)
        mainLayout.addLayout(playbackLayout)

        self.setLayout(mainLayout)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Music Player")
    class Win(QtGui.QMainWindow):
        def __init__(self):
            QtGui.QMainWindow.__init__(self)
            self.resize(620, 300)
            self.menubar = QtGui.QMenuBar(self)
            self.menubar.setGeometry(QtCore.QRect(0, 0, 812, 23))
            self.menu = QtGui.QMenu(self.menubar)
            self.menu.setTitle(u"文件")
            self.setMenuBar(self.menubar)
            self.menubar.addMenu(self.menu)
            self.addFilesAction = QtGui.QAction(self)
            self.addFilesAction.setText(u"添加文件 &F")
            self.addFilesAction.setShortcut("Ctrl+F")
            self.menu.addAction(self.addFilesAction)
            player = Player(self)
            self.addFilesAction.triggered.connect(player.addFiles)
            self.setCentralWidget(player)
            self.show()

    window = Win()

    sys.exit(app.exec_())
