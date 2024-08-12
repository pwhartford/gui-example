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

        #Connect buttons to functions
        self.loadFolderButton.clicked.connect(lambda: self.open_filepath(1))
        self.saveFolderButton.clicked.connect(self.save_filepath)

        #Connect our status bar actions to functions 
        self.saveConfigAction.triggered.connect(self.save_app_config)
        self.loadConfigAction.triggered.connect(self.load_app_config)

        self.actionLight.triggered.connect(lambda: self.change_theme('light'))
        self.actionDark.triggered.connect(lambda: self.change_theme('dark'))

        #Connect the scroll bar to image reader
        self.imageScrollBar.valueChanged.connect(lambda: self.update_image(self.imageScrollBar.value()))
        
        #Automatically load our app configuration
        self.load_app_config()

        #Automatically load the image if it exists
        self.get_images()

    #These two functions are basically the same - just for saving/loading...
    def open_filepath(self, var):
        #Create a file dialog to open a new folder - return it with a path object - default directory is record folder
        self.loadFolder = Path(QtWidgets.QFileDialog.getExistingDirectory(directory = str(self.loadFolder)))
        
        #Set the text to the file path
        self.loadFolderEdit.setText(str(self.loadFolder))

        #Automatically load images 
        self.get_images()

    def save_filepath(self):
        #Create a file dialog to open a new folder - return it with a path object - default directory is record folder
        self.saveFolder = Path(QtWidgets.QFileDialog.getExistingDirectory(directory = str(self.saveFolder)))
        
        #Set the text to the file path
        self.saveFolderEdit.setText(str(self.saveFolder))


    #This function loads default settings 
    def load_app_config(self): 
        #Create config parser object 
        self.settings = ConfigParser()

        #Check if the config file exists 
        if CONFIG_PATH.exists():
            #Read config file
            self.settings.read(CONFIG_PATH)

            #Set the widget values
            self.set_settings()

        #If the file doesn't exist, nothing will load :(
        else:
            #Automatically set light theme
            self.change_theme('light')
            
            #Save these as defaults
            self.loadFolder = Path('/')
            self.saveFolder = Path('/')


    #This function loads the default settings
    def set_settings(self):
        #Lets set the widget text to our settings file
        self.loadFolder = Path(self.settings['Folder Settings']['LoadFolder'])
        self.saveFolder = Path(self.settings['Folder Settings']['SaveFolder'])

        self.loadFolderEdit.setText(str(self.loadFolder))
        self.saveFolderEdit.setText(str(self.saveFolder))

        #Load Default Theme
        self.change_theme(self.settings['App Settings']['Theme'])
   
    #This function saves default settings
    def save_app_config(self):
        #Create a config parser object for the settings
        self.settings = ConfigParser()
        
        #Folder Settings create a nested dictionary
        self.settings['Folder Settings'] = {}
        self.settings['App Settings'] = {}

        #Now lets get the value of the folder boxes
        self.settings['Folder Settings']['LoadFolder'] = self.loadFolderEdit.text()
        self.settings['Folder Settings']['SaveFolder'] = self.saveFolderEdit.text()
        
        self.settings['App Settings']['theme'] = self.theme

        #Save the write the settings to our config file
        with open(CONFIG_PATH, 'w') as settings_file:
            self.settings.write(settings_file)

    #Quick theme changer - makes everything look good at once
    def change_theme(self, theme):
        #Save the theme variable and change the theme
        self.theme = theme
        qdarktheme.setup_theme(theme)

        #Change theme for plots
        self.livePlotWidget.change_theme(theme)
     

    #This tells the app the image files in our folder
    def get_images(self):
        #List all files in the image folder and sort
        self.imageList = sorted([file for file in self.loadFolder.glob(IMAGE_TYPE)])
        
        #Update widgets if there are images
        if len(self.imageList) > 0:
            #Set the scroll bar maximum 
            self.imageScrollBar.setMaximum(len(self.imageList)-1)

            #Enable the widgets 
            self.imageScrollBar.setEnabled(True)
            self.imageNumberLabel.setEnabled(True)
            self.imageResolutionLabel.setEnabled(True)
            
            #Update with the initial image
            self.update_image(0)

        #Disable the widgets if there arent any images
        else:
            #This can be simplified if they're all in the same group
            self.imageScrollBar.setDisabled(True)
            self.imageNumberLabel.setDisabled(True)
            self.imageResolutionLabel.setDisabled(True)

            self.livePlotWidget.cla() 
            self.imageNumberLabel.setText('Viewing Image: - of -, Name: -')
            self.imageResolutionLabel.setText('Image Resolution: 0x0')


    #When the scrollbar is changed, the plot will show a new image
    def update_image(self, num):
        #Read the image 
        try:
            #Read image from folder
            image = imread(self.imageList[num], as_gray=True)
      
        except: 
            return 
    
        #Clear axis - usually not the fastest option
        self.livePlotWidget.cla() 

        #Show the image
        self.livePlotWidget.canvas.ax.imshow(image, cmap = 'grey')

        #Turn off the axes
        self.livePlotWidget.canvas.ax.axis('off')

        self.livePlotWidget.canvas.figure.tight_layout()

        #Redraw the figure
        self.livePlotWidget.canvas.draw()

      
        #Update labels
        self.imageNumberLabel.setText('Image Number: %i of %i, Name: %s'%(num, len(self.imageList), self.imageList[num].name))
        self.imageResolutionLabel.setText('Image Resolution: %ix%i'%(image.shape[0], image.shape[1]))

  