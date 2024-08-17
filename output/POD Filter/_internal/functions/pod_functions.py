#This is for threading and connecting widgets
from PyQt5.QtCore import QThread, pyqtSignal

#This is for reading images
from skimage.io import imread, imshow, imsave  # this is for Matlab users

from pathlib import Path
import numpy as np



class ImageCutter(QThread):
    #This is our signal that takes a number 
    updateSignal = pyqtSignal(float, str)
    saveUpdateSignal = pyqtSignal(float, str)

    #This tells us that the thread is finished and if it succeeded
    finished = pyqtSignal(bool)
    finishedSaving = pyqtSignal(bool)

    def __init__(self, imageList, saveFolder):
        #Inherit the QThread Class
        super(ImageCutter, self).__init__()

        #We need to know our save folder and the list of our image paths
        self.imageList = imageList 

        #Default save folder
        self.saveFolder = saveFolder / 'cut'

        #Create function object
        self.function = 'cut'
  
    #This function does the cropping
    def cut_images(self):
        image = self.imageList[0]
        imageArray = imread(image)
       
        #This does the cropping
        self.imagesA = np.zeros((imageArray.shape[0]//2, imageArray.shape[1], len(self.imageList)))  # Initialize the Data matrix for image sequences A.
        self.imagesB = np.zeros((imageArray.shape[0]//2, imageArray.shape[1], len(self.imageList)))  # Initialize the Data matrix for image sequences B.


        try:
            for ii, image in enumerate(self.imageList): 
                #Read the image and get the shape
                imageArray = imread(image)


                #Put the images in each array
                self.imagesA[:,:,ii] = imageArray[0:imageArray.shape[0]//2,:]
                self.imagesB[:,:,ii] = imageArray[imageArray.shape[0]//2:imageArray.shape[0],:]

                #Update the progress bar
                self.updateSignal.emit(ii/len(self.imageList)*100, 'Cutting Image %i of %i'%(ii, len(self.imageList)))
            
       
        except:
            self.updateSignal.emit(0, 'Failed')
            self.finished.emit(False)
            return 
       
        #Makes the progress bar satisfying
        self.updateSignal.emit(100, 'Finished')
        self.finished.emit(True)


    def save_images(self):
        #Make the folder if it doesn't exist
        self.saveFolder.mkdir(exist_ok = True)

        try:
            for ii, image in enumerate(self.imageList): 
                imageArray = imread(image)
                imageShape = imageArray.shape[0]

                #Create image names for each pair
                imageNameA = self.saveFolder / ('cut_%04d_a.tif'%ii)
                imageNameB = self.saveFolder / ('cut_%04d_b.tif'%ii)
                

                #Save the image pairs
                imsave(imageNameA, imageArray[0:imageShape//2, :])
                imsave(imageNameB, imageArray[imageShape//2:imageShape, :])

                self.saveUpdateSignal.emit(ii/len(self.imageList)*100, 'Saving Image %i of %i'%(ii, len(self.imageList)))
        
        except:
            self.saveUpdateSignal.emit(0, 'Failed')
            self.finishedSaving.emit(False)

        self.saveUpdateSignal.emit(100, 'Finished')
        self.finishedSaving.emit(True)

    #This is what runs in the thread
    def run(self):
        if self.function == 'cut':
            self.cut_images()
        
        elif self.function == 'save':
            self.save_images()



class PODRunner(QThread):
    #Our signals to update progress bars
    updateSignal = pyqtSignal(float, str)
    saveSignal = pyqtSignal(float, str)

    #Our signal to indicate if things finished
    finishedComputation = pyqtSignal(bool)
    finishedSaving = pyqtSignal(bool)


    def __init__(self, imageList, saveFolder, settings):
        super(PODRunner, self).__init__() 

        self.useImageFiles = settings['useImageFiles']

        #We need to know our save folder and the list of our image paths
        self.imageList = imageList 

        self.saveFolder = saveFolder / 'POD_Output'

        #Make the folder if it doesn't exist

        if self.useImageFiles:
            #Split the list into a and b 
            self.imageAList = []
            self.imageBList = []

            for image in self.imageList:
                if image.name[-5] == 'a':
                    self.imageAList.append(image)
                elif image.name[-5] == 'b':
                    self.imageBList.append(image) 

            
        #Grab information from settings dictionary
        # Number of modes to remove. If 0, the filter is not active!
        self.nModes = settings['nModes']
        self.nPairs = settings['nPairs']
        self.flipImage = settings['flipImage']

        #Crop list - [X1, X2, Y1, Y2]
        self.cropList = settings['cropList'] 

        #This variable changes if we want to save/compute the filtered matrix
        self.function = 'compute_matrix'

    def compute_filtered_matrix(self):
        #Prepare image matrix and calculate shape
        if self.useImageFiles:
            imInitial = imread(self.imageAList[0])
        
        else:
            imInitial = self.imagesA[:,:,0]

        #Create image crop
        croppedImage = imInitial[self.cropList[2]:self.cropList[3], self.cropList[0]:self.cropList[1]]

        #Flip the image if we want to 
        if self.flipImage:
            croppedImage = np.fliplr(croppedImage)

        #Get the shape of the image
        self.imageShape = croppedImage.shape
        ny, nx = self.imageShape 


     
        #Create matrix to concatenate imasges
        D_a = np.zeros((nx * ny, self.nPairs))  # Initialize the Data matrix for image sequences A.
        D_b = np.zeros((nx * ny, self.nPairs))  # Initialize the Data matrix for image sequences B.

        #Update progress
        self.updateSignal.emit(0, 'Start Processing')
        
        #Process image pairs and concatenate
        for k in range(0, self.nPairs):       
            if self.useImageFiles:  
                #Read images
                imA = imread(self.imageAList[k])
                imB = imread(self.imageBList[k])
            
            else:
                #Take images from array 
                imA = self.imagesA[:,:,k]
                imB = self.imagesB[:,:,k]
      
            #Create image crop
            cropA = imA[self.cropList[2]:self.cropList[3], self.cropList[0]:self.cropList[1]]
            cropB = imB[self.cropList[2]:self.cropList[3], self.cropList[0]:self.cropList[1]]

            #Flip the image if we want to 
            if self.flipImage:
                cropA = np.fliplr(cropA)
                cropB = np.fliplr(cropB)

            #Cast to float array
            cropA = np.float64(cropA)  # We work with floating number not integers
            cropB = np.float64(cropB)  # We work with floating number not integers
            
            # Reshape into a column Vector
            cropA = np.reshape(cropA, ((nx * ny, 1)))  
            cropB = np.reshape(cropB, ((nx * ny, 1))) 

            #Append to matrix 
            D_a[:, k] = cropA[:, 0]
            D_b[:, k] = cropB[:, 0]

            self.updateSignal.emit(k/self.nPairs*100, 'Processed image %i of %i'%(k, self.nPairs))

        self.updateSignal.emit(0, 'Computing Correlation Matrices')

        # Compute the correlation matrix
        K_a = np.dot(D_a.transpose(), D_a)
        K_b = np.dot(D_b.transpose(), D_b)

        self.updateSignal.emit(0, 'Computing Filtered A Matrix')

        # Comput the Temporal basis for A
        Psi, Lambda, _ = np.linalg.svd(K_a)

        # Compute the Projection Matrix
        PSI_CROP = Psi[:, self.nModes::]
        PROJ = np.dot(PSI_CROP, PSI_CROP.transpose())
        self.D_a_filt = np.dot(D_a, PROJ)

        self.updateSignal.emit(50, 'Computing Filtered B Matrix')

        # Comput the Temporal basis for B
        Psi, Lambda, _ = np.linalg.svd(K_b)

        # Compute the Projection Matrix
        PSI_CROP = Psi[:, self.nModes::]
        PROJ = np.dot(PSI_CROP, PSI_CROP.transpose())
        self.D_b_filt = np.dot(D_b, PROJ)

        self.updateSignal.emit(100, 'Finished')
        self.finishedComputation.emit(True)


    def save_images(self):
        #Make the folder if it doesnt exist
        self.saveFolder.mkdir(exist_ok = True)

        #Get image shape
        (ny, nx) = self.imageShape
        for k in range(0, self.nPairs):
            #Save A images
            imdA = np.copy(self.D_a_filt[:, k])
            imPODA = np.reshape(imdA, ((ny, nx)))
            imPODA[imPODA < 0] = 0  # Things below 0 are treated as zero
            
            imPODA = np.uint8(imPODA)
            imsave(self.saveFolder / ('POD_Filt_%03d_a.tif'%k), imPODA)

            #Save b images
            imdB = np.copy(self.D_b_filt[:, k])
            imPODB = np.reshape(imdB, ((ny, nx)))
            imPODB[imPODB < 0] = 0  # Things below 0 are treated as zero
            
            imPODB = np.uint8(imPODB)
            imsave(self.saveFolder / ('POD_Filt_%03d_b.tif'%k), imPODB)

            #Update the signal
            self.saveSignal.emit(k/self.nPairs*100, 'Saving Image Pair %i of %i'%(k, self.nPairs))

        self.saveSignal.emit(100, 'Finished Saving')
        self.finishedSaving.emit(True)

    def run(self):
        if self.function == 'save':
            self.save_images()
        
        elif self.function == 'compute_matrix':
            self.compute_filtered_matrix() 