from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
class SensorAlarm(QGraphicsItem):
    def __init__ (self, x , y, size,level, type,sounds,commands, parent=None):
        QGraphicsItem.__init__(self, parent)
        self.x=x
        self.y=y
        self.size=size

        self.level=level
        self.type = type
        self.sounds=sounds
        self.command=commands
        #self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setAcceptDrops(True) #разрешаем таскать
        self.setAcceptHoverEvents (True)
        self.color = QColor(0,  0,  0)
        #self.setFlag(QGraphicsItem.ItemIsMovable)
    def paint(self, painter, option=None, widget=None):
        'пока просто красный крестик'
        painter.setPen(self.color)
        rect = QRect(self.x,self.y,self.size,self.size)
        color =QColor()
        if(self.level==1):
            color= QColor(0xff,0xa0,0x00)
        if(self.level==2):
            color=QColor(Qt.red)
        if(self.level in [3,33]):
            color=QColor(Qt.gray)
        if(self.level==4):
            color=QColor(Qt.green)
        if(self.type==6):
            brush=QBrush(QColor(Qt.white))

        painter.setBrush(QBrush(color))
        painter.drawRect(rect)
#uroven #1
        if(self.type==1):
            pp=QPolygonF()
            pp << QPointF(0, 0)<<QPointF(self.size,0)<<QPointF(self.size/2,self.size/2)
            brush=QBrush(QColor(Qt.white))
            painter.setBrush(brush)
            painter.drawPolygon(pp)

#Proliv #2
        if(self.type==2):
            pp=QPolygonF()
            pp << QPointF(0, 0)<<QPointF(self.size,0)<<QPointF(0,self.size)
            brush=QBrush(QColor(Qt.white))
            painter.setBrush(brush)
            painter.drawPolygon(pp)
#Davlenie #3
        if(self.type == 3):
            k=0.6
            r=self.size*k
            ap=self.size/2 - r/2
            brush=QBrush(QColor(Qt.white))
            painter.setBrush(brush)
            painter.drawEllipse(QRect(ap,ap,r,r))
#Temperatura #4
        if(self.type==4):
            k=0.3
            r=self.size*k
            apx=self.size/2 - r/2
            apy=self.size/1.4 -r/2
            brush=QBrush(QColor(Qt.white))
            painter.setBrush(brush)
            pen = QPen()
            pen.setStyle(0)
            painter.setPen(pen)
            painter.drawEllipse(QRect(apx,apy,r,r))

            r=self.size*k*0.5
            apx=self.size/2 -r/2
            apy= self.size*0.1
            painter.drawEllipse(QRect(apx,apy,r,self.size*0.75))
#Koncentracia #5
        if(self.type==5):
            ns=self.size*1
            brush=QBrush(QColor(Qt.white))
            painter.setBrush(brush)
            painter.drawChord(QRect(0,self.size/2,ns,ns),0,180*16)
#Ruthnoy Izveshatel #6
        if(self.type==6):
            brush=QBrush(QColor(Qt.white))
            pen = QPen()
            pen.setWidth(2)
            ns=self.size*1
            painter.setPen(pen)
            ns=self.size*0.5
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.drawArc(QRect(0+ns/2,-self.size/2+ns,ns,ns),0*16,-180*16)
            painter.drawLine(self.size/2,self.size/2,self.size/2,self.size-ns/4)


    def boundingRect(self):
        return QRectF(self.x,self.y,self.size,self.size)

    def animatePos(self, start, end):
        print ('Animating..')
        self.anim = QPropertyAnimation(self, 'pos')
        self.anim.setDuration(1400)
        self.anim.setStartValue(start)
        self.anim.setEasingCurve(QEasingCurve.SineCurve)
        self.anim.setEndValue(end)
        self.anim.setLoopCount(-1)
        #self.connect(anim, SIGNAL('valueChanged(const QVariant&)'), self.go)
        self.anim.finished.connect(self.go)

        self.anim.start()
    def go(self):
        print ('EndAnimation')

    def setLevel(self,level):
        self.level=level
        self.update()

