import time
import serial
from PyQt4 import QtCore
class x305Thread(QtCore.QThread):
    szuon=b'\x10\x03\x01\x01\x00\xda'
    szuoff=b'\x10\x03\x02\x01\x00\xda'
    WRcmd =b'\x10\x04\x01\xda'
    tk=5 # Время задержки сработки датчиков 
    level=-100
    time=0
    lines=[[level,time],[level,time],[level,time],[level,time],[level,time],[level,time]]
    notifyProgress = QtCore.pyqtSignal(int,int)
    def __init__(self, serialPort,baudratePort,timeoutPort):
        QtCore.QThread.__init__(self)
        self.dongle = serial.Serial(port=serialPort,baudrate=baudratePort,timeout=timeoutPort,rtscts=0,xonxoff=0)
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
    #Задержка от ложных сработок        
    def compare(self,level,i):
        tv=time.time()
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
        for i in range(0,5):
            if(self.func(bl[4],i)==1):
                level=2
            else:
                level=4
            if(self.func(bl[5],i)==1):
                level=3
            s=s+' i'+str(i)+'='+str(level)
            self.compare(level,i)
        ##----SS-903
        level=4
        if(self.func(bl[4],5)==1):
            level=1
        if(self.func(bl[4],6)==1):
            level=2
        if((self.func(bl[4],7)==1)or(self.func(bl[5],5)==1)or(self.func(bl[5],6)==1)):
            level=3
        s=s+' i'+str(5)+'='+str(level)
        self.compare(level,5)
        #print('S=',s)

    def func(self,num, pos):
        return (num & (1 << pos)) >> pos
    def __del__(self):
        self.dongle.close()

