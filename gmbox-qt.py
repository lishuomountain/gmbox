#!/usr/bin/python2
# -*- coding: utf-8 -*-
# Name:     gmbox-qt.py
# Author:   xiooli <xioooli[at]yahoo.com.cn>
# Licence:  GPLv3
# Version:  110222
import sys, os
from main_ui import Ui_mainWindow
from about import Ui_About
from core import *
from utils import *
from scratcher import *
from player import Player
from PyQt4.QtCore import pyqtSignal, Qt,  QModelIndex, \
        QVariant, SIGNAL, QString
from PyQt4.QtGui import QMainWindow, QApplication, QStandardItemModel, \
        QStandardItem, QAction, QMenu, QAbstractItemView, QWidget, \
        QVBoxLayout, QTreeView, qApp, QMessageBox, QIcon, QPixmap

__appname__ = u'Gmbox-Qt'
__version__ = u'pre-alpha 0.0'

class MyItemModel(QStandardItemModel):
    def __init__(self, data_list, header_list, parent = None):
        '''data_list is a list of lists with data, while
        header_list is a list with the header names'''
        QStandardItemModel.__init__(self, len(data_list), len(header_list), parent)
        self.data_list = data_list
        self.header_list = header_list

        for i, header in enumerate(self.header_list):
            self.setHeaderData(i, Qt.Horizontal, QVariant(header))

        for i, row in enumerate(self.data_list):
            for j, v in enumerate(row):
                self.setData(self.index(i, j), QVariant(v), 0)
        self.row = i + 1
    def appendRows(self, data_list, parent = None):
        self.insertRows(self.row, len(data_list))
        for i, row in enumerate(data_list):
            for j, v in enumerate(row):
                self.setText(self.index(i + self.row, j), v, Qt.DisplayRole)
        self.row += i + 1
    def addChildren(self, row_idx, data_list):
        # TODO implement this func
        pass

