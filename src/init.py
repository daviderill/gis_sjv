from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import *  #@UnusedWildImport
from qgis.core import *    #@UnusedWildImport
from qgis.utils import iface
from datetime import datetime
import time
import os.path             #@UnusedWildImport
import psycopg2
import psycopg2.extras
import sys
import webbrowser
from utils_fitxa import *  #@UnusedWildImport


def formOpen(dialog,layerid,featureid):

    global _dialog, _iface, current_path, current_date, report_folder
    global MSG_DURATION, MAX_CLAUS, PDF_UBICACIO, PDF_ZONES
    
    # Check if it is the first time we execute this module
    if isFirstTime():
          
        # Get current path and save reference to the QGIS interface
        current_path = os.path.dirname(os.path.abspath(__file__))
        date_aux = time.strftime("%d/%m/%Y")
        current_date = datetime.strptime(date_aux, "%d/%m/%Y")
        report_folder = current_path+"/reports/"
        _iface = iface        
        setInterface(iface)
        
        # Set constants
        MSG_DURATION = 5
        MAX_CLAUS = 4
        PDF_UBICACIO = 0
        PDF_ZONES = 1

        # Connect to Database (only once, when loading map)
        showInfo("Attempting to connect to DB")
        connectDb()

    # If not, close previous dialog	if already opened
    else:
        if _dialog.isVisible():
            _dialog.parent().setVisible(False)
       
    # Get dialog and his widgets
    _dialog = dialog
    setDialog(dialog)
    widgetsToGlobal()

    # Initial configuration
    initConfig()
    
    
def init():
    connectDb()
    fillReport()

def initAction(ninterno):
    global param  
    param = ninterno
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

    global ninterno, refcat, area, lblCondGenerals

    ninterno = _dialog.findChild(QLineEdit, "ninterno")
    refcat = _dialog.findChild(QLineEdit, "refcat")
    area = _dialog.findChild(QLineEdit, "area")
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

    # Refresh map
    _iface.mapCanvas().refresh()


def loadData():

    # Dades parcela: sector, classificacio i adreca
    sql = "SELECT sec_codi, sec_descripcio, cla_codi, cla_descripcio, (cat_tipo_via || ' ' || cat_nombre_via || ' ' || cat_primer_numero_policia) as adreca FROM data.rpt_parcela"
    cursor.execute(sql)
    row = cursor.fetchone()

    _dialog.findChild(QLineEdit, "txtSector").setText(row[1])
    lblSector = _dialog.findChild(QLabel, "lblSector")
    if row[0]:
        url = "sectors\\"+row[0]+".htm"
        text = "<a href="+url+">Veure Normativa sector</a>"
        lblSector.setText(text)
        lblSector.setToolTip(row[0])
    else:
        lblSector.setVisible(False)

    _dialog.findChild(QLineEdit, "txtClass").setText(row[3])
    lblClass = _dialog.findChild(QLabel, "lblClass")
    if row[2]:
        url = "classificacio\\"+row[2]+".htm"
        text = "<a href="+url+">Veure Normativa classificaci&oacute;</a>"
        lblClass.setText(text)
        lblClass.setToolTip(row[3])
    else:
        lblClass.setVisible(False)

    _dialog.findChild(QLineEdit, "txtAdreca").setText(row[4])

    # Dades claus
    i = 0
    sql = "SELECT qua_codi, SUM(per_int), tord_codi, tord_descripcio FROM data.rpt_planejament GROUP BY qua_codi, tord_codi, tord_descripcio ORDER BY SUM(per_int) DESC LIMIT "+str(MAX_CLAUS)
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        i = i+1
        _dialog.findChild(QLineEdit, "txtClau_"+str(i)).setText(row[0])
        _dialog.findChild(QLineEdit, "txtPer_"+str(i)).setText(str(row[1]))
        if row[2]:
            url = "ordenacions\\"+row[2]+".htm"
            text = "<a href="+url+">"+row[3]+"</a>"
            _dialog.findChild(QLabel, "lblOrd_"+str(i)).setText(text)
            _dialog.findChild(QLabel, "lblOrd_"+str(i)).setToolTip(u"Veure sistema d'ordenacio '"+row[3]+"'")
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
    gbZones = _dialog.findChild(QGroupBox, "gbZones")
    gbZones.setFixedHeight(gbZones.height() - offset)
    gbAnnex = _dialog.findChild(QGroupBox, "gbAnnex")
    gbAnnex.move(gbAnnex.x(), gbAnnex.y() - offset)	
    _dialog.adjustSize();

   
