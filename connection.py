from PyQt4 import QtSql, QtGui
import os
def createConnection():
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    ft=os.path.exists('data.db')
    db.setDatabaseName('data.db')
    if not db.open():
        QtGui.QMessageBox.critical(None, QtGui.qApp.tr("Cannot open database"),
                QtGui.qApp.tr("Unable to establish a database connection.\n"
                              "This example needs SQLite support. Please read "
                              "the Qt SQL driver documentation for information "
                              "how to build it.\n\n"
                              "Click Cancel to exit."),
                QtGui.QMessageBox.Cancel)
        return False
    if(ft==False):
        createDB()
        insertDB()
    return True

def createDB():
    query = QtSql.QSqlQuery()
    sql=[]
    sql.append('create table sensor(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
                        'address INTEGER,'
                        ' title text,'
                        ' info text,'
                        'x float ,'
                        'y float ,'
                        'type_id INTEGER,'
                        'sounds TEXT,'
                        'commands TEXT'
                        ');')
    sql.append('create table level(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
                        ' title text,'
                        ' info text);')
    sql.append('create table stype(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
                        ' title text,'
                        ' info text);')
    #Таблица журнала событи
    sql.append('create table event(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
                       'created datetime default (datetime(\'now\',\'localtime\')),'
                        ' sensor_id INTEGER,'
                        ' level_id INTEGER,'
                        ' user_id INTEGER,'
                        ' info text,'
                        ' status_id INTEGER,'
                        ' button_result_id INTEGER,'
                        ' monitoring_result'
                        ');')
    #Status_id. Статус сообщения. 0- не принят, 1-принят автоматически, 2- принят в ручную
    #Status_Result_id. Статус подтверждения. 0- Отмена, 1-Угроза ЧС, 2- ЧС
    #Monitoring_result -Результат доставки сообщения на сервер мониторинга
    sql.append('CREATE TABLE status(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
               'title TEXT,'
               'info TEXT);')
    sql.append('CREATE TABLE button(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
               'title TEXT,'
               'info TEXT);')

    sql.append('CREATE TABLE user(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
               'username TEXT,'
               'password TEXT);')

    for s in sql:
        if(query.exec_(s)==False):
            print('SQL:Create Table ERROR:',query.lastError().text(),' sql= ',s)

#-----------------------------------------------------------------------------------------------------------------------

