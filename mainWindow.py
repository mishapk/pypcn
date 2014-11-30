#!-*-coding:utf-8-*-
import sys


from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic, QtCore, QtSql
from PyQt4.phonon import Phonon
import connection
from sensor import SensorAlarm
from target import TargetAlarm
from x305 import x305Thread
from eventmodel import QSqlQueryColorModel

( Ui_MainWindow, QMainWindow ) = uic.loadUiType('MainWindow.ui')

Mode = 0
#0- Normal, 1 - Admin


class MainWindow(QMainWindow):
    """MainWindow inherits QMainWindow"""


    def __init__(self, parent=None):
        """

        :type self: object
        """
        self.UserId=0
        QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        actions = QActionGroup(self.ui.toolBar)
        actions.addAction(self.ui.actionHome)
        actions.addAction(self.ui.actionNotify)
        actions.addAction(self.ui.actionUsers)
        actions.addAction(self.ui.actionSettings)
        actions.addAction(self.ui.actionEvents)

        mapper = QSignalMapper(self)

        self.connect(self.ui.actionHome, SIGNAL('triggered()'), mapper, SLOT('map()'))
        self.connect(self.ui.actionNotify, SIGNAL('triggered()'), mapper, SLOT('map()'))
        self.connect(self.ui.actionUsers, SIGNAL('triggered()'), mapper, SLOT('map()'))
        self.connect(self.ui.actionEvents, SIGNAL('triggered()'), mapper, SLOT('map()'))
        self.connect(self.ui.actionSettings, SIGNAL('triggered()'), mapper, SLOT('map()'))
        mapper.setMapping(self.ui.actionHome,0)
        mapper.setMapping(self.ui.actionNotify,1)
        mapper.setMapping(self.ui.actionEvents,2)
        mapper.setMapping(self.ui.actionUsers,3)
        mapper.setMapping(self.ui.actionSettings,4)

        self.connect(mapper,SIGNAL("mapped(int)"),self.ui.stackedWidget,SLOT("setCurrentIndex(int)"))
        self.ui.actionHome.setChecked(True)
        self.ui.stackedWidget.setCurrentIndex(0)
        self.timer_Widget()
        if not connection.createConnection():
            sys.exit(1)

        self.ui.frame_cs.hide()

        self.ui.graphicsView.horizontalScrollBar().setValue(900)


        self.initGraphics()
        self.CreateTableEvent()
        self.InitUserPage()
        self.ui.splitter.setStretchFactor(0,1)
        self.SaveEvent('СТАРТ системы',-1,0,self.UserId)

        #self.x305Read=x305Thread("COM7",1900,0.1)
#        self.x305Read.notifyProgress.connect(self.setAlarm)
 #       self.x305Read.start()

    def timer_Widget(self):
        timerWidget = QWidget(self)
        self.spacer = QWidget(self)
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.lcd = QLCDNumber(self)
        self.lcd.setNumDigits(8)
        self.lcd.setMinimumHeight(36)
        self.lcd.setMinimumWidth(150)
        self.dateLabel = QLabel(self)
        self.dateLabel.setText("<b>[Требуется авторизация пользователя]")
        self.dateLabel.setStyleSheet("QLabel {  color : red; }")
        layout =QVBoxLayout(timerWidget)
        layout.addWidget(self.lcd)
        layout.addWidget(self.dateLabel)
        self.ui.toolBar.addWidget(self.spacer)
        self.ui.toolBar.addWidget(timerWidget)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.showlcd)
        timer.start(1000)
        self.showlcd()

    def showlcd(self):
        time = QtCore.QTime.currentTime()
        text = time.toString('hh:mm:ss')
        self.lcd.display(text)
        #date = QtCore.QDate.currentDate()
        #text = date.toString('[dd-MM-yyyy]')
        #self.dateLabel.setText(text)
