from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import QgsMessageBar
from qgis.utils import iface
from utils import *
from datetime import datetime
import time
import os.path
import psycopg2
import psycopg2.extras
import sys
import webbrowser
import getpass


def formOpen(dialog,layerid,featureid):

    global _dialog, _parent, _iface, current_path, current_date
    global MSG_DURATION, MAX_CLAUS
    
    # Set global variables    
    _dialog = dialog
    _parent = _dialog.parentWidget()
    MSG_DURATION = 5
    MAX_CLAUS = 4	
    widgetsToGlobal()
    #print getpass.getuser()
    
    # Check if it is the first time we execute this module
    if isFirstTime():
          
        # Get current path and save reference to the QGIS interface
        current_path = os.path.dirname(os.path.abspath(__file__))
        date_aux = time.strftime("%d/%m/%Y")
        current_date = datetime.strptime(date_aux, "%d/%m/%Y")
        _iface = iface

        # Connect to Database (only once, when loading map)
        showInfo("Attempting to connect to DB")
        connectDb()
        
    # Initial configuration
    initConfig()
    
    
def init():
    connectDb()
    fillReport()

def initAction(ninterno):
    global param
    param = ninterno
#    print "ninterno seleccionat: "+str(param)
    connectDb()
    fillReport()

def connectDb():

    global conn, cursor
    try:
        conn = psycopg2.connect("host=gisserver port=5432 dbname=gis_sjv user=gisadmin password=8u9ijn")
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e    
        sys.exit(1)

def widgetsToGlobal():

    global ninterno, refcat, area, txtSector, lblCondGenerals

    ninterno = _dialog.findChild(QLineEdit, "ninterno") 	
    refcat = _dialog.findChild(QLineEdit, "refcat")            
    area = _dialog.findChild(QLineEdit, "area")        
    txtSector = _dialog.findChild(QLabel, "txtSector")   
    lblCondGenerals = _dialog.findChild(QLabel, "lblCondGenerals")   	
    ninterno.setVisible(False)
	
	
def initConfig():    
    
    # Wire up our own signals
    setSignals()    
    
    # Other default configuration
    boldGroupBoxes()
	
	# Fill report tables
    fillReport()
	
	# Load data 
    loadData()	

	
def loadData():

	# Dades parcela
    sql = "SELECT sec_codi, sec_descripcio FROM data.rpt_parcela"
    cursor.execute(sql)
    row = cursor.fetchone()
    _dialog.findChild(QLineEdit, "txtSector").setText(row[1])
    if row[0]:
        url = "sectors\\"+row[0]+".htm"
        text = "<a href="+url+">Veure Normativa sector</a>"
        _dialog.findChild(QLabel, "lblSector").setText(text)
        _dialog.findChild(QLabel, "lblSector").setToolTip(row[0])
    else:
        _dialog.findChild(QLabel, "lblSector").setVisible(False)
	
    # Dades claus
    i = 0
    sql = "SELECT qua_codi, qua_descripcio, per_int, tord_codi, tord_descripcio FROM data.rpt_planejament ORDER BY area_int DESC LIMIT "+str(MAX_CLAUS)
    cursor.execute(sql)
    rows = cursor.fetchall()	
    for row in rows:	
        i = i+1
        #_dialog.findChild(QPushButton, "btnClauPdf_"+str(i)).clicked.connect(openClauPdf)  		
        #_dialog.findChild(QLineEdit, "txtClau_"+i).setText(row[0]+" - "+row[1])
        _dialog.findChild(QLineEdit, "txtClau_"+str(i)).setText(row[0])	
        _dialog.findChild(QLineEdit, "txtPer_"+str(i)).setText(str(row[2]))	
        if row[3]:	
            url = "ordenacions\\"+row[3]+".htm"
            text = "<a href="+url+">"+row[4]+"</a>"	
            _dialog.findChild(QLabel, "lblOrd_"+str(i)).setText(text)
            _dialog.findChild(QLabel, "lblOrd_"+str(i)).setToolTip(u"Veure sistema d'ordenacio '"+row[4]+"'")	
        else:
            _dialog.findChild(QLabel, "lblOrd_"+str(i)).setVisible(False) 	

    # Ocultar controls	
    offset = 0		
    while i<MAX_CLAUS:
        i = i+1
        offset = offset+30	
        _dialog.findChild(QLineEdit, "txtClau_"+str(i)).setVisible(False)	
        _dialog.findChild(QLineEdit, "txtPer_"+str(i)).setVisible(False)
        _dialog.findChild(QLabel, "lblOrd_"+str(i)).setVisible(False) 			
		
    # Redibuix components	
    _dialog.hideButtonBox()
    #print _parent.width()	
    #print _dialog.height()		
    gb2Zones = _dialog.findChild(QGroupBox, "gb2Zones")
    gb2Zones.setFixedHeight(gb2Zones.height() - offset)		
    gb3Annex = _dialog.findChild(QGroupBox, "gb3Annex")
    gb3Annex.move(gb3Annex.x(), gb3Annex.y() - offset)	
    #_dialog.resize(200, 100)
    #_dialog.setFixedSize(500, 300)	
    _dialog.adjustSize();
	
   
