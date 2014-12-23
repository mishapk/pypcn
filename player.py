import pyaudio
from PyQt4 import QtCore
from PyQt4.QtGui import (QWidget, QGridLayout, QLabel,QLineEdit, QSlider, QToolButton, QStyle)

class MPlayer(QWidget):
    mute=False
    def __init__(self, parent=None):
        super(MPlayer, self).__init__(parent)
        grid = QGridLayout(self)
        label1 = QLabel('Датчик')
        label2 = QLabel('Сообщение')

        self.LESensor = QLineEdit()
        self.LEMessage = QLineEdit()
        self.MuteButton =QToolButton()
        self.MuteButton.setIcon( self.style().standardIcon(QStyle.SP_MediaVolume))
        self.MuteButton.clicked.connect(self.setMute)

        self.DurationSlider = QSlider(QtCore.Qt.Horizontal)
        self.VolumeSlider = QSlider(QtCore.Qt.Horizontal)
        self.VolumeSlider.setMinimum(0)
        self.VolumeSlider.setMaximum(100)
        self.VolumeSlider.setSingleStep(5)
        self.VolumeSlider.valueChanged.connect(self.setVolume)
        self.VolumeSlider.setValue(100)

        grid.addWidget(label1,0,0)
        grid.addWidget(label2,1,0)
        grid.addWidget(self.LESensor,0,1,1,3)
        grid.addWidget(self.LEMessage,1,1)
        grid.addWidget(self.MuteButton,1,2)
        grid.addWidget(self.VolumeSlider,1,3)
        grid.addWidget(self.DurationSlider,2,0,1,4)



    def PlayAudio(self,filename, loop=1):
        pass
    def Stop(self):
        pass
    def Microphone(self, mode):
        pass
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