def insertDB():
    query = QtSql.QSqlQuery()
    sql=[]
    sql.append
    #Системная информация
    sql.append('INSERT INTO sensor(id,address,x,y,title,info,type_id)VALUES(0,-1,0,0," ","Система",0);')
    sql.append('INSERT INTO sensor(id,address,x,y,title,info,type_id)VALUES(-1,-1,0,0," ","Вход в систеу",0);')
    sql.append('INSERT INTO sensor(id,address,x,y,title,info,type_id)VALUES(-2,-1,0,0," ","Выход из системы",0);')
    sql.append('INSERT INTO sensor(id,address,x,y,title,info,type_id)VALUES(-3,-1,0,0," ","Авторизация",0);')
    #Датчики
    sql.append('INSERT INTO sensor(address,x,y,info,title,type_id,sounds,commands)VALUES(161,717,343,"Место хранеия кислоты","U2.1",2,"|tv_vitikkislotyVK.wav|error.wav|chimes.wav","");')
    sql.append('INSERT INTO sensor(address,x,y,info,title,type_id,sounds,commands)VALUES(161,717,259,"Место хранеия кислоты","U2.2",2,"|tv_vitikkislotyVK.wav|error.wav|chimes.wav","");')
    sql.append('INSERT INTO sensor(address,x,y,info,title,type_id,sounds,commands)VALUES(162,273,247,"Травильные ванны","U2.3",2,"|tv_vitikkislotyTV.wav|error.wav|chimes.wav","");')
    sql.append('INSERT INTO sensor(address,x,y,info,title,type_id,sounds,commands)VALUES(162,120,222,"Травильные ванны","U2.4",2,"|tv_vitikkislotyTV.wav|error.wav|chimes.wav","");')
    sql.append('INSERT INTO sensor(address,x,y,info,title,type_id,sounds,commands)VALUES(163,585,327,"Место хранеия кислоты","VTM1",6,"|tv_ns.wav|error.wav|chimes.wav","");')
    sql.append('INSERT INTO sensor(address,x,y,info,title,type_id,sounds,commands)VALUES(164,30,217,"Травильные ванны","VTM2",6,"|tv_ns.wav|error.wav|chimes.wav","");')
    sql.append('INSERT INTO sensor(address,x,y,info,title,type_id,sounds,commands)VALUES(165,30,264,"Травильные ванны","VTM3",6,"|tv_ns.wav|error.wav|chimes.wav","");')
    sql.append('INSERT INTO sensor(address,x,y,info,title,type_id,sounds,commands)VALUES(166,690,350,"Место хранеия кислоты","U3.1",5,"kpk1.wav|kpk2.wav|error.wav|chimes.wav","");')
    sql.append('INSERT INTO sensor(address,x,y,info,title,type_id,sounds,commands)VALUES(166,640,350,"Место хранеия кислоты","U3.2",5,"kpk1.wav|kpk2.wav|error.wav|chimes.wav","");')

    sql.append('INSERT INTO level(id,title,info)VALUES(0,"","системная");')
    sql.append('INSERT INTO level(id,title,info)VALUES(1,"Порог I","докритичесикй");')
    sql.append('INSERT INTO level(id,title,info)VALUES(2,"Порог II","критичесикй");')
    sql.append('INSERT INTO level(id,title,info)VALUES(3,"Отказ","неисправность");')
    sql.append('INSERT INTO level(id,title,info)VALUES(4,"Норма","нормальное сотояние");')
    
    sql.append('INSERT INTO stype(id,title,info)VALUES(0,"Ситемная информация","ситемная информация");')
    sql.append('INSERT INTO stype(id,title,info)VALUES(1,"Уровень","датчик уровня");')
    sql.append('INSERT INTO stype(id,title,info)VALUES(2,"Пролив","датчик пролива");')
    sql.append('INSERT INTO stype(id,title,info)VALUES(3,"Давление","датчик давления");')
    sql.append('INSERT INTO stype(id,title,info)VALUES(4,"Температура","датчик температуры");')
    sql.append('INSERT INTO stype(id,title,info)VALUES(5,"Концентрация","концентрация паров кислоты");')
    sql.append('INSERT INTO stype(id,title,info)VALUES(6,"Ручной извещатель","ручной извещатель");')

    sql.append('INSERT INTO user(id,username,password)VALUES(0,"нет","");')
    sql.append('INSERT INTO user(id,username,password)VALUES(1,"Admin","7777");')
    sql.append('INSERT INTO user(id,username,password)VALUES(2,"User","1111");')

    sql.append('INSERT INTO status(id,title,info)VALUES(-1,"","Система");')
    sql.append('INSERT INTO status(id,title,info)VALUES(0,"Не принято","");')
    sql.append('INSERT INTO status(id,title,info)VALUES(1,"Автоматически","");')
    sql.append('INSERT INTO status(id,title,info)VALUES(2,"Вручную","");')

    sql.append('INSERT INTO button(id,title,info)VALUES(-1,"","Система");')
    sql.append('INSERT INTO button(id,title,info)VALUES(0,"Принята","");')
    sql.append('INSERT INTO button(id,title,info)VALUES(1,"ЧС","");')
    sql.append('INSERT INTO button(id,title,info)VALUES(2,"Угроза ЧС","");')
    sql.append('INSERT INTO button(id,title,info)VALUES(3,"Отмена","");')

    print('Start Insert DB')
    for s in sql:
        if(query.exec_(s)==False):
            print('SQL:Insert data ERROR:',query.lastError().text(),' sql= ',s)
#-----------------------------------------------------------------------------------------------------------------------