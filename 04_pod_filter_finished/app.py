#GUI created by Peter Hartford - Thanks to Mehmet Arslan for his feedback

from pathlib import Path
import os, sys
   
#Current File Directory - pathlib is great for this
FILE_PATH = Path(__file__).parent.absolute()
sys.path.insert(0,str(FILE_PATH))

#Change directory to current file path
os.chdir(FILE_PATH)

from PyQt5 import QtWidgets, QtGui
import sys 

#Import our main window file
from gui.main_window_gui import MainWindow

ICON_PATH = Path(__file__).parent.absolute() / 'gui/icons/vki-blue.jpg'


def main(): 
    #Create application object
    app = QtWidgets.QApplication(sys.argv)

    app.setWindowIcon(QtGui.QIcon(str(ICON_PATH)))

    #Create main window object
    mainWindow = MainWindow(app)

    #Show main window
    mainWindow.window.show()

    #Stop script on exit
    sys.exit(app.exec())    


#Run script if it is main
if __name__ == '__main__':
    main()