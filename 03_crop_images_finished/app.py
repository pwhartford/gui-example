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


def main(): 
    #Create application object
    app = QtWidgets.QApplication(sys.argv)

    #Create main window object
    mainWindow = MainWindow()

    #Show main window
    mainWindow.window.show()

    #Stop script on exit
    sys.exit(app.exec())    


#Run script if it is main
if __name__ == '__main__':
    main()