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
from functions.pod_functions import ImageCutter, PODRunner

#Imports for pyqt5 widgets 
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSlot #This is for threading/signals 

#Dark theme - automatically applies nice stylesheet
import qdarktheme

#For configuration files
from configparser import ConfigParser
import numpy as np
from pathlib import Path
import sys

#For reading images
from skimage.io import imread, imshow, imsave  # this is for Matlab users


import matplotlib 
matplotlib.use('Qt5Agg')

#Create our config path object
CONFIG_PATH = Path(__file__).parent.parent.absolute() / 'config/app_config.cfg'
ICON_PATH = Path(__file__).parent.parent.absolute() / 'gui/icons'

#Image filetype (hard coded) 
IMAGE_EXTENSION_LIST = ['.tif', '.tiff', '.jpeg', '.png']

#Main Window Object
class MainWindow(Ui_MainWindow):
    #Init function (runs on creation)
    def __init__(self, app):
        #Inherit objects from our panel file
        super(MainWindow, self).__init__()

        #Fix for dark theme on python 12
        self.app = app
        
        #This is important for setting window properties 
        self.window = QtWidgets.QMainWindow()
        
        #This does all of the layout and attaches widgets to the window object
        self.setupUi(self.window)
        
        self.imageList = []
    
        #Create our plot widget and attach to the plot layout
        self.livePlotWidget = MplWidget(navigationToolbar = True)
        self.plotLayout.addWidget(self.livePlotWidget)     
     
        #Set load folder to default - this will be changed when we create a config file 
        self.loadFolder = Path('/')

        #Connect buttons to functions
        self.loadFolderButton.clicked.connect(self.open_filepath)

        #Connect our status bar actions to functions 
        self.saveConfigAction.triggered.connect(self.save_app_config)
        self.loadConfigAction.triggered.connect(self.load_app_config)

        self.actionLight.triggered.connect(lambda: self.change_theme('light'))
        self.actionDark.triggered.connect(lambda: self.change_theme('dark'))
        self.actionSurprise.triggered.connect(self.surprise)

        # self.podBatchBox.valueChanged.connect(self.get_images)
        # self.podPairBox.valueChanged.connect(self.get_images)

        #Connect the scroll bar to image reader
        self.imageScrollBar.valueChanged.connect(lambda: self.update_image(self.imageScrollBar.value()))

        #Cropping 
        self.xCropMinBox.valueChanged.connect(lambda: self.update_image(self.imageScrollBar.value()))
        self.xCropMaxBox.valueChanged.connect(lambda: self.update_image(self.imageScrollBar.value()))
        self.yCropMinBox.valueChanged.connect(lambda: self.update_image(self.imageScrollBar.value()))
        self.yCropMaxBox.valueChanged.connect(lambda: self.update_image(self.imageScrollBar.value()))
        self.cropResetButton.clicked.connect(self.update_crop_values)


        #Cutting pictures
        self.cuttingSaveButton.clicked.connect(self.save_cut_images)
        self.previewCutImagesCheckbox.clicked.connect(self.get_images)

        #POD Buttons
        self.podRunButton.clicked.connect(self.compute_pod_matrices)
        self.podContinueButton.clicked.connect(self.continue_pod_runner)
        self.showComputedImagesCheckbox.clicked.connect(self.update_image)

        self.podCutImagesCheckbox.clicked.connect(self.get_images)
        
        self.podBatchBox.valueChanged.connect(self.update_batch_boxes)
        self.podPairBox.valueChanged.connect(self.update_batch_boxes)


        for imageType in IMAGE_EXTENSION_LIST:
            self.imageTypeComboBox.addItem(imageType)

        #Automatically load our app configuration
        self.load_app_config()

        self.showCutImages = False
        self.surprise = False


        #Automatically load the image if it exists
        self.get_images()

    #These two functions are basically the same - just for saving/loading...
    def open_filepath(self, var):
        #Create a file dialog to open a new folder - return it with a path object - default directory is record folder
        self.loadFolder = Path(QtWidgets.QFileDialog.getExistingDirectory(directory = str(self.loadFolder)))
        
        #Set the text to the file path
        self.loadFolderEdit.setText(str(self.loadFolder))

        self.showCutImages = False
    

        #Automatically load images 
        self.get_images()


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


    #This function loads the default settings
    def set_settings(self):
        #Lets set the widget text to our settings file
        self.loadFolder = Path(self.settings['Folder Settings']['LoadFolder'])
        self.loadFolderEdit.setText(str(self.loadFolder))

        self.podModeBox.setValue(int(self.settings['POD Settings']['nModes']))
        self.podPairBox.setValue(int(self.settings['POD Settings']['nPairs']))
        self.podBatchBox.setValue(int(self.settings['POD Settings']['nBatches']))

        self.podFlipImageCheckbox.setChecked(bool(self.settings['POD Settings']['flipImages']))
        self.podCutImagesCheckbox.setChecked(bool(self.settings['POD Settings']['cutImages']))

        #Load Default Theme
        self.change_theme(self.settings['App Settings']['Theme'])
   
    #This function saves default settings
    def save_app_config(self):
        #Create a config parser object for the settings
        self.settings = ConfigParser()
        
        #Folder Settings create a nested dictionary
        self.settings['Folder Settings'] = {}
        self.settings['App Settings'] = {}
        self.settings['POD Settings'] = {} 

        #Now lets get the value of the folder boxes
        self.settings['Folder Settings']['LoadFolder'] = self.loadFolderEdit.text()
        
        self.settings['App Settings']['theme'] = self.theme

        #Settings for POD
        self.settings['POD Settings']['nModes'] = str(self.podModeBox.value())
        self.settings['POD Settings']['nPairs'] = str(self.podPairBox.value())
        self.settings['POD Settings']['flipImages'] = str(self.podFlipImageCheckbox.isChecked())
        self.settings['POD Settings']['nBatches'] = str(self.podBatchBox.value())
        self.settings['POD Settings']['cutImages'] = str(self.podCutImagesCheckbox.isChecked())

        #Save the write the settings to our config file
        with open(CONFIG_PATH, 'w') as settings_file:
            self.settings.write(settings_file)

    #Quick theme changer - makes everything look good at once
    def change_theme(self, theme):
        #Save the theme variable and change the theme
        self.theme = theme
        if sys.version_info.minor==12:
            self.app.setStyleSheet(qdarktheme.load_stylesheet(theme))
        else:
            qdarktheme.setup_theme(theme)
        
        #Change theme for plots
        self.livePlotWidget.change_theme(theme)
     

    #This tells the app the image files in our folder
    def get_images(self):
        #List all files in the image folder and sort
        self.imageList = sorted([file for file in self.loadFolder.glob('*%s'%self.imageTypeComboBox.currentText())])
        
        #Update widgets if there are images
        if len(self.imageList) > 0:
            #Enable the widgets 
            self.imageScrollBar.setEnabled(True)
            self.imageNumberLabel.setEnabled(True)
            self.imageResolutionLabel.setEnabled(True)
            
            #Image crop group
            self.cuttingGroup.setEnabled(True)
            self.cuttingSaveButton.setEnabled(True)
            self.cuttingSaveProgressBar.setEnabled(True)
            self.cuttingSaveFolderEdit.setEnabled(True)

            #POD Group
            self.podFilterGroup.setEnabled(True)
            self.podRunButton.setEnabled(True)
            self.podProgressBar.setEnabled(True)
            self.podSettingsBox.setEnabled(True)

            currentIm = self.imageScrollBar.value()
         
            #Update with the initial image
            #Read image
            image = imread(self.imageList[currentIm], as_gray = True)
            self.imageShape = [image.shape[0], image.shape[1]]

            if self.previewCutImagesCheckbox.isChecked():
                self.imageNumber = (len(self.imageList)-1)*2
                self.imageShape[0] = self.imageShape[0]//2
            
            elif self.showComputedImagesCheckbox.isChecked():
                self.imageNumber = self.podRunner.D_a_filt.shape[1]
                self.imageShape = self.podRunner.imageShape

            else:
                image = imread(self.imageList[currentIm], as_gray=True)
                self.imageNumber = len(self.imageList)-1

            self.imageScrollBar.setMaximum(self.imageNumber)
            self.update_batch_boxes()
            
            if self.podCutImagesCheckbox.isChecked():
                self.podPairBox.setValue(len(self.imageList))

            else:
                self.podPairBox.setValue(len(self.imageList)//2)

            
            self.update_crop_values(currentIm)

        #Disable the widgets if there arent any images
        else:
            #This can be simplified if they're all in the same group
            self.imageScrollBar.setDisabled(True)
            self.imageNumberLabel.setDisabled(True)
            self.imageResolutionLabel.setDisabled(True)

            #Image crop group
            self.cuttingGroup.setDisabled(True)
            self.podFilterGroup.setDisabled(True)
            self.podSettingsBox.setDisabled(True)

            self.livePlotWidget.cla() 
            self.imageNumberLabel.setText('Viewing Image: - of -, Name: -')
            self.imageResolutionLabel.setText('Image Resolution: 0x0')

    def update_batch_boxes(self):
        if self.podCutImagesCheckbox.isChecked():
            self.podPairBox.setMaximum(len(self.imageList))
            self.podImagesPerBatchLabel.setText('Images Per Batch: %i'%(self.podPairBox.value()/self.podBatchBox.value()))
            
        else:
            self.podPairBox.setMaximum(len(self.imageList)//2)
            self.podImagesPerBatchLabel.setText('Images Per Batch: %i'%(self.podPairBox.value()/self.podBatchBox.value()))



    def update_crop_values(self, currentIm):
        #Update Crop Values
        self.xCropMinBox.setMaximum(self.imageShape[1])
        self.xCropMaxBox.setMaximum(self.imageShape[1])
        self.yCropMinBox.setMaximum(self.imageShape[0])
        self.yCropMaxBox.setMaximum(self.imageShape[0])


        self.xCropMinBox.setValue(0)
        self.yCropMinBox.setValue(0)
        self.xCropMaxBox.setValue(self.imageShape[1])
        self.yCropMaxBox.setValue(self.imageShape[0])

        self.update_image(currentIm)


    #When the scrollbar is changed, the plot will show a new image
    def update_image(self, num):
        #Read the image 
        try:
            if self.surprise: 
                image = imread(ICON_PATH / 'Mehmet.jpeg')
                imageName = 'Mehmet'
                self.imageNumber = 0
                self.surprise = False

            #Preview images from POD if we want to
            elif self.showComputedImagesCheckbox.isChecked():
                #Select image pair
                if num%2==1: #even images are b
                    num-=1
                    image = np.copy(self.podRunner.D_b_filt[:, num])
                    imageName = 'B_FILTERED_' + self.imageList[num].name

                else:
                    image = np.copy(self.podRunner.D_a_filt[:, num])
                    imageName = 'A_FILTERED_' + self.imageList[num].name

                (nx, ny) = self.podRunner.imageShape
                image = np.reshape(image, ((nx, ny)))
                image[image < 0] = 0  # Things below 0 are treated as zero
            
                #Cast to uint 
                image = np.uint8(image)
               
                #Image is already cropped so we don't need this 


            elif self.previewCutImagesCheckbox.isChecked():
                #Preview cut images 
                if num%2==1:
                    num-=1 
                    image = imread(self.imageList[num], as_gray=True)
                    image = image[image.shape[0]//2:image.shape[0],:]

                    imageName = 'B_' + self.imageList[num].name

                else:
                    image = imread(self.imageList[num], as_gray=True)
                    image = image[:image.shape[0]//2, :]

                    imageName = 'A_' + self.imageList[num].name

                #Apply crop preview 

                image = image[self.yCropMinBox.value():self.yCropMaxBox.value(), self.xCropMinBox.value():self.xCropMaxBox.value()]

            #Else we read the image
            else:
                #Read image from folder
                image = imread(self.imageList[num], as_gray=True)
                imageName = self.imageList[num].name

                #Apply crop preview
                image = image[self.yCropMinBox.value():self.yCropMaxBox.value(), self.xCropMinBox.value():self.xCropMaxBox.value()]
            

            #Clear axis - usually not the fastest option
            self.livePlotWidget.cla() 

            #Show the image
            self.livePlotWidget.canvas.ax.imshow(image, cmap = 'grey', interpolation = 'none')

            #Turn off the axes
            self.livePlotWidget.canvas.ax.axis('off')

            self.livePlotWidget.canvas.figure.tight_layout()

            #Redraw the figure
            self.livePlotWidget.canvas.draw()

        
            #Update labels
            self.imageNumberLabel.setText('Image Number: %i of %i, Name: %s'%(num, self.imageNumber, imageName))
            self.imageResolutionLabel.setText('Image Resolution: %ix%i'%(image.shape[0], image.shape[1]))
       

        except Exception as e:
            print(e) 
            return 
    
       
    def save_cut_images(self):
        #Create image cropper class
        settings = {}
        settings['cropList'] = [self.xCropMinBox.value(), 
                                self.xCropMaxBox.value(),
                                self.yCropMinBox.value(),
                                self.yCropMaxBox.value()]
        settings['saveCrop'] = self.cutApplyCropCheckbox.isChecked() 

        self.imageCutter = ImageCutter(self.imageList, self.loadFolder, settings)

        #Connect the signal to updating progress bar
        self.imageCutter.saveUpdateSignal.connect(self.update_cut_save_bar)    

        if self.cuttingSaveFolderEdit.text()=='':
            self.imageCutter.saveFolder = self.loadFolder / 'cut'
        
        else:
            self.imageCutter.saveFolder = self.loadFolder / self.cuttingSaveFolderEdit.text() 

        self.imageCutter.start()

    def update_cut_save_bar(self, percent, label):
        #Set the percentage
        self.cuttingSaveProgressBar.setValue(int(percent))

        #Update the progress
        self.cuttingSaveProgressBar.setFormat(label)


    def update_cut_folder(self, finished):
        if finished:
            self.showCutImages = True 
            self.get_images()

      

    def compute_pod_matrices(self):
        #Collect settings
        settings = {} 
        settings['nModes'] = self.podModeBox.value() 
        settings['nPairs'] = self.podPairBox.value()//self.podBatchBox.value()
        settings['flipImage'] = self.podFlipImageCheckbox.isChecked() 

        settings['cutImages'] = self.podCutImagesCheckbox.isChecked()
        settings['nBatches'] = self.podBatchBox.value()

        #Crop list - [X1, X2, Y1, Y2]
        settings['cropList'] = [self.xCropMinBox.value(), 
                                self.xCropMaxBox.value(),
                                self.yCropMinBox.value(),
                                self.yCropMaxBox.value()]

        #Create podRunner object
        self.podRunner = PODRunner(self.imageList, self.loadFolder, settings) 


        #Connect signals to functions
        self.podRunner.updateSignal.connect(self.update_pod_bar)
        self.podRunner.finishedComputation.connect(self.on_finished_computing)

        self.podRunButton.setDisabled(True)

        #Set the function to compute matrix and start
        self.podRunner.function = 'save'
        
        if self.podSaveFolderEdit.text() == '':
            self.podRunner.saveFolder = self.loadFolder / 'pod_images'
        else:
            self.podRunner.saveFolder = self.loadFolder / self.podSaveFolderEdit.text() 

        self.podRunner.start()

    def continue_pod_runner(self):
        self.podRunner.continue_pod = True 
        self.podRunner.start()

    def on_finished_computing(self, finished):
        if finished:
            self.podContinueButton.setEnabled(True)
            self.podSaveFolderEdit.setEnabled(True)
            self.podSaveFolderLabel.setEnabled(True)

            self.showComputedImagesCheckbox.setEnabled(True)
            self.showComputedImagesCheckbox.setChecked(True)
            self.get_images()
        
        self.podRunButton.setEnabled(True)

    #Functions to update POD progress bars
    def update_pod_bar(self, percent, label):
        #Set the percentage
        self.podProgressBar.setValue(int(percent))

        #Update the progress
        self.podProgressBar.setFormat(label)

    def surprise(self):
        self.surprise = True 
        self.update_image(0)

            