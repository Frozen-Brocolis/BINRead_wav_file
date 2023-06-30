import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow,QApplication,QMenu, QToolBar, QMenuBar,QPushButton,QGridLayout, QWidget,QListWidgetItem,QCheckBox
from PyQt6.QtGui import QAction
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib
import math
import random
import wave
import companding
matplotlib.use('Qt5Agg')

class Ui_MainWindow():
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(546, 500)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget,tabsClosable=True)
        self.tabWidget.tabCloseRequested.connect(lambda index: self.tabWidget.removeTab(index))
        self.tabWidget.setObjectName("tabWidget")

        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.init_menbar(MainWindow)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.Pages=[]
        #self.add_Page("test.wav")
    def init_menbar(self,MainWindow):
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 540, 21))
        self.menubar.setObjectName("menubar")

        self.openAction = QAction("&Открыть", self.menubar)
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.triggered.connect(self.Open)

        self.saveAction = QAction("&Сохранить", self.menubar)
        self.saveAction.triggered.connect(self.Save_as)
        self.saveAction.setShortcut("Ctrl+S")

        self.cutAction = QAction("C&ut", self.menubar)
        self.helpContentAction = QAction("&Help Content", self.menubar)
        self.aboutAction = QAction("&About", self.menubar)

        self.fileMenu = QMenu("&Файл", self.menubar)
        self.menubar.addMenu(self.fileMenu)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.openAction)


        self.Graf_1 = QAction("&Режим 1 график", self.menubar)
        self.Graf_1.triggered.connect(self.F_Graf_1 )
        self.Graf_4 = QAction("&Режим 4 графика", self.menubar)
        self.Graf_4.triggered.connect(self.F_Graf_4)
        self.fileMenu = QMenu("&Вид", self.menubar)
        self.menubar.addMenu(self.fileMenu)
        self.fileMenu.addAction(self.Graf_1)
        self.fileMenu.addAction(self.Graf_4)
        MainWindow.setMenuBar(self.menubar)
    def F_Graf_1(self):

        self.Pages[self.tabWidget.currentIndex()].draw2(False)
    def F_Graf_4(self):
        self.Pages[self.tabWidget.currentIndex()].draw2(True)
    def add_Page(self,name,more_G=False):
        tab = QtWidgets.QWidget()
        self.tabWidget.addTab(tab, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(tab), QtCore.QCoreApplication.translate("MainWindow", f"{name}"))
        self.Pages.append(Page(name,tab,more_G=more_G))
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Чтение wav-файлов"))
    def Save_as(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File','.\\',"Sound (*.wav)")[0]
        Page=self.Pages[self.tabWidget.currentIndex()]
        print(f"Save as - {name}")
        with wave.open(name, mode='wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(int(Page.inf["bit depth"]/8))  # bytes
            wav_file.setframerate(Page.inf["Sample Rate"])
            for i in Page.Data[2][1]:
                wav_file.writeframes(i)
    def Open(self):
        name=QtWidgets.QFileDialog.getOpenFileNames(self, "Open",".\\","Sound (*.wav)")
        if len(name)>0:
            self.add_Page(name[0][0].split("/")[-1])


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setupUi(self)

class Page():
    def __init__(self,name,tab,more_G=False):
        self.tab=tab
        self.name=name
        self.gridLayout = QtWidgets.QGridLayout(self.tab)
        self.gridLayout.setObjectName("gridLayout")
        self.inf, self.Data = companding.read_file(name)
        self.draw2(more_G)
        self.colors=["b","y","g","r"]
    def draw(self,item):
        item.is_visible=(not item.is_visible)
        self.Plot.axes.clear()
        for index in range(self.kksView.count()):
            item=self.kksView.item(index)
            if item.is_visible:
                self.Plot.axes.plot(self.Data[index][0],self.Data[index][1],label=item.text(),color=self.colors[index])
        self.Plot.axes.legend(loc='upper right')
        self.Plot.draw()
    def draw2(self,more_G):
        for i in range(self.gridLayout.count()):
            self.gridLayout.itemAt(0).widget().setParent(None)
        self.fig, self._ax = plt.subplots()
        _translate = QtCore.QCoreApplication.translate
        self.groupBox = QtWidgets.QGroupBox(self.tab)
        self.groupBox.clicked.connect(self.click)
        self.groupBox.setObjectName("groupBox")
        self.Plot = MplCanvas(self.tab, width=5, height=4, dpi=100, more_G=more_G)
        self.Plot.clicked.connect(self.click)
        self.toolbar = NavigationToolbar(self.Plot, self.tab)
        self.grid = QGridLayout()
        self.grid.addWidget(self.toolbar, 0, 0, 1, 1)
        self.grid.addWidget(self.Plot, 1, 0, 1, 1)
        self.groupBox.setLayout(self.grid)
        self.groupBox.setTitle(_translate("MainWindow", "Графики"))
        self.G_names=["Изначальный","Graf_2","Восстановленный","Разница"]
        if not more_G:
            self.kksView = QtWidgets.QListWidget()
            for text in self.G_names:
                item = QListWidgetItem(text)
                item.is_visible = False
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                self.kksView.addItem(item)
            self.kksView.itemChanged.connect(self.draw)
            self.gridLayout.addWidget(self.kksView, 0, 0, 1, 15)

        else:
            if True:
                for index in range(4):
                    self.Plot.axess[index].clear()
                    self.Plot.axess[index].set_title(self.G_names[index])
                    self.Plot.axess[index].plot(self.Data[index][0], self.Data[index][1],color=self.colors[index])
                self.Plot.draw()
        self.gridLayout.addWidget(self.groupBox, 0, 15, 1, 1)


    def click(self):#Эта функция вызывается когда нажимаешь на график
        pass

class MplCanvas(FigureCanvasQTAgg):
    clicked = QtCore.pyqtSignal()
    def __init__(self, parent=None, width=5, height=4, dpi=100,more_G=False):
        fig = Figure(figsize=(width, height), dpi=dpi)
        if more_G:
            self.axess = [fig.add_subplot(221), fig.add_subplot(222), fig.add_subplot(223), fig.add_subplot(224)]
        else:
            self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.clicked.emit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec())
