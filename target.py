from PyQt4.QtCore import *
from PyQt4.QtGui import *
class TargetAlarm(QGraphicsObject):
    def __init__ (self, x , y, size):
        QGraphicsItem.__init__(self)
        self.x=x
        self.y=y
        self.k=3
        self.size=size*self.k

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setAcceptDrops(True) #разрешаем таскать
        self.setAcceptHoverEvents (True)
        #self.setFlag(QGraphicsItem.ItemIsMovable)
        print("InitTerget")
    def paint(self, painter, option=None, widget=None):
        rect = QRect(self.x,self.y,self.size,self.size)
        painter.setRenderHint(QPainter.Antialiasing, True)
        pen= QPen(QColor(Qt.black))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawEllipse(rect)
        pen.setWidth(3)
        painter.setPen(pen)

        painter.drawPoint(self.size/2,self.size/2)
        pen.setColor(QColor(Qt.red))
        pen.setWidth(2)
        painter.setPen(pen)
        k=self.k
        m=10
        x1=self.size/2
        x2=self.size/2
        y1=self.y-5
        y2=self.size/k-m
        painter.drawLine(QPointF(x1,y1),QPointF(x2,y2))
        x1=self.x-5
        x2=self.size/k-m
        y1=self.size/2
        y2=self.size/2
        painter.drawLine(QPointF(x1,y1),QPointF(x2,y2))

        x1=self.size-m
        x2=self.size+5
        y1=self.size/2
        y2=self.size/2
        painter.drawLine(QPointF(x1,y1),QPointF(x2,y2))

        y1=self.size-m
        y2=self.size+5
        x1=self.size/2
        x2=self.size/2
        painter.drawLine(QPointF(x1,y1),QPointF(x2,y2))


    def boundingRect(self):
        return QRectF(self.x-5,self.y-5,self.size+10,self.size+10)

    def animatePos(self, start, end):
        #print ('Animating..')
        self.anim = QPropertyAnimation(self, 'pos')
        self.anim.setDuration(2000)
        self.anim.setStartValue(start)
        self.anim.setEasingCurve(QEasingCurve.SineCurve)
        self.anim.setEndValue(end)
        self.anim.setLoopCount(-1)
        #self.connect(anim, SIGNAL('valueChanged(const QVariant&)'), self.go)
        self.anim.finished.connect(self.go)

        self.anim.start()

    def animateRotation(self):
        #print ('Animating..')
        self.setTransformOriginPoint(QPointF(self.size/2,self.size/2))
        self.anim1 = QPropertyAnimation(self, 'scale')
        self.anim1.setDuration(700)
        self.anim1.setStartValue(1.5)
        self.anim1.setEasingCurve(QEasingCurve.SineCurve)
        self.anim1.setEndValue(0.5)
        self.anim1.setLoopCount(-1)

        self.anim2 = QPropertyAnimation(self, 'rotation')
        self.anim2.setDuration(2000)
        self.anim2.setStartValue(0)
        self.anim2.setEasingCurve(QEasingCurve.CosineCurve)
        self.anim2.setEndValue(360)
        self.anim2.setLoopCount(-1)

        self.GroupAnimation= QParallelAnimationGroup(self)
        self.GroupAnimation.addAnimation(self.anim1)
        #self.GroupAnimation.addAnimation(self.anim2)
        self.GroupAnimation.start()
    def setPosTarget(self,x,y):
        size=self.size/3;
        x=x-size*3/2+size/2
        y=y-size*3/2+size/2
        self.setPos(x,y)
    def go(self):
        print ('EndAnimation')