#----------HomePage-----------------------------------------------------------------------------------------------------
    def sensorSymbol(self,ids,adr,x,y,size,level,types):
        item=SensorAlarm(0,0,size,level,types)
        item.setPos(x,y)
        item.id= ids
        item.address=adr
        self.scene.addItem(item)
        self.GI.append(item)
    def initGraphics(self):
        self.scene = QGraphicsScene(self)
        self.backGround= QGraphicsPixmapItem()
        self.backGround.setPixmap(QPixmap('./images/000.jpg'))
        self.scene.setSceneRect(self.backGround.sceneBoundingRect())
        self.scene.addItem(self.backGround)
        self.GI=[]
        query = QtSql.QSqlQuery()
        query.exec_('select * from sensor where address>0;')
        size=20
        x=0
        y=0
        while query.next():

            x = query.value(4)
            y = query.value(5)
            tp= query.value(6)

            print('x=',x,'y=',y)
            ids=query.value(0)
            adr =query.value(1)

            self.sensorSymbol(ids,adr,x,y,size,3,tp)
            #


        #sna = SensorAlarm(0,0,20,2,6)
        #self.scene.addItem(sna)
        print('LoadEnd')

        self.targetAlarm = TargetAlarm(0,0,size)
        self.targetAlarm.setPos(x-size*3/2+size/2,y-size*3/2+size/2)
        self.scene.addItem(self.targetAlarm )
        self.ui.graphicsView.setScene(self.scene)
        self.CreateTableSensor()

    def saveSansors(self):
        query = QtSql.QSqlQuery()
        for p in self.GI:
            x = p.pos().x()
            y = p.pos().y()
            print('x=',x,'y=',y)
            txt='update sensor SET x={}, y={} where id={}'.format(x,y,p.id)
            if(query.exec_(txt)==False):
                print(query.lastError().text())
            #print(txt,'==>>',rec.count())
        self.tm.select()
        print('SaveEnd')

    def enableDragSensor(self):

        if(self.ui.checkBoxDragSensor.isChecked()):
            dr=True
        else:
            dr=False
        for p in self.GI:
            p.setFlag(QGraphicsItem.ItemIsMovable, dr)

    def selectSensorInTable(self):
        print('select')

    def CreateTableSensor(self):
        self.tm = QtSql.QSqlRelationalTableModel(self)
        self.tm.setTable('sensor')
        self.tm.setFilter('address > 0')
        self.tm.setRelation(6, QtSql.QSqlRelation('stype', 'id', '*'))
        self.tm.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.tm.select()
        self.ui.tableSensor.setModel(self.tm)


    def playAnimation(self):
        #x=self.item.pos().x()
        #y=self.item.pos().y()
        #self.targetAlarm.animatePos(QPointF(x-20,y-20),QPointF(x+20,y+20))
        self.setAlarm(162,2)
        output = Phonon.AudioOutput(Phonon.MusicCategory,self)
        print('volume=',output.volume())
        output.setVolume(10/100)
        m_media = Phonon.MediaObject(self)
        Phonon.createPath(m_media, output)
        m_media.setCurrentSource(Phonon.MediaSource("sounds/1.wav"))
        m_media.play()


        #self.player = Phonon.createPlayer(Phonon.MusicCategory)
        #self.player.setCurrentSource(Phonon.MediaSource("sounds/1.wav"))
        #self.player.play()

    def setAlarm(self,sensor_address, sensor_level):
        for p in self.GI:
            if(p.address==sensor_address):
                p.setLevel(sensor_level)
                x=p.pos().x()
                y=p.pos().y()
                id_s=p.id
        self.targetAlarm.setPosTarget(x,y)
        self.targetAlarm.animateRotation()
        self.ui.frame_cs.show()

        self.ui.graphicsView.centerOn(x,y)
        self.SaveEvent('Датчик',id_s,sensor_level,self.UserId)


#---------HomePage End--------------------------------------------------------------------------------------------------
#--------Event_page-----------------------------------------------------------------------------------------------------
    def CreateTableEvent(self):
        self.tableEventModel = QSqlQueryColorModel(self)
        sql='SELECT event.created,sensor.info,stype.title,level.id,level.title,event.info,user.username ' \
            'FROM  (event INNER JOIN sensor ON event.sensor_id=sensor.id) ' \
            'INNER JOIN stype ON sensor.type_id=stype.id ' \
            'INNER JOIN level ON event.level_id=level.id   ' \
            'INNER JOIN user ON event.user_id=user.id   ' \
            'ORDER BY event.id DESC LIMIT 1000'
        print(self.tableEventModel.setQuery(sql))
        """
        columns:
            0:event.created,
            1:sensor.info,
            2:stype.title,
            3:level.id,
            4:level.title,
            5:event.info,
            6:user.username 
        """

        self.ui.tableEvent.setModel(self.tableEventModel)
        self.ui.tableEvent.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableEvent.setSelectionBehavior(QAbstractItemView.SelectRows)
        #for column in range( self.tableEventModel.columnCount()):
        #    self.ui.tableEvent.resizeColumnToContents(column)
       
        self.ui.tableEvent.resizeColumnsToContents()
        self.ui.tableEvent.hideColumn(3)
        self.ui.tableEvent.horizontalHeader().setResizeMode(5,QHeaderView.Stretch)
        self.tableEventModel.setHeaderData(0, Qt.Horizontal, "Дата/Время");
        self.tableEventModel.setHeaderData(1, Qt.Horizontal, "Расположение");
        self.tableEventModel.setHeaderData(2, Qt.Horizontal, "Датчик");
        self.tableEventModel.setHeaderData(3, Qt.Horizontal, "Статус.ID");
        self.tableEventModel.setHeaderData(4, Qt.Horizontal, "Статус");
        self.tableEventModel.setHeaderData(5, Qt.Horizontal, "Информация");
        self.tableEventModel.setHeaderData(6, Qt.Horizontal, "Пользователь");
        self.tm.select()
    def closeEvent(self, event):
        self.SaveEvent('ОТКЛЮЧЕНИЕ системы',-2,0,self.UserId)
        print("-CloseProgramm-")

    def SaveEvent(self,info,sensor_id,level_id,user_id):
        query = QtSql.QSqlQuery()
        sql='INSERT INTO  event(info,sensor_id, level_id, user_id)VALUES("{}",{},{},{});'.format(info,sensor_id,level_id,user_id)
        print(query.exec_(sql),'SQL=',sql)
        self.tableEventModel.setQuery( self.tableEventModel.query().lastQuery() )

