from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.gui import QgsMessageBar
import logging
import os.path


#	
# Utility funcions	
# 
def setDialog(p_dialog):
    
    global _dialog
    _dialog = p_dialog
 
         
def setInterface(p_iface):
    
    global _iface, MSG_DURATION
    _iface = p_iface
    MSG_DURATION = 5        
 
    
def isFirstTime():
    
    global first
    if not 'first' in globals():
        first = True
    else:    
        first = False
    return first


def setCursor(p_cursor):
    
    global cursor
    cursor = p_cursor


def fillComboBox(widget, sql):
    
    elem = _dialog.findChild(QComboBox, widget)
    elem.clear()	
    elem.addItem("")	
    if not 'cursor' in globals():
        print "cursor error"
        return
    else:
        print "defined"
    return

    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        elem.addItem(row[0])	
        
        
def setComboModel(widget, vector):
    
    completer = QCompleter()
    completer.setCompletionColumn(0)
    completer.setMaxVisibleItems(10)
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    model = QStringListModel()
    model.setStringList(vector)         
    completer.setModel(model)
    widget.setModel(model)   
    widget.setCompleter(completer)        


def sqlToList(sql):
    
    vector = []
    vector.append('')
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        vector.append(unicode(row[0]))   
    return vector 
        

def setSelectedItem(widget, sql):
    
    cursor.execute(sql)
    row = cursor.fetchone()
    if not row:
        return				
    elem = _dialog.findChild(QComboBox, widget)
    if elem:
        index = elem.findText(row[0])
        elem.setCurrentIndex(index);		


def getSelectedItem(widget):
    
    elem = _dialog.findChild(QComboBox, widget)
    if not elem.currentText():
        elem_text = "null"
    else:
        elem_text = "'"+elem.currentText()+"'"	
    elem_text = widget+"="+elem_text
    return elem_text	


def getSelectedItem2(widget):
    
    elem = _dialog.findChild(QComboBox, widget)
    if not elem.currentText():
        elem_text = "null"
    else:
        elem_text = "'"+elem.currentText().replace("'", "''")+"'"	
    return elem_text	


def getValue(widget):
    
    elem = _dialog.findChild(QLineEdit, widget)
    if elem:	
        if elem.text():
            elem_text = widget + " = "+elem.text().replace(",", ".")		      
        else:
            elem_text = widget + " = null"
    else:
        elem_text = widget + " = null"
    return elem_text


def getFloat(widgetName):
    
    widget = _dialog.findChild(QLineEdit, widgetName)
    value = 0.0
    if widget:	
        if widget.text():
            value = float(widget.text().replace(",", "."))	      
    return value


def getStringValue(widget):
    
    elem = _dialog.findChild(QLineEdit, widget)
    if elem:	
        if (not elem.text() or elem.text().lower() == "null"):
            elem_text = widget + " = null"    
        else:
            elem_text = widget + " = '"+elem.text().replace("'", "''")+"'"
    else:
        elem = _dialog.findChild(QTextEdit, widget)	
        if elem:	
            if (not elem.toPlainText() or elem.toPlainText().lower() == "null"):  
                elem_text = widget + " = null"    
            else:
                elem_text = widget + " = '"+elem.toPlainText().replace("'", "''")+"'"
        else:				
            elem_text = widget + " = null"
    return elem_text


def getStringValue2(widget):
    
    elem = _dialog.findChild(QLineEdit, widget)
    if elem:	
        if (not elem.text() or elem.text().lower() == "null"):
            elem_text = "null"
        else:
            elem_text = "'"+elem.text().replace("'", "''")+"'"
    else:
        elem = _dialog.findChild(QTextEdit, widget)	
        if elem:	
            if (not elem.toPlainText() or elem.toPlainText().lower() == "null"):                
                elem_text = "null"    
            else:
                elem_text = "'"+elem.toPlainText().replace("'", "''")+"'"
        else:				
            elem_text = "null"
    return elem_text	


def getDate(widget, fieldName):

    try:    
        date_widget = _dialog.findChild(QDateEdit, widget)
        if not date_widget:
            print "not found"
            return
        
        dateAux = date_widget.date()
        aux = dateAux.toString("yyyy-MM-dd") 
        if aux:   
            value = aux
            text = fieldName+"='"+value+"'"  
        else:
            value = "null"
            text = fieldName+"=null"              
    except ValueError:
        value = "null"
        text = "" 
        
    return dict(value = value, text = text)


def isNull(widget):
    
    elem = _dialog.findChild(QLineEdit, widget)
    empty = True	
    if elem:	
        if elem.text():
            empty = False
    return empty	


def isNumber(elem):
    
    try:
        float(elem)
        return True
    except ValueError:
        return False


def isChecked(widgetName):
    
    widget = _dialog.findChild(QCheckBox, widgetName)
    value = False    
    if widget:    
        value = widget.isChecked()
    return str(value)   


def setText(widget, text):
    
    elem = _dialog.findChild(QLineEdit, widget)
    if elem:    
        elem.setText(str(text))
    else:
        print "setText"
        
def showInfo(text, duration = None):
    
    if duration is None:
        _iface.messageBar().pushMessage("", text, QgsMessageBar.INFO, MSG_DURATION)  
    else:
        _iface.messageBar().pushMessage("", text, QgsMessageBar.INFO, duration)              
    
def showWarning(text, duration = None):
    
    if duration is None:
        _iface.messageBar().pushMessage("", text, QgsMessageBar.WARNING, MSG_DURATION)  
    else:
        _iface.messageBar().pushMessage("", text, QgsMessageBar.WARNING, duration)          
        

def setLogger(name, folder, filename):
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # create file handler
    if not os.path.exists(folder):
        os.makedirs(folder)
    filepath = folder + "/" + filename 
    fh = logging.FileHandler(filepath)
    fh.setLevel(logging.INFO)
    
    # create console handler
    #ch = logging.StreamHandler()
    #ch.setLevel(logging.INFO)
    
    # create formatter and add it to the handlers
    formatter_fh = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #formatter_ch = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter_fh)
    #ch.setFormatter(formatter_ch)
    
    # add the handlers to logger
    if (len(logger.handlers) > 0):  
        removeHandlers(logger) 
    logger.addHandler(fh)
    #logger.addHandler(ch)   
    
    return logger

    
def removeHandlers(logger):    
    
    #logger.info('Total: %d'%len(logger.handlers))    
    for h in logger.handlers:
        #logger.info('removing handler %s'%str(h))
        logger.removeHandler(h)     
        
        
