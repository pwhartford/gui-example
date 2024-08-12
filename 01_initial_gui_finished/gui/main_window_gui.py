#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 11:54:46 2024

@author: peter
"""

#Import the matplotlib widget and main window
from gui.panels.main_window import Ui_MainWindow
from gui.extra_widgets import MplWidget

#Function Classes - we use this class for all of our functions
# from functions.pod_functions import ImageCutter, PODRunner

#Imports for pyqt5 widgets 
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSlot #This is for threading/signals 

#Dark theme - automatically applies nice stylesheet
import qdarktheme

#For configuration files
from configparser import ConfigParser
import numpy as np
from pathlib import Path

#For reading images
from skimage.io import imread, imshow, imsave  # this is for Matlab users


import matplotlib 
matplotlib.use('Qt5Agg')

#Create our config path object
CONFIG_PATH = Path(__file__).parent.parent.absolute() / 'config/app_config.cfg'

#Image filetype (hard coded) 
IMAGE_TYPE = '*.tif'

#Main Window Object
class MainWindow(Ui_MainWindow):
    #Init function (runs on creation)
    def __init__(self):
        #Inherit objects from our panel file
        super(MainWindow, self).__init__()
        
        #This is important for setting window properties 
        self.window = QtWidgets.QMainWindow()
        
        #This does all of the layout and attaches widgets to the window object
        self.setupUi(self.window) 
    
        #Create our plot widget and attach to the plot layout
        self.livePlotWidget = MplWidget(navigationToolbar = True)
        self.plotLayout.addWidget(self.livePlotWidget)     
     
        #Set load folder to default - this will be changed when we create a config file 
        self.loadFolder = Path('/')
        self.saveFolder = Path('/')

        #Connect buttons to functions
        self.loadFolderButton.clicked.connect(lambda: self.open_filepath(1))
        self.saveFolderButton.clicked.connect(self.save_filepath)

 
    #These two functions are basically the same - just for saving/loading...
    def open_filepath(self, var):
        #Create a file dialog to open a new folder - return it with a path object - default directory is record folder
        self.loadFolder = Path(QtWidgets.QFileDialog.getExistingDirectory(directory = str(self.loadFolder)))
        
        #Set the text to the file path
        self.loadFolderEdit.setText(str(self.loadFolder))

    def save_filepath(self):
        #Create a file dialog to open a new folder - return it with a path object - default directory is record folder
        self.saveFolder = Path(QtWidgets.QFileDialog.getExistingDirectory(directory = str(self.saveFolder)))
        
        #Set the text to the file path
        self.saveFolderEdit.setText(str(self.saveFolder))