#--------Event Page End-------------------------------------------------------------------------------------------------
#--------UserLogin------------------------------------------------------------------------------------------------------
    def enterUsernameLogin(self,index):
        rec=QtSql.QSqlRecord()
        rec=self.tmUser.record(index.row())
        self.ui.lineEditLogin.setText(rec.value("username"))
        self.ui.lineEditPassword.clear()
    def InitUserPage(self):
        self.tmUser = QtSql.QSqlQueryModel(self)
        self.tmUser.setQuery('SELECT username FROM user WHERE(ID>0)ORDER BY id DESC')
        self.ui.tableUser.setModel(self.tmUser)
        self.ui.tableUser.horizontalHeader().setResizeMode(0,QHeaderView.Stretch)
        self.ui.tableUser.verticalHeader().hide()
        self.ui.tableUser.setSelectionMode(QAbstractItemView.SingleSelection)
    def enterDigitButtonLogin(self):
        clickedButton = self.sender()
        txt=clickedButton.text()
        newtxt=self.ui.lineEditPassword.text()+txt
        self.ui.lineEditPassword.setText(newtxt)
    def enterBackSpaceLogin(self):
        txt=self.ui.lineEditPassword.text()
        newtxt=txt[0:-1]
        self.ui.lineEditPassword.setText(newtxt)
    def enterEnterLogin(self):
        query = QtSql.QSqlQuery()
        login=self.ui.lineEditLogin.text()
        password= self.ui.lineEditPassword.text()
        sql='SELECT * FROM user WHERE ((username="{}")and (password="{}"))'.format(login,password)
        query.exec_(sql)
        if(query.next()):
            self.dateLabel.setText('<b>[Пользователь: {} - авторизован]'.format(login))
            self.dateLabel.setStyleSheet("QLabel {  color : green; }")
            self.UserId=query.value(0)
            self.SaveEvent('Авторизация пользователя',-3,0,self.UserId)
        else:
            self.dateLabel.setText('[{}]'.format('Ошибка авторизации. Не верный пароль'))
            self.dateLabel.setStyleSheet("QLabel {  color : red; }")
            self.UserId=0
#--------UserLogin End--------------------------------------------------------------------------------------------------

    def __del__(self):
        self.ui = None

# -----------------------------------------------------#
if __name__ == '__main__':
    # create application
    app = QApplication(sys.argv)
    app.setApplicationName('PCN')

    sshFile="./darkorange.stylesheet"
    sshFile="styles/qmc2-black-0.10/qmc2-black-0.10.qss"
    #sshFile="styles/qmc2-fire-0.8/qmc2-fire-0.8.qss "
    with open(sshFile,"r") as fh:
        app.setStyleSheet(fh.read())
    app.setStyle('plastique')
    #originalPalette = QApplication.palette()
    #app.setPalette(QApplication.style().standardPalette())
    #app.setPalette(originalPalette)
    #app.setStyle(QStyleFactory.create('plastique'))
    # create widget
    w = MainWindow()
    w.setWindowTitle('PCN')
    w.setGeometry(30,30,800,550)
    w.show()

    # connection
    QObject.connect(app, SIGNAL('lastWindowClosed()'), app, SLOT('quit()'))

    # execute application
    sys.exit(app.exec_())