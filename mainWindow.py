#!-*-coding:utf-8-*-
import sys
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic, QtCore, QtSql
import pyaudio
import connection
import Player


from sensor import SensorAlarm
from target import TargetAlarm
from x305 import x305Thread
from eventmodel import QSqlQueryColorModel

( Ui_MainWindow, QMainWindow ) = uic.loadUiType('MainWindow.ui')

Mode = 0
#0- Normal, 1 - Admin


class MainWindow(QMainWindow):
    """MainWindow inherits QMainWindow"""
    #Режим работы таймера(0- системное время; 1- обратный очте;)
    timerMode=0
    user_login=''
    timerInterval1 = QTime(0,0,10)
    timerInterval2 = QTime(0,0,10)
    ti_1=QTime
    ti_2=QTime
    s_leve=-1 # Сотояние датчика (уровень)
    s_id=-1   # ID датчика
    br_id=-1  # ID конопки резульат


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
         #----AudioPlayer-
        self.player=Player.MPlayer()

        self.ui.VAO.addWidget(self.player)
#        self.output = Phonon.AudioOutput(Phonon.MusicCategory,self)
#        self.m_media = Phonon.MediaObject(self)
#        self.ui.volumeSlider.setAudioOutput(self.output)
#        self.ui.seekSlider.setMediaObject(self.m_media)
#        Phonon.createPath(self.m_media,self.output)
        #---------------

        if not connection.createConnection():
            sys.exit(1)

        self.ui.frame_cs.hide()

        self.ui.graphicsView.horizontalScrollBar().setValue(900)


        self.initGraphics()
        self.CreateTableEvent()
        self.InitUserPage()
        self.ui.splitter.setStretchFactor(0,1)
        self.ui.splitter.setSizes([0])
        #self.ui.groupBox.hide()
        self.SaveEvent('СТАРТ системы',-1,0,self.UserId,-1,-1)



        self.x305Read=x305Thread("COM7",1900,0.1)
        self.x305Read.notifyProgress.connect(self.setAlarm)
        self.x305Read.start()



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
        if(self.timerMode==0):

            time=QTime.currentTime()
            text=QTime.toString(time)
            self.lcd.display(text)

        if(self.timerMode==1):
            self.ti_1=self.ti_1.addSecs(-1)
            time=self.ti_1
            text=QTime.toString(time)
            self.lcd.display(text)
            if(self.ti_1<=QTime(0,0,0)):
                self.aPrinaty(1)

        if(self.timerMode==2):
            self.ti_2=self.ti_2.addSecs(-1)
            time=self.ti_2
            text=QTime.toString(time)
            self.lcd.display(text)
            if(self.ti_2<=QTime(0,0,0)):
                self.aUCS(1)

        #date = QtCore.QDate.currentDate()
        #text = date.toString('[dd-MM-yyyy]')
        #self.dateLabel.setText(text)
#Обработка клавиш принятия решения--------------------------------------------------------------------------------------
    def setTimerMode(self,mode):

        self.timerMode=mode
        if(mode==0):
            self.ui.frame_cs.hide()
            self.targetAlarm.GroupAnimation.stop()
            self.targetAlarm.hide()
            self.getMessageDB()
        if(mode==1):
            self.ti_1 = self.timerInterval1
            self.ui.frame_cs.show()
            self.ui.pushB_p.show()
            self.ui.pushB_cs.hide()
            self.ui.pushB_ucs.hide()
            self.ui.pushB_ncs.hide()
        if(mode==2):
            self.ti_2 = self.timerInterval2
            self.ui.frame_cs.show()
            self.ui.pushB_p.hide()
            self.ui.pushB_cs.show()
            self.ui.pushB_ucs.show()
            self.ui.pushB_ncs.show()

    def aPrinaty(self,m):
        if(self.s_leve in[1,2]):
            self.setTimerMode(2)
        if(self.s_leve in[3,4]):
            self.saveStatusP(self.s_id,m,0)
            self.setTimerMode(0)
    def aCS(self,m):
        self.saveStatusP(self.s_id,m,1)
        self.setTimerMode(0)
    def aUCS(self,m):
        self.saveStatusP(self.s_id,m,2)
        self.setTimerMode(0)
        self.pBSZUOff()
    def aNCS(self,m):
        self.saveStatusP(self.s_id,m,3)
        self.setTimerMode(0)


    def bPrinaty(self):
        print('Нажата кнопка [Принять]')
        self.aPrinaty(2)

    def bCS(self):
        print('Нажата кнопка [Наличие ЧС]')
        self.aCS(2)

    def bUCS(self):
        print('Нажата кнопка [Угроза ЧС]')
        self.aUCS(2)

    def bNCS(self):
        print('Нажата кнопка [Отмена]')
        self.aNCS(2)
        self.pBSZUOff()
        self.m_media.stop()
