import audioop
import math

import numpy, wave, sys
import pyaudio
from PyQt4.QtCore import *
from PyQt4.QtGui import (QWidget, QFrame, QGridLayout, QLabel, QLineEdit, QSlider, QGroupBox, QCheckBox, QProgressBar,
                         QToolButton, QStyle, QSizePolicy, QPainter, QPixmap, QIcon, QColor)


class MPlayer(QWidget):
    mute=False
    def __init__(self, parent=None):
        super(MPlayer, self).__init__(parent)
        self.indicator = QProgressBar()
        self.indicator.setOrientation(Qt.Vertical)
        self.indicator.setValue(0)
        self.indicator.setStyleSheet(" QProgressBar::chunk { background: green; }")
        self.indicator.setTextVisible(False)
        grid = QGridLayout(self)
        label1 = QLabel('Датчик')
        label2 = QLabel('Сообщение')
        self.RecordDirect = QCheckBox('Прямой')
        RecordGroup = QGroupBox("Экстренный микрофон")
        grid2 = QGridLayout(RecordGroup)
        self.labelMic = QLabel('<b>Готов</b>')

        pixmap = QPixmap(80, 80)
        pixmap.fill(Qt.color0)
        painter = QPainter()
        painter.begin(pixmap)
        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(0, 0, 80, 80)
        painter.end()

        self.LESensor = QLineEdit(self)
        self.LEMessage = QLineEdit(self)
        self.MuteButton = QToolButton(self)
        self.MuteButton.setIcon( self.style().standardIcon(QStyle.SP_MediaVolume))
        self.MuteButton.clicked.connect(self.setMute)
        self.PlayButton = QToolButton(self)
        self.PlayButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.StopButton = QToolButton(self)
        self.StopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.MRButton = QToolButton(RecordGroup)
        self.MRButton.setCheckable(True)
        self.MRButton.setMaximumSize(40, 40)
        self.MRButton.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        self.MRButton.clicked.connect(self.Microphone)

        ico = QIcon()
        ico.addPixmap(pixmap, QIcon.Normal, QIcon.Off)
        ico.addPixmap(pixmap, QIcon.Normal, QIcon.On)
        self.MRButton.setIcon(ico)

        self.DurationSlider = QSlider(Qt.Horizontal)
        self.VolumeSlider = QSlider(Qt.Horizontal)
        self.VolumeSlider.setMinimum(0)
        self.VolumeSlider.setMaximum(100)
        self.VolumeSlider.setSingleStep(5)
        self.VolumeSlider.valueChanged.connect(self.setVolume)
        self.VolumeSlider.setValue(100)

        grid.addWidget(label1,0,0)
        grid.addWidget(label2,1,0)
        # grid.addWidget(label3,0,7,1,1)
        grid.addWidget(self.LESensor, 0, 1, 1, 5)
        grid.addWidget(self.LEMessage, 1, 1, 1, 5)
        grid.addWidget(self.MuteButton, 5, 3)
        grid.addWidget(self.VolumeSlider, 5, 4, 1, 2)
        grid.addWidget(self.DurationSlider, 2, 0, 1, 6)
        grid.addWidget(self.PlayButton, 5, 1)
        grid.addWidget(self.StopButton, 5, 2)

        # grid.addWidget(lineV,0,6,6,1)
        # grid.addWidget(lineV,0,7,6,1)

        grid.addWidget(self.indicator, 0, 7, 5, 1)
        grid.addWidget(RecordGroup, 0, 6, 5, 1)
        grid2.addWidget(self.MRButton, 0, 0, 2, 2)
        grid2.addWidget(self.labelMic, 0, 2)
        grid2.addWidget(self.RecordDirect, 1, 2)


    def PlayAudio(self,filename, loop=1):
        pass
    def Stop(self):
        self.MRButton.setChecked(False)


    def Microphone(self):
        self.Record = RThread(self.RecordDirect.isChecked(), self.VolumeSlider.value())
        self.Record.finished.connect(self.Stop)
        self.Record.levelProgress.connect(self.indicator.setValue)
        self.Record.start()


    def setMute(self):
        if self.mute:
            self.MuteButton.setIcon( self.style().standardIcon(QStyle.SP_MediaVolume))
            self.mute=False
            print(self.mute)
        else:
            self.MuteButton.setIcon( self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
            self.mute=True
            print(self.mute)
    def setVolume(self):
        pass


class RThread(QThread):
    levelProgress = pyqtSignal(int)

    def __init__(self, mode, value, parent=None):
        super(RThread, self).__init__(parent)
        self.mode = mode
        self.value = value


    def player(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt24
        CHANNELS = 1
        RATE = 8000
        RECORD_SECONDS = 5
        WAVE_OUTPUT_FILENAME = "output.wav"

        if sys.platform == 'darwin':
            CHANNELS = 1
        p = pyaudio.PyAudio()


        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        p2 = pyaudio.PyAudio()
        stream2 = p2.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          output=True)

        print("* recording")

        frames = []

        m = 0
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)

            decodedata = numpy.fromstring(data, numpy.int16)
            newdata = (decodedata * 1).astype(numpy.int16)
            nd = newdata.tostring()
            frames.append(nd)
            rms = audioop.max(nd, 2)
            k = rms*100/2**15

            m = max(rms, m, )
            print(k, ' ', rms, )
            self.levelProgress.emit(k)
            # http://www.qsl.net/pa2ohh/11rmsmeter.htm


            if self.mode:
                decodedata = numpy.fromstring(data, numpy.int16)
                newdata = (decodedata * 1).astype(numpy.int16)
                nd = newdata.tostring()
                # stream2.write(nd)
            else:
                pass
                # $if not self.mode:
                # for data in frames:
                # stream2.write(data)

        print("* done recording max=", m)

        stream.stop_stream()
        stream.close()
        stream2.stop_stream()
        stream2.close()
        p.terminate()
        p2.terminate()
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)

        wf.writeframes(b''.join(frames))
        wf.close()

    def run(self):
        self.player()

    def __del__(self):
        print('Ex_TH')


class RMSIndicator(QFrame):
    def __init__(self, parent=None):
        super(RMSIndicator, self).__init__(parent)
        self.setLineWidth(3)
        self.setFrameStyle(QFrame.Box | QFrame.Sunken)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)
        f = 100
        painter.drawRect(0, 0, self.width() * f, self.height());
        self.drawFrame(event, painter)
        print('Hello')


