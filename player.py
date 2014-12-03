from PyQt4.phonon import Phonon
class player():
    output = Phonon.AudioOutput(Phonon.MusicCategory,self)
    m_media = Phonon.MediaObject(self)
    Phonon.createPath(m_media, output)
    def play(self,fn):
        self.m_media.stop()
        self.m_media.setCurrentSource(Phonon.MediaSource("sounds/{}".format(fn)))
        self.m_media.play()