#Обработка клавиш принятия решения [Конец]------------------------------------------------------------------------------
#----------NotifyPage---------------------------------------------------------------------------------------------------


    def pBSirenaOn(self):
        self.x305Read.setSZU(1)
        text='Сирена'
        self.ui.lineEditAOs.setText(text)
        file='tv_ns.wav'
        fn="sounds/{}".format(file)
        if(os.path.exists(fn)==False):
            print('Error: Файл"',fn,'" не найден!')
        self.m_media.setCurrentSource(Phonon.MediaSource(fn))
        self.ui.lineEditAOm.setText(file)
        self.m_media.play()
        self.ui.lineEditSZU.setText('СЗУ включено')

    def pBSirenaOff(self):
        self.m_media.stop()
        self.x305Read.setSZU(0)
        self.ui.lineEditSZU.setText('')
    def pBSZUOn(self):
        self.x305Read.setSZU(1)
        self.ui.lineEditSZU.setText('СЗУ включено')

    def pBSZUOff(self):
        self.x305Read.setSZU(0)
        self.ui.lineEditSZU.setText('')
#----------HomePage-----------------------------------------------------------------------------------------------------
    def sensorSymbol(self,ids,adr,x,y,size,level,types,sounds,commands):
        item=SensorAlarm(0,0,size,level,types,sounds,commands)
        item.setPos(x,y)
        item.id= ids
        item.address=adr
        item.sounds=sounds
        item.commands=commands

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
            sounds= query.value(7)
            commands=query.value(8)
            #print('x=',x,'y=',y)
            ids=query.value(0)
            adr =query.value(1)

            self.sensorSymbol(ids,adr,x,y,size,33,tp,sounds,commands)
            #


        #sna = SensorAlarm(0,0,20,2,6)
        #self.scene.addItem(sna)
        print('LoadEnd')

        self.targetAlarm = TargetAlarm(0,0,size)
        self.targetAlarm.setPos(x-size*3/2+size/2,y-size*3/2+size/2)
        self.targetAlarm.hide()
        self.scene.addItem(self.targetAlarm )
        self.ui.graphicsView.setScene(self.scene)
        self.CreateTableSensor()

    def saveSansors(self):
        query = QtSql.QSqlQuery()
        for p in self.GI:
            x = p.pos().x()
            y = p.pos().y()
            #print('x=',x,'y=',y)
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
        output.setVolume(100/100)
        m_media = Phonon.MediaObject(self)
        Phonon.createPath(m_media, output)
        m_media.setCurrentSource(Phonon.MediaSource("sounds/1.wav"))
        m_media.play()


        #self.player = Phonon.createPlayer(Phonon.MusicCategory)
        #self.player.setCurrentSource(Phonon.MediaSource("sounds/1.wav"))
        #self.player.play()
#Слот сигнала новых сработок
    def setAlarm(self,sensor_address, sensor_level):
        for p in self.GI:
            if(p.address==sensor_address):
                old_level=p.level
                p.setLevel(sensor_level)
                x=p.pos().x()
                y=p.pos().y()
                id_s=p.id
                sounds=p.sounds.split('|')
        if(sensor_level in [1,2]):


            self.pBSZUOn()
            self.m_media.stop()
            fn="sounds/{}".format(sounds[sensor_level-1])
            if(os.path.exists(fn)==False):
                print('Error: Файл"',fn,'" не найден!')
            self.m_media.setCurrentSource(Phonon.MediaSource(fn))
            self.m_media.play()

        #---33 Уровень равный при первом запуске системы
        if(old_level==33 and not sensor_level in [1,2]):
            st=1
            sb=0
        else:
            st=0
            sb=-1
        self.SaveEvent('Датчик',id_s,sensor_level,self.UserId,st,sb)
        #Информаци для плеера
        if(sensor_level in [1,2]):
            self.ui.lineEditAOm.setText(sounds[sensor_level-1])
            #---------------------------------------------------------------------------------------------------
            fields='sensor.info, stype.info, level.title, event.created, event.id,level.id'
            where='WHERE((event.status_id=0)and(level.id in(1,2,3,4)))'
            sql=self.formatSqlEvent(fields,where)
            query = QtSql.QSqlQuery(sql)
            if(query.next()):
                text = '{}, {}, {} '.format(query.value(0),query.value(1),query.value(2))
                self.ui.lineEditAOs.setText(text)
            #---------------------------------------------------------------------------------
        self.getMessageDB()