class Win(QMainWindow, Ui_mainWindow):
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.header = [u'名字', u'艺人', u'专辑']
        self.colwidth = [200, 200, 200]

        self.search_results = {}
        self.treeViews = []
        self.models = []
        self.search_tabs = []
        self.search_types = {QString(u'歌曲'): Search,
            QString(u'专辑'): DirSearch,
            QString(u'歌手'): DirArtist}

        self.redio_btns = [self.radioButton, self.radioButton_2, self.radioButton_3]

        # player
        self.player = Player(self)
        verLayout = QVBoxLayout(self.tab_2)
        verLayout.addWidget(self.player)

        # downloader
        # TODO downloader works OK separately, needed to integrate into the main window

        # about
        self.about_widget = QWidget()
        about = Ui_About()
        about.setupUi(self.about_widget)
        about.pushButton.setText(u'%s\n%s' %(__appname__, __version__))

        self.show()
        self.connect_signals()

    def connect_signals(self):
        '''connect the signals'''
        self.pushButton.clicked.connect(self._on_add_tab)
        self.pushButton_2.clicked.connect(self._on_prev_page)
        self.pushButton_4.clicked.connect(self._on_next_page)
        self.action_exit.triggered.connect(self.close)
        self.action_qt.triggered.connect(qApp.aboutQt)
        self.action_add_musics.triggered.connect(self._on_add_musics)
        self.action_config.triggered.connect(self._on_config_gmbox_qt)
        self.action_about_gmbox_qt.triggered.connect(self._on_about_gmbox_qt)
        self.tabWidget_2.tabCloseRequested.connect(self._on_tabWidget_2_removeTab)
        self.tabWidget_2.currentChanged.connect(self._on_tabWidget_2_tab_changed)
        self.lineEdit.returnPressed.connect(self._on_add_tab)

    def _on_add_musics(self):
        self.tabWidget.setCurrentIndex(1)
        self.player.addFiles()

    def add_tab(self, search_cls, tabText):
        data = []
        key_words = myurlencode(u'%s' %self.lineEdit.text())
        tab = QWidget()
        treeView = QTreeView(tab)
        treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        treeView.customContextMenuRequested.connect(self._contextMenu)
        verLayout = QVBoxLayout(tab)
        verLayout.addWidget(treeView)
        self.tabWidget_2.addTab(tab, u"%s" %tabText)
        self.tabWidget_2.setCurrentIndex(self.tabWidget_2.indexOf(tab))
        self.search_tabs.append(tab)
        self.treeViews.append(treeView)
        thrd = mythread(self)
        thrd.callback = lambda: search_cls(key_words)
        thrd.data_pool = self.search_results
        thrd.data_key = tabText
        thrd.start()
        thrd.finished.connect(lambda: self.update_treeView(treeView,
            self.search_results[tabText]))

    def change_page(self, next = True):
        treeView = self.treeViews[self.tabWidget_2.currentIndex()]
        tabText = '%s' %self.tabWidget_2.tabText(self.tabWidget_2.currentIndex())
        search_obj = self.search_results[tabText]
        if next:
            page = search_obj.current_page + 1
            try:
                self.update_treeView(treeView, search_obj, page)
            except:
                search_obj.current_page -= 1
        else:
            page = search_obj.current_page - 1
            try:
                self.update_treeView(treeView, search_obj, page)
            except:
                search_obj.current_page += 1

    def _on_next_page(self):
        self.change_page(next = True)

    def _on_prev_page(self):
        self.change_page(next = False)

    def _on_tabWidget_2_tab_changed(self, idx):
        try:
            treeView = self.treeViews[idx]
            self.pushButton_2.setDisabled(treeView.prev_page_disabled)
            self.pushButton_4.setDisabled(treeView.next_page_disabled)
        except:
            pass

    def update_treeView(self, treeView, search_obj, page = 0):
        if page <= 0:
            self.pushButton_2.setDisabled(True)
            treeView.prev_page_disabled = True
        else:
            self.pushButton_2.setDisabled(False)
            treeView.prev_page_disabled = False
        number = 20
        start = number * page
        search_obj.current_page = page
        try:
            songs = search_obj.load_songs(start, number)
        except:
            try:
                songs = search_obj.load_songlists(start, number)
            except:
                pass

        if len(songs) < number:
            self.pushButton_4.setDisabled(True)
            treeView.next_page_disabled = True
        else:
            self.pushButton_4.setDisabled(False)
            treeView.next_page_disabled = False

        data = [[s.name, s.artist, s.album] for s in songs]
        model = MyItemModel(data, self.header, self)
        treeView.setModel(model)
        for i, wid in enumerate(self.colwidth):
            treeView.setColumnWidth(i, wid)
        if treeView in self.treeViews and len(self.models) != 0 and \
                self.treeViews.index(treeView) in range(len(self.models)):
            self.models[self.treeViews.index(treeView)] = model
        else:
            self.models.append(model)

    def get_search_type(self):
        for r in self.redio_btns:
            if r.isChecked():
                return r.text()

    def _on_add_tab(self):
        if self.lineEdit.text():
            tabText = '%s - (%s)' %(self.lineEdit.text(), self.get_search_type())
            for i in range(len(self.search_tabs)):
                if self.tabWidget_2.tabText(i) == QString(tabText):
                    self.tabWidget_2.setCurrentIndex(i)
                    return
            self.add_tab(self.search_types[self.get_search_type()], tabText)

    def _contextMenu(self, menu_pos):
        # Select the right clicked item
        cur_tab_idx = self.tabWidget_2.currentIndex()
        index = self.treeViews[cur_tab_idx].indexAt(menu_pos)
        if index.isValid() and self.models[cur_tab_idx]:
            self.menu.exec_(self.treeViews[cur_tab_idx].viewport().mapToGlobal(menu_pos))

    def _on_echo(self, idx = None):
        # test func
        print self.tabWidget.currentIndex(), idx

    def _on_config_gmbox_qt(self):
        '''configuration part'''
        # TODO the configuration actions
        print 'configuration'

    def _on_about_gmbox_qt(self):
        '''show about gmbox-qt'''
        self.about_widget.show()

    def _on_tabWidget_2_removeTab(self, idx):
        '''close tab in tabWidget_2 when the close mark on tab is pressed'''
        self.tabWidget_2.removeTab(idx)
        try:
            self.search_tabs.pop(idx)
            self.treeViews.pop(idx)
            self.models.pop(idx)
        except:
            pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Win()
    sys.exit(app.exec_())
