from PyQt5.QtWidgets import QMainWindow, QWidget

from datetime import datetime
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot, QUrl
from qt_ui.MainWindow import Ui_MainWindow
from PyQt5.QtMultimedia import (QAudioInput, QAudioOutput, QAudioRecorder, QAudioDeviceInfo,
                                QAudio, QMediaPlayer, QAudioEncoderSettings, QMultimedia,
                                QMediaContent
                                )
from PyQt5.QtGui import QPaintEvent
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot

class AudioGraph(QWidget):
    def __init__(self):
        super.__init__()
    def paintEvent(self, paint_event:QPaintEvent):
        paint_event.
