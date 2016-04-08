import time
import serial
import struct
from PyQt4 import QtCore
class x305Thread(QtCore.QThread):
    szuon=b'\x10\x03\x01\x02\x00\xda'
    szuoff=b'\x10\x03\x02\x01\x00\xda'
    WRcmd =b'\x10\x04\x01\xda'
    tk=5 # Время задержки сработки датчиков 
    level=-100
    time=0
    lines=[[level,time],[level,time],[level,time],[level,time],[level,time],[level,time],[level,time],[level,time]]
    notifyProgress = QtCore.pyqtSignal(int,int)
    enSZU = False
    indexSZU = 0
    def __init__(self, serialPort,baudratePort,timeoutPort):
        QtCore.QThread.__init__(self)
        self.dongle = serial.Serial(port=serialPort,baudrate=baudratePort,timeout=timeoutPort,rtscts=0,xonxoff=0)
    def setSZU(self,index):
        self.indexSZU= index
        self.enSZU=True


    def SZU(self):

        if(self.enSZU==True):

            s=''
            print('EnablesSZU')
            if(self.indexSZU==0):
                s=self.szuoff
                print('EnableSZU')
            else:
                s=self.szuon
                print('DisableSZU')
            self.dongle.write(s)
            s = self.dongle.readline()
            self.enSZU=False

    def run(self):
        i=0
        while True:
            i+=1
            if(i>101):
                i=1
            s=self.WRcmd
            #print('Write=',s)
            self.dongle.write(s)
            #time.sleep(0.1)
            s = self.dongle.readline()
            #print('Read = ',s[4],' ',s[5])
            if(len(s)>5):
                self.result(s)
            self.SZU()

    #Задержка от ложных сработок        
    def compare(self,level,i):
        tv=time.time()
        print(self.lines)
        if(self.lines[i][0]!=level):
            if(self.lines[i][1]==0):
                self.lines[i][1]=tv
            tmp= time.time()-self.lines[i][1]
            if(tmp>=self.tk):
                self.lines[i][1]=0
                self.lines[i][0]=level
                address=0x10*10+i+1
                self.notifyProgress.emit(address,level)
            #print('srabotka: address={} level= {}'.format(address,level))
        else:
            self.lines[i][1]=0    

    def result(self,bl):
        s=''

        if bl[0]!=0x10: return
        print(bl)
        print(bl[4:4+4])

       # Range 0-4 input X305
        for i in range(0,5):
            rf=self.bytes32ToFloat(bl[i*4+4:i*4+4+4])
       #nek 1,2,3,4
            if i in [0,1]:
                if 2.1<=rf<=2.5:
                    self.compare(2,i*2)
                    self.compare(4,i*2+1)

                elif 2.8<=rf<=3.2:
                    self.compare(4,i*2)
                    self.compare(2,i*2+1)

                elif 4.6<=rf<=5:
                    self.compare(2,i*2)
                    self.compare(2,i*2+1)

                elif 1.6<=rf<=2:
                    self.compare(4,i*2)
                    self.compare(4,i*2+1)
                else:
                    self.compare(3,i*2)
                    self.compare(3,i*2+1)
        #Rv-1,3
            if i in [2,3,4]:
                if 1.4<=rf<=2.4:
                    self.compare(2,i+2)
                elif 3.1<=rf<=4.1:
                   self.compare(4,i+2)
                else:
                    self.compare(3,i+2)
         #SSS-903m

        rf1=self.bytes32ToFloat(bl[5*4+4:5*4+4+4])
        rf2=self.bytes32ToFloat(bl[6*4+4:6*4+4+4])
        p3=bl[32]

        if 1.4<rf1<2.4:
            p1=2
        elif 3.1<rf1<4.1:
            p1=4
        else:
            p1=3
        if 1.4<rf2<2.4:
            p2=2
        elif 3.1<rf2<4.1:
            p2=4
        else:
            p2=3

        if p1==3 or p2==3 or p3==0:
            self.compare(3,7)
        elif p2==2:
            self.compare(2,7)
        elif p1==2:
            self.compare(1,7)
        else:
            self.compare(4,7)

    def func(self,num, pos):
        return (num & (1 << pos)) >> pos
    def bytes32ToFloat(self, arg):
        return struct.unpack('f',arg)[0]

    def __del__(self):
        self.dongle.close()