def boldGroupBoxes():   
    
    _dialog.findChild(QGroupBox, "gb1Ubicacio").setStyleSheet("QGroupBox { font-weight: bold; } ")
    _dialog.findChild(QGroupBox, "gbSector").setStyleSheet("QGroupBox { font-weight: bold; } ")	
    _dialog.findChild(QGroupBox, "gb2Zones").setStyleSheet("QGroupBox { font-weight: bold; } ")
    _dialog.findChild(QGroupBox, "gb3Annex").setStyleSheet("QGroupBox { font-weight: bold; } ")	
    _dialog.findChild(QLabel, "lblTitle").setStyleSheet("QLabel { background-color: rgb(220, 220, 220); }");	
            	
def fillReport():

    param = ninterno.text()
    sql = "SELECT data.fill_report("+str(param)+")"
    #print "executeSql: "+str(sql)
    executeSql(sql)
    
def getResult(sql):
    cursor.execute(sql)
    row = cursor.fetchone()
    if not row:
        print "getResult: Error"
    conn.commit()
    return row[0]
    
def executeSql(sql):
    cursor.execute(sql)
    conn.commit()
	
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

		
# Wire up our own signals    
def setSignals():
  
    # Parcela
    _dialog.findChild(QPushButton, "btnParcelaPdf").clicked.connect(openPdfUbicacio)  
    _dialog.findChild(QLabel, "lblSector").linkActivated.connect(openURL)		
	
    # Claus	
    _dialog.findChild(QPushButton, "btnClauPdf_1").clicked.connect(openPdfZones)  
    _dialog.findChild(QLabel, "lblOrd_1").linkActivated.connect(openURL)	
	
	# Annex
    _dialog.findChild(QLabel, "lblCondGenerals").linkActivated.connect(openURL)	
    _dialog.findChild(QLabel, "lblParamFinca").linkActivated.connect(openURL)
    _dialog.findChild(QLabel, "lblParamEdificacio").linkActivated.connect(openURL)	
    _dialog.findChild(QLabel, "lblDotacioAparc").linkActivated.connect(openURL)
    _dialog.findChild(QLabel, "lblRegulacioAparc").linkActivated.connect(openURL)
	
	
# Slots
def openPdfUbicacio():

    composerView = _iface.activeComposers()[1].composition()
    composerView.setAtlasMode(QgsComposition.PreviewAtlas) 	
    filePath = current_path+"\\reports\\"+refcat.text()+"_ubicacio.pdf"
    result = composerView.exportAsPDF(filePath)
    if result:
        showInfo("PDF generated in: "+filePath)
        os.startfile(filePath)
    else:
        showWarning("PDF could not be generated in: "+filePath)

	
def openPdfZones():

    composerView = _iface.activeComposers()[0].composition()
    composerView.setAtlasMode(QgsComposition.PreviewAtlas) 	
    filePath = current_path+"\\reports\\"+refcat.text()+"_zones.pdf"
    result = composerView.exportAsPDF(filePath)
    if result:
        showInfo("PDF generated in: "+filePath)
        os.startfile(filePath)		
    else:
        showWarning("PDF could not be generated in: "+filePath)

	
def openURL(url):

    urlPath = "file://"+current_path+"\\html\\"+url
    print "openURL: "+urlPath		
    webbrowser.open(urlPath, 2)	

	
	
if __name__ == '__main__':
    init()