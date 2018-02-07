import os
import traceback
import wave
from enum import Enum

import numpy
from PyQt5.QtCore import QUrl, QTimer, QDir, QModelIndex, QFile, QTextStream
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QMainWindow, QFileSystemModel, QMessageBox, QMenu, QAction, QFontDialog

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtGui import QActionEvent, QFont, QFontInfo

from nlp import tokenizer
from qt_ui.MainWindow import Ui_MainWindow


class Window(QMainWindow):
    save_crop_signal = pyqtSignal()

    samling_ratio = 60

    class State(Enum):
        Initial = 1
        OneCursorPlaced = 2
        TwoCursorPlaced = 3

    def __init__(self):

        super().__init__()
        self.last_audio_file = None
        self.player = QMediaPlayer()
        self.sentence_tokens = []
        self.wave = None
        self.crop_count = 0
        self.ui = Ui_MainWindow()
        # setup main Window's UI
        self.ui.setupUi(self)
        self._setup_connections()
        self._setup_matplotlib()
        self._setup_directory_browser()
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self.plot_animator)
        self.ymax = 30000
        self.state = None
        self.crop_line_1_pos = None
        self.crop_line_2_pos = None
        self.play_limit = (0, 0)
        self.current_zoom = 100
        self.seconds_to_prefetch = 27
        self.minimum_file_file_length = 1.0
        self.save_crop_signal.connect(self.save_crop_to_file)
        self.ui.widget_tab.currentChanged.connect(self.tab_changed)
        self.ui.text_edit.textChanged.connect(self.text_editor_changed)
        self._setup_document_editor()
        self.settings = QSettings()
        self._setup_from_settings()
        self.preeti = QFont("./preetiTTf")

    def _setup_matplotlib(self):

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout = self.ui.graph_widget.layout()
        layout.addWidget(self.canvas)
        self.canvas_click_connection = None
        self.canvas_scroll_connection = None
        self.subplot = self.figure.add_subplot(111)

        self.audio_plot, = self.subplot.plot([0], [0], '-', color=(0.70, 0.70, 0.70))
        self.playIndicator, = self.subplot.plot([0], [0], '^')
        self.crop_line_1, = self.subplot.plot([], [], '-r')
        self.crop_line_2, = self.subplot.plot([], [], '-r')
        self.ui.vertical_splitter.setSizes([2, 12])

    def _setup_directory_browser(self):
        curdir = os.path.abspath(os.path.curdir)
        self.file_system_model = QFileSystemModel(self)
        self.file_system_model.setReadOnly(True)
        self.file_system_model.setFilter(QDir.AllDirs | QDir.AllEntries | QDir.NoDotAndDotDot)
        self.file_system_model.setNameFilters(['*.wav', '*.txt'])
        self.file_system_model.setNameFilterDisables(False)

        self.ui.directory_view.setModel(self.file_system_model)
        self.file_system_model.setRootPath(curdir)
        index = self.file_system_model.index(curdir)
        self.ui.directory_view.setRootIndex(index)
        self.ui.directory_view.hideColumn(1)
        self.ui.directory_view.hideColumn(2)
        self.ui.directory_view.hideColumn(3)
        # index: QModelIndex = model.index(os.path.abspath(os.path.curdir))
        # self.ui.directory_view.expand(index);
        # self.ui.directory_view.scrollTo(index)
        # self.ui.directory_view.setCurrentIndex(index)
        self.ui.directory_view.doubleClicked.connect(self.file_selected)

    def _setup_document_editor(self):
        self.ui.text_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.text_edit.customContextMenuRequested.connect(self.text_edit_context_menu)

    def _setup_from_settings(self):
        self.settings.sync()
        try:
            if self.settings.value("text-file"):
                self.read_text(self.settings.value("text-file"))

            if self.settings.value("audio-file"):
                if self.settings.value("audio-pos"):
                    if self.settings.value("crop-count"):
                        self.read_audio(self.settings.value("audio-file"), int(self.settings.value("audio-pos")))
                        self.crop_count = int(self.settings.value("crop-count"))
                        self.show_line(self.crop_count + 1)
                    else:
                        self.read_audio(self.settings.value("audio-file"))
                else:
                    self.read_audio(self.settings.value("audio-file"))
        except:
            QMessageBox.warning(self, "Unexpected",
                                "Last opened files may have been deleted. Thus they were not loaded.", QMessageBox.Ok)
        print('', end='')

    def plot(self, ydata_byte, start_pos=0):
        ''' plot some random stuff '''
        ploty = numpy.fromstring(ydata_byte, numpy.int16)
        plotdatay = ploty[0:len(ploty):Window.samling_ratio]
        plotdatax = [x for x in range(start_pos, len(ploty) + start_pos, Window.samling_ratio)]

        self.set_view_range(start_pos - 1000, plotdatax[-1])
        self.view_limit_range = (start_pos, plotdatax[-1])
        _max = max(plotdatay)
        self.figure.get_axes()[0].set_ylim(-_max, _max)
        self.ymax = _max
        self.audio_plot.set_data(plotdatax, plotdatay)

        self.crop_line_1_pos = plotdatax[0]
        self.crop_line_1.set_data([self.crop_line_1_pos, self.crop_line_1_pos], [-_max, _max])
        self.crop_line_1.set_color("green")
        # refresh canvas
        self.state = Window.State.OneCursorPlaced
        self.canvas.draw()

    def set_view_range(self, start, end):
        self.figure.get_axes()[0].set_xlim(start, end)
        self.current_view = [start, end]

    def plot_animator(self):

        # current_music_time = self.play_started_audio_time + diff
        current_time_ms = self.player.position()
        current_music_frame = int((current_time_ms * self.wave.getframerate()) / 1000)

        self.playIndicator.set_data([current_music_frame], [0])
        self.canvas.draw()
        if current_time_ms >= self.play_limit[1]:
            self.player.pause()
            self.play_timer.stop()
            self.playIndicator.set_data(self.crop_line_2_pos, 0)
        self.canvas.draw()

    def _setup_connections(self):
        self.player.stateChanged.connect(self.player_status_changed)
        self.player.positionChanged.connect(self.playback_progress_change)

    def toggle_pause(self):
        if self.playing:
            self.player.pause()
            self.play_timer.stop()
        else:
            self.player.play()
            self.play_timer.start()
        self.playing = not self.playing

    def seek(self, pos):
        self.player.setPosition(pos)
        self.player.play()
        if self.player.state() != QMediaPlayer.PlayingState:
            self.player.play()
        if not self.play_timer.isActive():
            self.play_timer.start()

    def seek_frame(self, frame_pos):
        self.seek(int((frame_pos * 1000) / (self.wave.getframerate())))
        # self.seek(int(frame_pos / (self.wave.getframerate() * 1000)))

    def canvas_click_listener(self, event):
        if not event.xdata:
            return
        currentframe = event.xdata
        current_time_in_milli = int(currentframe / self.wave.getframerate() * 1000)
        if (current_time_in_milli < 0):
            current_time_in_milli = 0
        current_x = int(event.xdata)
        if (current_x < (self.data_shift // 2)):
            current_x = self.data_shift // 2

        if self.state == Window.State.Initial:
            self.crop_line_1.set_data([current_x, current_x], [-self.ymax, self.ymax])
            self.crop_line_1_pos = current_x
        elif self.state == Window.State.OneCursorPlaced:
            if current_x > self.crop_line_1_pos:
                self.crop_line_2_pos = current_x
                self.crop_line_2.set_data([current_x, current_x], [-self.ymax, self.ymax])
        self.canvas.draw()
        self.seek(current_time_in_milli)

    def canvas_scroll_listener(self, event):
        current_range = self.current_view[1] - self.current_view[0]
        if current_range < 0:
            return
        if event.button == 'down':
            new_range = current_range / 1.3
        else:
            new_range = current_range * 1.3

        new_view = [event.xdata - new_range / 2, event.xdata + new_range / 2]
        count = 0
        if new_view[0] < self.view_limit_range[0]:
            new_view[1] += self.view_limit_range[0] - new_view[0]
            new_view[0] = self.view_limit_range[0]
            if new_view[1] > self.view_limit_range[1]:
                new_view[1] = self.view_limit_range[1]

        elif new_view[1] > self.view_limit_range[1]:
            new_view[0] -= new_view[1] - self.view_limit_range[1]
            new_view[1] = self.view_limit_range[1]
            if new_view[0] < self.view_limit_range[0]:
                new_view[0] = self.view_limit_range[0]
        if new_view[0] > new_view[1]:
            return
        self.figure.get_axes()[0].set_xlim(new_view[0] - 1000, new_view[1] + 1000)
        self.current_view = new_view
        self.canvas.draw()

    def eventFilter(self, event):

        return False

    def keyPressEvent(self, event):

        key = event.key()
        if key == Qt.Key_Space:
            self.toggle_pause()
        if key == Qt.Key_Return:

            if self.state == Window.State.Initial:
                if self.crop_line_1_pos:
                    self.state = Window.State.OneCursorPlaced
                    self.crop_line_1.set_data([self.crop_line_1_pos, self.crop_line_1_pos], [-self.ymax, self.ymax])
                    self.crop_line_1.set_color("green")
                    self.canvas.draw()

            elif self.state == Window.State.OneCursorPlaced:
                if self.crop_line_2_pos:
                    self.crop_line_2.set_color("green")
                    self.zoom_to_crop()
                    self.state = Window.State.TwoCursorPlaced
                    self.seek_frame(self.crop_line_2_pos - self.wave.getframerate() // 2)
                    self.ui.statusbar.showMessage("Hit 'Enter' to save the clip to file", 3000)

            elif self.state == Window.State.TwoCursorPlaced:
                self.update_cropped_plot()

        if key == Qt.Key_Backspace:
            if self.state == Window.State.OneCursorPlaced:
                self.state = Window.State.Initial
                self.crop_line_1_pos = None
                self.crop_line_1.set_color("red")
                self.crop_line_2.set_data([], [])
                self.canvas.draw()
            elif self.state == Window.State.TwoCursorPlaced:

                self.play_limit = self.play_limit_bak
                self.state = Window.State.OneCursorPlaced
                self.crop_line_2_pos = None
                self.crop_line_2.set_color("red")
                self.canvas.draw()

    def show_line(self, line_no):
        if self.sentence_tokens:
            line_index = line_no - 1
            if line_index >= len(self.sentence_tokens):
                self.ui.text_browser.setPlainText("-- No more text to display --")
            else:
                self.ui.text_browser.setPlainText(self.sentence_tokens[line_index])
        else:
            self.ui.text_browser.setPlainText("-- Text file not loaded --")

    @pyqtSlot(QMediaPlayer.State)
    def player_status_changed(self, x):
        if x == QMediaPlayer.StoppedState:
            self.play_timer.stop()
            pass
        elif x == QMediaPlayer.PlayingState:
            pass
        elif x == QMediaPlayer.PausedState:
            pass

    @pyqtSlot('qint64')
    def playback_progress_change(self, position):
        pass
        # self.ui.progressBar.setValue(int(position / self.player.duration() * 100))

    def read_audio(self, filename, pos=0):

        if self.wave:
            if filename == self.last_audio_file:
                return
            elif QMessageBox.question(self, "Warning",
                                      "If you open a new file, You cannot continue the progress of this file.\n So open new file only when you are done with this file\n Are you done with this file?",
                                      QMessageBox.Yes | QMessageBox.No | QMessageBox.Warning
                                      ) == QMessageBox.No:
                return

            self.wave.close()
        self.playing = False
        print("reading new file")
        self.last_audio_file = os.path.abspath(filename)
        # reset the cursors to default values
        self.wave = wave.open(filename, 'rb')
        self.channels = self.wave.getnchannels()
        self.rate = self.wave.getframerate()
        self.wave.setpos(pos)
        nframes = self.seconds_to_prefetch * self.wave.getframerate()

        self.data = self.wave.readframes(nframes)
        self.total_frames_read = pos + len(self.data) // 2

        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
        if pos:
            self.seek_frame(pos)
        nframes = min(self.wave.getnframes(), nframes)
        self.data_shift = pos * 2
        pos_1 = (pos * 1000) / self.wave.getframerate()
        pos_2 = pos_1 + ((nframes * 1000) / self.wave.getframerate())
        self.play_limit = (pos_1, pos_2)
        self.crop_count = 0
        self.current_open_file_name = filename[:-4]

        self.toggle_pause()
        if not self.canvas_scroll_connection:
            self.canvas_click_connection = self.canvas.mpl_connect("button_press_event", self.canvas_click_listener)
            self.canvas_scroll_connection = self.canvas.mpl_connect("scroll_event", self.canvas_scroll_listener)

        self.plot(self.data, pos)
        self.crop_line_2_pos = None
        self.crop_line_2.set_data([], [])
        self.crop_line_2.set_color("red")
        if self.sentence_tokens:
            if self.sentence_tokens:
                self.show_line(1)
        else:
            self.ui.text_browser.setPlainText("-----Please open a text file to view it's content------")
        self.player.play()
        return True

    def read_text(self, filename):
        self.text_file = QFile(filename)
        if not self.text_file.open(QFile.ReadOnly | QFile.Text):
            QMessageBox.warning(self, "Application", "Cannot read file " + self.text_file.errorString(), QMessageBox.Ok)
            return
        in_stream = QTextStream(self.text_file)
        # self.ui.text_edit.setPlainText(in_stream.readAll())

        # font: QFont = self.ui.text_browser.font()
        # font.setPixelSize(40)
        # self.ui.text_browser.setFont(font)
        data = in_stream.readAll()
        self.sentence_tokens = tokenizer.nepali_tokenizer.tokenize(data)
        if self.wave:
            if self.crop_count >= len(self.sentence_tokens):
                self.ui.text_browse.setPlainText("-----Please open a text file to view it's content------")
            else:
                self.ui.text_browser.setPlainText(self.sentence_tokens[self.crop_count])
        else:
            self.ui.text_browser.setPlainText('\n\n'.join(self.sentence_tokens))
        self.ui.text_edit.setPlainText(data)
        self.text_file.close()

    def zoom_to_crop(self):
        ##TODO : make crop from line1 and line2 position
        self.set_view_range(self.crop_line_1_pos - 1000, self.crop_line_2_pos + self.wave.getframerate() * 2)
        # cropped_data = self.data[self.crop_line_1_pos:self.crop_line_2_pos]
        self.play_limit_bak = self.play_limit
        self.play_limit = ((self.crop_line_1_pos * 1000) / self.wave.getframerate(),
                           (1000 * self.crop_line_2_pos) / self.wave.getframerate())
        self.seek_frame(self.crop_line_1_pos)
        self.canvas.draw()

    def update_cropped_plot(self):
        # frames remain in the total sound clip
        self.crop_nchannel = self.wave.getnchannels()
        self.crop_stampwidth = self.wave.getsampwidth()
        self.crop_framerate = self.wave.getframerate()
        self.audio_pos = self.crop_line_2_pos + 1

        remaining_frames = (self.wave.getnframes()) - int(self.crop_line_2_pos)
        # time remain for compleliton of sound clip
        remaining_ms = (remaining_frames * 1000) / self.wave.getframerate()

        if remaining_ms < 1000:
            return self.crop_completed(remaining_ms)

        # the no of frames that will remain after crop in the memory
        frames_in_memory = int(self.total_frames_read - self.crop_line_2_pos)
        # the starting position of current data in bytes
        data_crop_line_1 = int(self.crop_line_1_pos * 2 - self.data_shift)
        data_crop_line_2 = int(self.crop_line_2_pos * 2 - self.data_shift)
        self.crop_to_save = self.data[data_crop_line_1:data_crop_line_2]
        # byte value for the data shift in memory
        self.data_shift = self.crop_line_2_pos * 2

        # the no of maximum frames that will be showed in preview
        total_frames_required = self.seconds_to_prefetch * self.wave.getframerate()
        # the no of frames that needs to be read from disk
        frames_to_read = total_frames_required - frames_in_memory
        if frames_to_read > 0:
            # the file may not have that many frames, so it's the minimun of frames to read and frames in disk remain
            #  to read
            frames_that_will_be_read = min(self.wave.getnframes() - self.total_frames_read, frames_to_read)

            self.total_frames_read += frames_that_will_be_read
            self.data = self.data[data_crop_line_2:len(self.data)] + self.wave.readframes(frames_that_will_be_read)
        else:
            self.data = self.data[data_crop_line_2:len(self.data)]

        # frames_remain_to_read = self.wave.getnframes() - self.total_frames_read
        self.play_limit = ((self.crop_line_2_pos * 1000) / self.wave.getframerate(),
                           (self.total_frames_read * 1000) / self.wave.getframerate())
        self.view_limit_range = (self.crop_line_2_pos, self.total_frames_read)
        self.seek_frame(self.crop_line_2_pos)

        self.plot(self.data, self.crop_line_2_pos)
        self.crop_line_2.set_data([], [])
        self.crop_line_2.set_color("red")
        self.crop_line_2_pos = None
        self.save_crop_signal.emit()

    @pyqtSlot(QModelIndex)
    def file_selected(self, index):
        try:
            filename = self.file_system_model.filePath(index)
            if filename.endswith('.txt'):
                self.read_text(filename)
                self.settings.setValue("text-file", filename)
            elif self.read_audio(filename):
                self.settings.setValue("audio-file", filename)
                self.settings.setValue("crop-count", 0)
                self.settings.setValue("audio-pos", 0)
                self.settings.sync()

        except:
            traceback.print_exc(2)
            self.ui.statusbar.showMessage("Reading the file failed", 300)

    @pyqtSlot()
    def save_crop_to_file(self):
        self.crop_count += 1
        self.show_line(self.crop_count + 1)
        # strip the .wav.
        file = self.current_open_file_name[:-4]
        if not os.path.exists(file+os.path.sep):
            os.makedirs(file+os.path.sep)
        file_to_save = os.path.join(file, "crop_" + str(self.crop_count) + '.wav')

        wave_file = wave.open(file_to_save, 'wb')
        wave_file.setnchannels(self.crop_nchannel)
        wave_file.setsampwidth(self.crop_stampwidth)
        wave_file.setframerate(self.crop_framerate)
        wave_file.writeframes(self.crop_to_save)
        wave_file.close()
        self.settings.setValue("crop-count", self.crop_count)
        self.settings.setValue("audio-pos", self.audio_pos)
        self.settings.sync()

    def save_edited_text_to_file(self, text: str):
        f = open(self.text_file.fileName(), "w")
        f.write(text)
        f.close()

    def crop_completed(self, remaining_ms):
        self.state = Window.State.Initial
        self.crop_line_1.set_data([], [])
        self.crop_line_2.set_data([], [])
        self.crop_line_1.set_color("red")
        self.crop_line_2.set_color("red")
        self.crop_line_1_pos = None
        self.crop_line_2_pos = None
        self.audio_plot.set_data([], [])
        self.ui.statusbar.showMessage("Cropping this file has been completed")
        self.canvas.mpl_disconnect(self.canvas_click_connection)
        self.canvas.mpl_disconnect(self.canvas_scroll_connection)
        self.canvas_scroll_connection = None
        self.canvas_click_connection = None
        self.canvas.draw()
        self.player.stop()
        self.play_timer.stop()
        self.wave.close()
        self.wave = None
        self.ui.statusbar.showMessage(
            "Only %f seconds left thus this file is considered completed" % (remaining_ms / 1000))
        self.settings.setValue('audio-file', None)
        self.settings.sync()

    @pyqtSlot(int)
    def tab_changed(self, tab_index):
        if tab_index == 0:
            if self.text_edited:
                self.save_edited_text_to_file(self.ui.text_edit.toPlainText())
                self.sentence_tokens = tokenizer.nepali_tokenizer.tokenize(self.ui.text_edit.toPlainText())
                self.show_line(self.crop_count + 1)
        if tab_index == 1:
            if tab_index == 1:
                self.text_edited = False

    @pyqtSlot()
    def text_editor_changed(self):
        self.text_edited = True

    @pyqtSlot()
    def close(self):
        self.settings.sync()
        if not self.canvas_scroll_connection:
            self.canvas.mpl_disconnect(self.canvas_click_connection)
            self.canvas.mpl_disconnect(self.canvas_scroll_connection)
        super()

    @pyqtSlot(QPoint)
    def text_edit_context_menu(self, point: QPoint):
        print(point.x(), point.y())
        _global = self.ui.text_edit.mapToGlobal(point)
        # contextMenu=QMenu("Context menu", self.ui.text_edit)
        contextMenu = self.ui.text_edit.createStandardContextMenu()
        contextMenu.addAction("Select Font", self.select_font)
        contextMenu.setFont(self.font())
        contextMenu.exec(_global);

    @pyqtSlot()
    def select_font(self):
        font, ok = QFontDialog.getFont(self)

        if ok:
            params = font.toString().split(",")
            self.ui.text_edit.setStyleSheet("font-family :%s;font-size:%spt;" % (params[0], params[1]))
            self.ui.text_browser.setStyleSheet("font-family :%s;font-size:%spt;" % (params[0], params[1]))
