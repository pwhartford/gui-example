#This is for threading and connecting widgets
from PyQt5.QtCore import QThread, pyqtSignal

#This is for reading images
from skimage.io import imread, imshow, imsave  # this is for Matlab users

from pathlib import Path
import numpy as np

class ImageCutter(QThread):
    #This is our signal that takes a number 
    updateSignal = pyqtSignal(float)

    #This tells us that the thread is finished and if it succeeded
    finished = pyqtSignal(bool)


    def __init__(self, imageList, saveFolder):
        #Inherit the QThread Class
        super(ImageCutter, self).__init__()

        #We need to know our save folder and the list of our image paths
        self.imageList = imageList 
        self.saveFolder = saveFolder / 'cut'

        #Make the folder if it doesn't exist
        self.saveFolder.mkdir(exist_ok = True)

    #This function does the cropping
    def cut_images(self):
        #This does the cropping
        try:
            for ii, image in enumerate(self.imageList): 
                #Read the image and get the shape
                imageArray = imread(image)
                imageShape = imageArray.shape[0]

                #Create image names for each pair
                imageNameA = self.saveFolder / ('cut_%04d_a.tif'%ii)
                imageNameB = self.saveFolder / ('cut_%04d_b.tif'%ii)

                #Save the image pairs
                imsave(imageNameA, imageArray[0:imageShape//2, :])
                imsave(imageNameB, imageArray[imageShape//2:imageShape, :])

                #Update the progress bar
                self.updateSignal.emit(ii)
            
            #Makes the progress bar satisfying
            self.updateSignal.emit(len(self.imageList))
            self.finished.emit(True)

        except:
            self.finished.emit(False)
            return 
    
    #This is what runs in the thread
    def run(self):
        self.cut_images()