def boldGroupBoxes():   
    
    _dialog.findChild(QGroupBox, "gbUbicacio").setStyleSheet("QGroupBox { font-weight: bold; } ")
    _dialog.findChild(QGroupBox, "gbSector").setStyleSheet("QGroupBox { font-weight: bold; } ")
    _dialog.findChild(QGroupBox, "gbClass").setStyleSheet("QGroupBox { font-weight: bold; } ")
    _dialog.findChild(QGroupBox, "gbZones").setStyleSheet("QGroupBox { font-weight: bold; } ")
    _dialog.findChild(QGroupBox, "gbAnnex").setStyleSheet("QGroupBox { font-weight: bold; } ")
    _dialog.findChild(QLabel, "lblTitle").setStyleSheet("QLabel { background-color: rgb(220, 220, 220); }");
    
def createReport():
    sql = "SELECT data.create_report()"
    executeSql(sql)

def fillReport():
    param = ninterno.text()
    sql = "SELECT data.fill_report("+str(param)+")"
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


# Wire up our own signals    
def setSignals():
  
    # Parcela
    _dialog.findChild(QPushButton, "btnParcelaPdf").clicked.connect(openPdfUbicacio)
    _dialog.findChild(QLabel, "lblSector").linkActivated.connect(openURL)
    _dialog.findChild(QLabel, "lblClass").linkActivated.connect(openURL)

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

    myComposition = _iface.activeComposers()[PDF_UBICACIO].composition()
    myComposition.setAtlasMode(QgsComposition.PreviewAtlas)
    filePath = report_folder+refcat.text()+"_ubicacio.pdf"
    result = myComposition.exportAsPDF(filePath)
    if result:
        showInfo("PDF generated in: "+filePath)
        os.startfile(filePath)
    else:
        showWarning("PDF could not be generated in: "+filePath)
        
        
def openPdfZones():    

    # Get composition and Atlas
    myComposition = _iface.activeComposers()[PDF_ZONES].composition()   
    myComposition.setAtlasMode(QgsComposition.ExportAtlas)         
    myAtlas = myComposition.atlasComposition() 
    myAtlas.setSingleFile(True)

    filePath = report_folder+refcat.text()+"_zones.pdf"
    #print "filePath: "+filePath   
    #print "num. features: "+str(myAtlas.numFeatures())   
     
    # Prepare for first feature, so that we know paper size to begin with
    printer = QPrinter()
    painter = QPainter()
    myAtlas.beginRender()     
    myAtlas.prepareForFeature(0)
    myComposition.beginPrintAsPDF(printer, filePath)
    
    # Set the correct resolution
    myComposition.beginPrint(printer)
    printReady = painter.begin(printer)
    if not printReady:
        showWarning("PDF could not be generated at: "+filePath)
        return    
    
    progress = QProgressDialog("Rendering maps...", "Abort", 0, myAtlas.numFeatures())
    QApplication.setOverrideCursor(Qt.BusyCursor)
    
    for featureI in range(0, myAtlas.numFeatures()):
        print "feature: "+str(featureI)
        progress.setValue(featureI+1)
        # Process input events in order to allow aborting
        QCoreApplication.processEvents()
        if progress.wasCanceled():
            myAtlas.endRender()
            break
        if not myAtlas.prepareForFeature(featureI):
            showWarning("Atlas processing error")                
            progress.cancel()
            QApplication.restoreOverrideCursor()
            return
        # Start print on a new page if we're not on the first feature
        if featureI > 0:
            printer.newPage()
        myComposition.doPrint(printer, painter)
    
    myAtlas.endRender()
    painter.end()
    QApplication.restoreOverrideCursor()      
    
    # Show message and open PDF
    showInfo("PDF generated in: "+filePath)
    os.startfile(filePath)       


def openPdfZones_multi():

    myComposition = _iface.activeComposers()[PDF_ZONES].composition()   
    myComposition.setAtlasMode(QgsComposition.ExportAtlas)         
    myAtlas = myComposition.atlasComposition() 
    myAtlas.setSingleFile(False)
   
    # Generate atlas 
    #print "num. features: "+str(myAtlas.numFeatures())    
    myAtlas.beginRender()     
    for i in range(0, myAtlas.numFeatures()): 
        #print "feature: "+str(i)            
        myAtlas.prepareForFeature(i)       
        filePath = report_folder+refcat.text()+"_"+myAtlas.currentFilename()+".pdf"
        #print "filePath: "+filePath         
        result = myComposition.exportAsPDF(filePath)        
        if result:
            showInfo("PDF generated in: "+filePath)
            #os.startfile(filePath)        
        else:
            showWarning("PDF could not be generated in: "+filePath)               
        
    myAtlas.endRender()  


def openURL(url):

    urlPath = "file://"+current_path+"\\html\\"+url
    webbrowser.open(urlPath, 2)



#if __name__ == '__main__':
#    init()