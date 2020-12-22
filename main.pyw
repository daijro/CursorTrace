from PyQt5 import QtCore, QtGui, QtWidgets
import time
import skimage
import skimage.io
import skimage.feature
import skimage.viewer
import sys, os
import pyautogui
import threading
from pynput.mouse import Button, Controller
from pynput import keyboard
from tkinter import messagebox
import tkinter as tk
import numpy as np
from skimage.io._plugins.pil_plugin import ndarray_to_pil
import pygame
import win32gui, win32con, win32api
from tkinter.filedialog import askopenfile
import ctypes

mouse = Controller()

root = tk.Tk()
root.withdraw()

class Ui_MainWindow(object):
    def initialize_preview(self, process_image=False, initialize_pygame=False):
        # read command-line arguments
        
        sigma = self.doubleSpinBox_2.value()
        low_threshold = self.doubleSpinBox_4.value() / 100
        high_threshold = self.doubleSpinBox_5.value() / 100
        scale = self.doubleSpinBox_3.value() / 100
        originx = self.spinBox.value()
        originy = self.spinBox_2.value()


        if process_image:
            image = skimage.io.imread(fname=self.filename, as_gray=True)
            # load and display original image as grayscale
            self.edges = skimage.feature.canny(
                image=image,
                sigma=sigma,
                low_threshold=low_threshold,
                high_threshold=high_threshold,
            )

            self.edges = skimage.feature.canny(
                image=image,
                sigma=sigma,
                low_threshold=low_threshold,
                high_threshold=high_threshold,
            )

            #viewer = skimage.viewer.ImageViewer(self.edges)
            #viewer.show()

            # self.edges[154, 259] is Y, X
            # len(self.edges) returns the height, so it is rows or X
            # len(self.edges[0] # this returns the width, so it is cols or Y
        if initialize_pygame:
            pygame.init() # initialize pygame window
            pygame.display.set_caption('CursorTrace - Preview') #set the title
            #WINDOW_SIZE = (ceil(len(self.edges)*scale), ceil(len(self.edges[0])*scale)) #set window size
            user32 = ctypes.windll.user32
            self.screen = pygame.display.set_mode((user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)), pygame.NOFRAME) #get the self.screen, set window size to self.screen / For borderless, use pygame.NOFRAME
            self.hwnd = pygame.display.get_wm_info()['window']
            win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0,0,0,0,0 | win32con.SWP_NOSIZE)

        self.white_pixels = []

        for i in range(len(self.edges)):
            for j in range(len(self.edges[0])):
                if self.edges[i, j]:
                    self.white_pixels.append([j*scale, i*scale])

        self.clock = pygame.time.Clock() #refresh every 1/60 of a sec

        self.fuchsia = (255, 0, 128)  # Transparency color

        # Create layered window
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE,
                            win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        # Set window transparency color
        win32gui.SetLayeredWindowAttributes(self.hwnd, win32api.RGB(*self.fuchsia), 0, win32con.LWA_COLORKEY)

        self.screen.fill(self.fuchsia)
        
        # Lag free mode
        if not self.checkBox.isChecked():
            image = ndarray_to_pil(self.edges)
            image = image.convert('RGB')

            size = image.size
            data = image.tobytes()

            py_image = pygame.image.fromstring(data, size, 'RGB')
            py_image = pygame.transform.scale(py_image, (round(size[0]*scale), round(size[1]*scale)))

            self.screen.blit(py_image, (originx, originy))
        else:
            # Draw Preview
            for i in self.white_pixels:
                pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(round(originx + i[0]), round(originy + i[1]), round(scale), round(scale)))
        

        #os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (self.spinBox.value(), self.spinBox_2.value())
        #pygame.display.set_mode((ceil(len(self.edges)*scale), ceil(len(self.edges[0])*scale)), pygame.NOFRAME) #Update the window
        #pygame.display.set_mode((ceil(len(self.edges)*scale), ceil(len(self.edges[0])*scale)), pygame.NOFRAME)
        pygame.display.update()
    
    def changeXY(self):
        scale = self.doubleSpinBox_3.value() / 100
        self.screen.fill(self.fuchsia)
        if not self.checkBox.isChecked():
            image = ndarray_to_pil(self.edges)
            image = image.convert('RGB')


            size = image.size
            #image = image.resize((round(size[0]*scale), round(size[1]*scale)))
            data = image.tobytes()

            py_image = pygame.image.fromstring(data, size, 'RGB')
            py_image = pygame.transform.scale(py_image, (round(size[0]*scale), round(size[1]*scale)))

            self.screen.blit(py_image, (self.spinBox.value(), self.spinBox_2.value()))
        else:
            for i in self.white_pixels:
                pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(round(self.spinBox.value() + i[0]), round(self.spinBox_2.value() + i[1]), round(scale), round(scale)))
        pygame.display.update()
    
    def toggle(self):
        self.toggle_loop = not self.toggle_loop

    def toggle_pause1(self):
        self.toggle_pause = not self.toggle_pause
        #messagebox.showinfo('CursorTrace - Paused', f'Drawing has been paused. Please press {self.pausehotkey} to continue.')

    def keyboard_thread(self, stophotkey, pausehotkey):
        with keyboard.GlobalHotKeys({stophotkey: self.toggle, pausehotkey: self.toggle_pause1}) as h:
            h.join()
        
    def draw(self):
        #if messagebox.askokcancel('CursorTrace', 'Are you sure you want to start?') != True:
        #    return
        pygame.quit()
        scale = self.doubleSpinBox_3.value() / 100
        originx = self.spinBox.value()
        originy = self.spinBox_2.value()
        stophotkey = self.lineEdit_2.text()
        pausehotkey = self.lineEdit.text()
        delay = self.doubleSpinBox.value() / 1000
        MainWindow.close()

        self.toggle_loop = True
        self.toggle_pause = True

        if self.comboBox_2.currentText() == 'Left': click = Button.left
        elif self.comboBox_2.currentText() == 'Right': click = Button.right
        elif self.comboBox_2.currentText() == 'Middle': click = Button.middle


        #originx, originy = pyautogui.position()

        x, y = self.white_pixels[0]
        mouse.position = (originx+x, originy+y)

        try: _= self.t
        except:
            self.t = threading.Thread(target=self.keyboard_thread, args=(stophotkey, pausehotkey))
            self.t.daemon = True
            self.t.start()
        

        pyautogui.PAUSE = delay
        mouse.press(click)
        while len(self.white_pixels) > 0 and self.toggle_loop:
            if not self.toggle_pause:
                mouse.release(click)
                while not self.toggle_pause:
                    pass
                pyautogui.moveTo(originx+x, originy+y)
                mouse.press(click)
            if [x, y+scale] in self.white_pixels:
                y+=scale
                pyautogui.moveTo(originx+x, originy+y)
                self.white_pixels.remove([x, y])
            elif [x+scale, y] in self.white_pixels:
                x+=scale
                pyautogui.moveTo(originx+x, originy+y)
                self.white_pixels.remove([x, y])
            elif [x, y-scale] in self.white_pixels:
                y-=scale
                pyautogui.moveTo(originx+x, originy+y)
                self.white_pixels.remove([x, y])
            elif [x-scale, y] in self.white_pixels:
                x-=scale
                pyautogui.moveTo(originx+x, originy+y)
                self.white_pixels.remove([x, y])
            elif [x+scale, y+scale] in self.white_pixels:
                x+=scale; y+=scale
                pyautogui.moveTo(originx+x, originy+y)
                self.white_pixels.remove([x, y])
            elif [x+scale, y-scale] in self.white_pixels:
                x+=scale; y-=scale
                pyautogui.moveTo(originx+x, originy+y)
                self.white_pixels.remove([x, y])
            elif [x-scale, y-scale] in self.white_pixels:
                x-=scale; y-=scale
                pyautogui.moveTo(originx+x, originy+y)
                self.white_pixels.remove([x, y])
            elif [x-scale, y+scale] in self.white_pixels:
                x-=scale; y+=scale
                pyautogui.moveTo(originx+x, originy+y)
                self.white_pixels.remove([x, y])
            else:
                mouse.release(click)
                # print(x, y)
                x, y = self.white_pixels[0]
                pyautogui.moveTo(originx+x, originy+y)

                self.white_pixels.remove([x, y])
                mouse.press(click)
            time.sleep(delay)
            #print(len(self.white_pixels))
        mouse.release(click)
        #t.terminate()
        if not self.toggle_loop:
            if messagebox.askokcancel('CursorTrace - Stopped', f'Drawing has been stopped. Would you like to open the config?') != True:
                sys.exit()
        self.toggle_loop = True
        self.toggle_pause = True
        self.initialize_preview(True, True)
        MainWindow.show()

    def setconnections(self):
        MainWindow.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(sys.argv[0]), 'icons', 'icon.ico')))
        self.spinBox.setMaximum(999999999)
        self.spinBox_2.setMaximum(999999999)
        self.spinBox.setMinimum(-999999999)
        self.spinBox_2.setMinimum(-999999999)
        try:
            self.filename = sys.argv[1]
        except:
            self.filename = askopenfile()
            if self.filename == None: sys.exit()
            self.filename = self.filename.name.replace('/', '\\')
            print(self.filename)

        self.initialize_preview(True, True)
        self.horizontalSlider.valueChanged.connect(lambda x: self.doubleSpinBox_2.setValue(x/4))
        self.horizontalSlider_2.valueChanged.connect(lambda x: self.doubleSpinBox_4.setValue(x/100))
        self.horizontalSlider_3.valueChanged.connect(lambda x: self.doubleSpinBox_5.setValue(x/100))


        self.doubleSpinBox_3.valueChanged.connect(self.initialize_preview)
        self.spinBox.valueChanged.connect(self.changeXY)
        self.spinBox_2.valueChanged.connect(self.changeXY)
        self.doubleSpinBox_2.valueChanged.connect(lambda: self.initialize_preview(True))
        self.doubleSpinBox_4.valueChanged.connect(lambda: self.initialize_preview(True))
        self.doubleSpinBox_5.valueChanged.connect(lambda: self.initialize_preview(True))
        self.pushButton_3.clicked.connect(lambda: sys.exit())
        self.checkBox.toggled.connect(self.changeXY)

        self.pushButton.clicked.connect(self.draw)
        MainWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        MainWindow.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        MainWindow.show()
        self.done = False
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
            pygame.display.update()
            self.clock.tick(0)
            #QtCore.QCoreApplication.processEvents()
                

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(483, 410)
        MainWindow.setMinimumSize(QtCore.QSize(0, 410))
        MainWindow.setMaximumSize(QtCore.QSize(1000, 410))
        font = QtGui.QFont()
        font.setFamily("Poppins Medium")
        font.setPointSize(10)
        MainWindow.setFont(font)
        MainWindow.setWindowOpacity(0.95)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.gridLayout.addLayout(self.horizontalLayout, 6, 0, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setMinimumSize(QtCore.QSize(75, 0))
        self.label_6.setMaximumSize(QtCore.QSize(75, 16777215))
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_5.addWidget(self.label_6)
        self.spinBox_2 = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox_2.setMinimum(-999999999)
        self.spinBox_2.setMaximum(999999999)
        self.spinBox_2.setObjectName("spinBox_2")
        self.horizontalLayout_5.addWidget(self.spinBox_2)
        self.gridLayout.addLayout(self.horizontalLayout_5, 2, 0, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setChecked(False)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 3, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setMinimumSize(QtCore.QSize(75, 0))
        self.label_7.setMaximumSize(QtCore.QSize(75, 16777215))
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_2.addWidget(self.label_7)
        self.doubleSpinBox_3 = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_3.setPrefix("")
        self.doubleSpinBox_3.setDecimals(0)
        self.doubleSpinBox_3.setMaximum(10000.0)
        self.doubleSpinBox_3.setSingleStep(50.0)
        self.doubleSpinBox_3.setProperty("value", 100.0)
        self.doubleSpinBox_3.setObjectName("doubleSpinBox_3")
        self.horizontalLayout_2.addWidget(self.doubleSpinBox_3)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setMinimumSize(QtCore.QSize(0, 190))
        self.tabWidget.setMaximumSize(QtCore.QSize(16777215, 180))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 1, 0, 1, 1)
        self.doubleSpinBox_4 = QtWidgets.QDoubleSpinBox(self.tab)
        self.doubleSpinBox_4.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.doubleSpinBox_4.setDecimals(2)
        self.doubleSpinBox_4.setMaximum(100.0)
        self.doubleSpinBox_4.setProperty("value", 1.0)
        self.doubleSpinBox_4.setObjectName("doubleSpinBox_4")
        self.gridLayout_3.addWidget(self.doubleSpinBox_4, 1, 1, 1, 1)
        self.doubleSpinBox_5 = QtWidgets.QDoubleSpinBox(self.tab)
        self.doubleSpinBox_5.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.doubleSpinBox_5.setDecimals(2)
        self.doubleSpinBox_5.setMaximum(100.0)
        self.doubleSpinBox_5.setProperty("value", 3.0)
        self.doubleSpinBox_5.setObjectName("doubleSpinBox_5")
        self.gridLayout_3.addWidget(self.doubleSpinBox_5, 2, 1, 1, 1)
        self.horizontalSlider_2 = QtWidgets.QSlider(self.tab)
        self.horizontalSlider_2.setMaximum(10000)
        self.horizontalSlider_2.setSingleStep(100)
        self.horizontalSlider_2.setProperty("value", 100)
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        self.gridLayout_3.addWidget(self.horizontalSlider_2, 1, 2, 1, 1)
        self.horizontalSlider = QtWidgets.QSlider(self.tab)
        self.horizontalSlider.setMaximum(28)
        self.horizontalSlider.setProperty("value", 8)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.gridLayout_3.addWidget(self.horizontalSlider, 0, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setMinimumSize(QtCore.QSize(110, 0))
        self.label_3.setMaximumSize(QtCore.QSize(110, 16777215))
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 2, 0, 1, 1)
        self.horizontalSlider_3 = QtWidgets.QSlider(self.tab)
        self.horizontalSlider_3.setMaximum(10000)
        self.horizontalSlider_3.setSingleStep(100)
        self.horizontalSlider_3.setProperty("value", 300)
        self.horizontalSlider_3.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_3.setObjectName("horizontalSlider_3")
        self.gridLayout_3.addWidget(self.horizontalSlider_3, 2, 2, 1, 1)
        self.doubleSpinBox_2 = QtWidgets.QDoubleSpinBox(self.tab)
        self.doubleSpinBox_2.setMinimumSize(QtCore.QSize(70, 0))
        self.doubleSpinBox_2.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.doubleSpinBox_2.setMaximum(100.0)
        self.doubleSpinBox_2.setProperty("value", 2.0)
        self.doubleSpinBox_2.setObjectName("doubleSpinBox_2")
        self.gridLayout_3.addWidget(self.doubleSpinBox_2, 0, 1, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_8 = QtWidgets.QLabel(self.tab_2)
        self.label_8.setMinimumSize(QtCore.QSize(80, 0))
        self.label_8.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_8.setObjectName("label_8")
        self.gridLayout_2.addWidget(self.label_8, 1, 0, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.tab_2)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout_2.addWidget(self.lineEdit_2, 0, 1, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout_2.addWidget(self.lineEdit, 1, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.tab_2)
        self.label_4.setMinimumSize(QtCore.QSize(80, 0))
        self.label_4.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 3, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.tab_2)
        self.label_9.setMinimumSize(QtCore.QSize(80, 0))
        self.label_9.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_9.setObjectName("label_9")
        self.gridLayout_2.addWidget(self.label_9, 0, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.tab_2)
        self.label_10.setMinimumSize(QtCore.QSize(80, 0))
        self.label_10.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_10.setObjectName("label_10")
        self.gridLayout_2.addWidget(self.label_10, 2, 0, 1, 1)
        self.comboBox_2 = QtWidgets.QComboBox(self.tab_2)
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.gridLayout_2.addWidget(self.comboBox_2, 2, 1, 1, 1)
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(self.tab_2)
        self.doubleSpinBox.setDecimals(4)
        self.doubleSpinBox.setProperty("value", 2.5)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.gridLayout_2.addWidget(self.doubleSpinBox, 3, 1, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout.addWidget(self.tabWidget, 4, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setMinimumSize(QtCore.QSize(75, 0))
        self.label_5.setMaximumSize(QtCore.QSize(75, 16777215))
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_4.addWidget(self.label_5)
        self.spinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox.setMinimum(-999999999)
        self.spinBox.setMaximum(999999999)
        self.spinBox.setObjectName("spinBox")
        self.horizontalLayout_4.addWidget(self.spinBox)
        self.gridLayout.addLayout(self.horizontalLayout_4, 1, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CursorTrace - Config"))
        self.pushButton.setText(_translate("MainWindow", "Start"))
        self.pushButton_3.setText(_translate("MainWindow", "Exit"))
        self.label_6.setText(_translate("MainWindow", "Y Position"))
        self.checkBox.setText(_translate("MainWindow", "Transparent Preview"))
        self.label_7.setText(_translate("MainWindow", "Scale"))
        self.doubleSpinBox_3.setSuffix(_translate("MainWindow", "%"))
        self.label.setText(_translate("MainWindow", "Sigma"))
        self.label_2.setText(_translate("MainWindow", "Low Threshold"))
        self.doubleSpinBox_4.setSuffix(_translate("MainWindow", "%"))
        self.doubleSpinBox_5.setSuffix(_translate("MainWindow", "%"))
        self.label_3.setText(_translate("MainWindow", "High Threshold"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Edge Detect"))
        self.label_8.setText(_translate("MainWindow", "Pause"))
        self.lineEdit_2.setText(_translate("MainWindow", "<ctrl>+<alt>+1"))
        self.lineEdit.setText(_translate("MainWindow", "<ctrl>+<alt>+2"))
        self.label_4.setText(_translate("MainWindow", "Pixel Delay"))
        self.label_9.setText(_translate("MainWindow", "Stop"))
        self.label_10.setText(_translate("MainWindow", "Button"))
        self.comboBox_2.setItemText(0, _translate("MainWindow", "Left"))
        self.comboBox_2.setItemText(1, _translate("MainWindow", "Right"))
        self.comboBox_2.setItemText(2, _translate("MainWindow", "Middle"))
        self.doubleSpinBox.setSuffix(_translate("MainWindow", "ms"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Drawing"))
        self.label_5.setText(_translate("MainWindow", "X Position"))

def detect_darkmode_in_windows(): 
    try:
        import winreg
    except ImportError:
        return False
    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    reg_keypath = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
    try:
        reg_key = winreg.OpenKey(registry, reg_keypath)
    except FileNotFoundError:
        return False

    for i in range(1024):
        try:
            value_name, value, _ = winreg.EnumValue(reg_key, i)
            if value_name == 'AppsUseLightTheme':
                return value == 0
        except OSError:
            break
    return False

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    if detect_darkmode_in_windows():
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(25,35,45))
        palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(39, 49, 58))
        palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(25,35,45))
        palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(25,35,45))
        palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.blue)
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(20, 129, 216))
        palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        app.setPalette(palette)
    
    QtGui.QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(sys.argv[0]).replace('/', '\\'), 'fonts\\Poppins Medium.ttf'))
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.setconnections()
    MainWindow.show()
    sys.exit(app.exec_())
