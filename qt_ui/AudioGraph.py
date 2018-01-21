from PyQt5.QtWidgets import QMainWindow, QWidget
import random
import pyaudio
import wave
from datetime import datetime
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot, QUrl
from qt_ui.MainWindow import Ui_MainWindow
from PyQt5.QtMultimedia import (QAudioInput, QAudioOutput, QAudioRecorder, QAudioDeviceInfo,
                                QAudio, QMediaPlayer, QAudioEncoderSettings, QMultimedia,
                                QMediaContent
                                )
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPaintEvent, QPainter, QPen
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class AudioGraph(QWidget):

    def __init__(self,parent=None):
        super().__init__(parent)
        self.wave = None
        self.data = None
        self.channels = 0
        self.rate = 0
        self.position = 0
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.canvas.mpl_connect("button_press_event", self.canvas_click_listener)

    def setFile(self, filename):
        self.wave = wave.open(filename, 'rb')
        self.channels = self.wave.getnchannels()
        self.rate = self.wave.getframerate()
        self.seek(0);

    def seek(self, pos):
        self.wave.setpos(pos)

    def canvas_click_listener(self, event):
        pass

    def plot(self):
        ''' plot some random stuff '''
        # random data

        data = [random.randint(-8000, 8000) for i in range(1000)]

        # create an axis

        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.clear()
        ax.axis([0, 1000, -8000, 8000])
        # plot data
        ax.plot(data, '-')
        self.figure.tight_layout()
        # refresh canvas
        self.canvas.draw()

    def setData(data):
        pass
