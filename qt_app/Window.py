from PyQt5.QtWidgets import QMainWindow, QWidget

from datetime import datetime
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot, QUrl
from qt_ui.MainWindow import Ui_MainWindow
from PyQt5.QtMultimedia import (QAudioInput, QAudioOutput, QAudioRecorder, QAudioDeviceInfo,
                                QAudio, QMediaPlayer, QAudioEncoderSettings, QMultimedia,
                                QMediaContent
                                )
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot


class Window(QMainWindow):
    login_request_signal = pyqtSignal([str, str])
    like_activate_signal = pyqtSignal(float)
    comment_activate_signal = pyqtSignal(list, float)
    follow_activate_signal = pyqtSignal(list, float)
    unfollow_activate_signal = pyqtSignal(list, float)

    like_stop_signal = pyqtSignal()
    comment_stop_signal = pyqtSignal()
    follow_stop_signal = pyqtSignal()
    unfollow_stop_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()

        self.player.setMedia(QMediaContent(QUrl.fromLocalFile("/home/paradox/Music/tomorrow.mp3")))
        self.player.setVolume(50)
        self.player.stateChanged.connect(self.player_status_changed)
        self.player.positionChanged.connect(self.playback_progress_change)

        self.recorder = QAudioRecorder(self)
        self.audioSettings = QAudioEncoderSettings()
        self.audioSettings.setCodec("audio/amr")
        self.audioSettings.setQuality(QMultimedia.HighQuality)

        self.audioRecorder = QAudioRecorder()
        self.audioRecorder.setEncodingSettings(self.audioSettings)
        self.audioRecorder.setOutputLocation(QUrl.fromLocalFile("test.amr"))
        self.ui = Ui_MainWindow()
        self.recording = False
        self.recordPause = False
        # setup main Window's UI
        self.ui.setupUi(self)
        self.player.play()

    def setup_connections(self):


    @pyqtSlot(str)
    def log(self, logText: str):
        self.ui.logBrowser.setPlainText(self.ui.logBrowser.toPlainText() + '\n' + logText)
        self.ui.logBrowser.verticalScrollBar().setSliderPosition(
            self.ui.logBrowser.verticalScrollBar().maximum()
        )

    def selfLog(self, *args) -> None:
        '''
         For logging window's activities,
         Good programming would be : the async_bot being responsible to genere all the necessary log.
         But that's not happening, so window is logging some of the activities.
        :param args:
        :return:
        '''
        args = list(args)
        log = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for logUnit in args:
            log += ' > ' + logUnit
        self.log(log)

    def toggle_pause(self):
        if self.recording:
            self.recorder.pause()
        else:
            self.recorder.record()
        self.recording = not self.recording

    def toggle_stop(self):
        if self.recordPause:
            self.recorder.record()
        else:
            self.recorder.stop()
        self.recordPause = not self.recordPause

    def seek(self):
        print("Total durationn :", self.player.duration())
        try:
            i = int(self.ui.input_seek.text())
            self.player.setPosition(i)
            if self.player.state() == QMediaPlayer.StoppedState:
                self.player.play()
        except ValueError:
            pass

    @pyqtSlot(QMediaPlayer.State)
    def player_status_changed(self, x):
        if x == QMediaPlayer.StoppedState:
            pass
        elif x == QMediaPlayer.PlayingState:
            pass
        elif x == QMediaPlayer.PausedState:
            pass
    @pyqtSlot('qint64')
    def playback_progress_change(self,position):
        print(position)
        self.ui.progressBar.setValue(int(position/self.player.duration()*100))
