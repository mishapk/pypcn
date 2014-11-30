import sys
from PyQt4 import QtCore, QtGui, QtSql
from PyQt4.QtGui import QColor
class QSqlQueryColorModel(QtSql.QSqlQueryModel):
    def __init__(self, column):
        super(QSqlQueryColorModel, self).__init__()
        self.column = column
    def data(self, index, role):
        value = QtSql.QSqlQueryModel.data(self, index, role)
        if role == QtCore.Qt.TextColorRole and index.column() == 4:
            level =    index.sibling(index.row(),3).data()
            if level==1:
                return QtGui.QColor(QColor(0xff,0xa0,0x00))
            if level==2:
                return QtGui.QColor(QtCore.Qt.red)
            if level==3:
                return QtGui.QColor(QtCore.Qt.darkBlue)
            if level==4:
                return QtGui.QColor(QtCore.Qt.green)
            
        if role == QtCore.Qt.TextColorRole and index.column() != 4:
            level =    index.sibling(index.row(),3).data()
            if level==0:
                return QtGui.QColor(QtCore.Qt.darkMagenta)
               
        return value  