#----Функция обработки накомпленных сообщений  о сработке---------------------------------------------------------------
    def getMessageDB(self):

        fields='sensor.x, sensor.y, sensor.info, stype.info, level.title, event.created, event.id,level.id'
        where='WHERE((event.status_id=0)and(level.id in(1,2,3,4)))'
        sql=sql=self.formatSqlEvent(fields,where)
        query = QtSql.QSqlQuery(sql)
        if(query.next()):
            x = query.value(0)
            y = query.value(1)
            place=query.value(2)
            sensor=query.value(3)
            level= query.value(4)
            created= query.value(5)
            self.s_id=query.value(6)
            self.s_leve=query.value(7)
            info='<br>{}, {} : {} <br>[{}]'.format(place,sensor,level,created)
            self.targetAlarm.setPosTarget(x,y)
            self.targetAlarm.animateRotation()
            self.targetAlarm.show()
            self.ui.graphicsView.centerOn(x,y)
            self.ui.label_info_cs.setText('<b><font color="red">{}</font></b><font color="blue"> {}</font>'.format('Внимание!',info))
            self.setTimerMode(1)
        #if query.next():



#---------HomePage End--------------------------------------------------------------------------------------------------
    def saveStatusP(self,id,status,button):
        sql='UPDATE event SET status_id={},button_result_id={}, user_id={} WHERE(id={} )'.format(status,button,self.UserId,id,)
        query = QtSql.QSqlQuery(sql)
        self.tableEventModel.setQuery( self.tableEventModel.query().lastQuery() )
        self.br_id=button
        #print(sql)
#--------Event_page-----------------------------------------------------------------------------------------------------

    def formatSqlEvent(self,fields,where):
        sql='SELECT {} ' \
            'FROM  (event INNER JOIN sensor ON event.sensor_id=sensor.id) ' \
            'INNER JOIN stype ON sensor.type_id=stype.id ' \
            'INNER JOIN level ON event.level_id=level.id   ' \
            'INNER JOIN user ON event.user_id=user.id   ' \
            'INNER JOIN status ON event.status_id=status.id ' \
            'INNER JOIN button ON event.button_result_id=button.id ' \
            ' {} ' \
            'ORDER BY event.id DESC LIMIT 1000'
        result=sql.format(fields,where)
        return result

    def CreateTableEvent(self):
        self.tableEventModel = QSqlQueryColorModel(1,self)
        fields='event.created,sensor.info,stype.title,level.id,level.title,event.info,user.username,' \
               'status.title as "Принято",' \
               'button.title as "Ситуация"'
        sql=self.formatSqlEvent(fields,'')
        #print('Ev=',sql)

        self.tableEventModel.setQuery(sql)
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
        self.SaveEvent('ОТКЛЮЧЕНИЕ системы',-2,0,self.UserId,-1,-1)
        print("-CloseProgramm-")

    def SaveEvent(self,info,sensor_id,level_id,user_id,status_id,button_result_id):
        query = QtSql.QSqlQuery()
        sql='INSERT INTO  event(info,sensor_id, level_id, user_id, status_id, button_result_id)' \
            'VALUES("{}",{},{},{},{},{});'.format(info,sensor_id,level_id,user_id,status_id,button_result_id)
        query.exec_(sql)
        self.tableEventModel.setQuery( self.tableEventModel.query().lastQuery() )

#--------Event Page End-------------------------------------------------------------------------------------------------
#--------UserLogin------------------------------------------------------------------------------------------------------
    def enterUsernameLogin(self,index):
        rec=QtSql.QSqlRecord()
        rec=self.tmUser.record(index.row())
        self.user_login=rec.value("username")
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

        login=self.user_login
        password= self.ui.lineEditPassword.text()
        sql='SELECT * FROM user WHERE ((username="{}")and (password="{}"))'.format(login,password)
        query.exec_(sql)
        if(query.next()):
            self.dateLabel.setText('<b>[Пользователь: {} - авторизован]'.format(login))
            self.dateLabel.setStyleSheet("QLabel {  color : green; }")
            self.UserId=query.value(0)
            self.SaveEvent('Авторизация пользователя',-3,0,self.UserId,-1,-1)
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
    #sshFile="styles/qmc2-xmas-0.5/qmc2-xmas-0.5.qss"
    #sshFile="styles/qmc2-machinery-0.3/qmc2-machinery-0.3.qss"
    #sshFile="styles/qmc2-fire-0.8/qmc2-fire-0.8.qss "
    sshFile="styles/qmc2-metal-0.9/qmc2-metal-0.9.qss"
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