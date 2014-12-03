import sys
from PyQt4 import QtCore, QtGui, QtSql
from PyQt4.QtGui import QColor
class QSqlQueryColorModel(QtSql.QSqlQueryModel):
    def __init__(self,mode, parent = None):
        super(QSqlQueryColorModel, self).__init__(parent)
        self.mode = mode
    def data(self, index, role):
        value = QtSql.QSqlQueryModel.data(self, index, role)
        if(self.mode==0):
            if role == QtCore.Qt.TextColorRole and index.column() == 4:
                level =    index.sibling(index.row(),3).data()
                if level==1:
                    return QtGui.QColor(QColor(0xff,0xa0,0x00))
                if level==2:
                    return QtGui.QColor(QtCore.Qt.red)
                if level==3:
                    return QtGui.QColor(QtCore.Qt.blue)
                if level==4:
                    return QtGui.QColor(QtCore.Qt.green)
            
            if role == QtCore.Qt.TextColorRole and index.column() != 4:
                level =    index.sibling(index.row(),3).data()
                if level==0:
                    return QtGui.QColor(QtCore.Qt.darkMagenta)
        if(self.mode==1):
            if role == QtCore.Qt.BackgroundColorRole and index.column() == 4:
                level =    index.sibling(index.row(),3).data()
                if level==1:
                    return QtGui.QColor(QColor(0xff,0xa0,0x00))
                elif level==2:
                    return QtGui.QColor(QtCore.Qt.red).darker(70)
                elif level==3:
                    return QtGui.QColor(QtCore.Qt.blue).darker(70)
                elif level==4:
                    return QtGui.QColor(QtCore.Qt.green).darker(70)
                else:
                    return QtGui.QColor(QtCore.Qt.gray).darker(80)

            if role == QtCore.Qt.BackgroundColorRole and index.column() != 4:
                level =    index.sibling(index.row(),3).data()
                if level==0:
                    return QtGui.QColor(QtCore.Qt.gray).darker(80)
               
        return value  
