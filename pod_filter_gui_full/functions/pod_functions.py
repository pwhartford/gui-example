#This is for threading and connecting widgets
from PyQt5.QtCore import QThread, pyqtSignal

#This is for reading images
from skimage.io import imread, imshow, imsave  # this is for Matlab users

from pathlib import Path
import numpy as np



class ImageCutter(QThread):
    #This is our signal that takes a number 
    saveUpdateSignal = pyqtSignal(float, str)

    #This tells us that the thread is finished and if it succeeded
    finishedSaving = pyqtSignal(bool)

    def __init__(self, imageList, saveFolder, settings):
        #Inherit the QThread Class
        super(ImageCutter, self).__init__()

        #We need to know our save folder and the list of our image paths
        self.imageList = imageList 

        #Crop images before saving 
        self.saveCrop = settings['saveCrop'] 
        self.cropList = settings['cropList']

        #Default save folder
        self.saveFolder = saveFolder / 'cut'

        #Create function object
        self.function = 'cut'


    def save_images(self):
        #Make the folder if it doesn't exist
        self.saveFolder.mkdir(exist_ok = True)

        try:
            for ii, image in enumerate(self.imageList): 
                imageArray = imread(image)
                imageShape = imageArray.shape[0]

                #Create image names for each pair
                imageNameA = self.saveFolder / ('A%04da.tif'%ii)
                imageNameB = self.saveFolder / ('A%04db.tif'%ii)
                
                imageA = imageArray[:imageShape//2, :]
                imageB = imageArray[imageShape//2:, :]

                if self.saveCrop:

                    imageA = imageA[self.cropList[2]:self.cropList[3], self.cropList[0]:self.cropList[1]]
                    imageB = imageB[self.cropList[2]:self.cropList[3], self.cropList[0]:self.cropList[1]]

                #Save the image pairs
                imsave(imageNameA, imageA)
                imsave(imageNameB, imageB)

                self.saveUpdateSignal.emit(ii/len(self.imageList)*100, 'Saving Image Pair %i of %i'%(ii, len(self.imageList)))
        
        except:
            self.saveUpdateSignal.emit(0, 'Failed')
            self.finishedSaving.emit(False)

        self.saveUpdateSignal.emit(100, 'Finished')
        self.finishedSaving.emit(True)

    #This is what runs in the thread
    def run(self):
        self.save_images()



class PODRunner(QThread):
    #Our signals to update progress bars
    updateSignal = pyqtSignal(float, str)

    #Our signal to indicate if things finished
    finishedComputation = pyqtSignal(bool)
    finishedSaving = pyqtSignal(bool)


    def __init__(self, imageList, saveFolder, settings):
        super(PODRunner, self).__init__() 

        self.cutImages = settings['cutImages']

        #We need to know our save folder and the list of our image paths
        self.imageList = imageList 

        self.saveFolder = saveFolder / 'pod_output'

        #Make the folder if it doesn't exist

        if not self.cutImages:
            #Split the list into a and b 
            self.imageAList = []
            self.imageBList = []

            for image in self.imageList:
                if image.name[-5] == 'a':
                    self.imageAList.append(image)
                elif image.name[-5] == 'b':
                    self.imageBList.append(image) 

        self.continue_pod = False
            
        #Grab information from settings dictionary
        # Number of modes to remove. If 0, the filter is not active!
        self.nModes = settings['nModes']
        self.nPairs = settings['nPairs']
        self.flipImage = settings['flipImage']
        
        #Batches to Run
        self.nBatches = settings['nBatches']

        #Crop list - [X1, X2, Y1, Y2]
        self.cropList = settings['cropList'] 

        #This variable changes if we want to save/compute the filtered matrix
        self.function = 'compute_matrix'
        
    def continue_batches(self):
        self.save_images(0)
        for batch in range(1, self.nBatches):
            self.pod_batch(batch)
            self.save_images(batch)

    def pod_batch(self, batch):
        #Prepare image matrix and calculate shape
        imInitial = imread(self.imageList[0])

        if self.cutImages:
            imInitial = imInitial[:imInitial.shape[0]//2, :]

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
        
            imageNumber = k+batch*self.nPairs
            
            if self.cutImages:  
                #Read images
                image = imread(self.imageList[imageNumber])
                imA = image[:image.shape[0]//2,:]
                imB = image[image.shape[0]//2:,:]

            else:
                if len(self.imageAList)==0:
                    self.updateSignal.emit(0, 'Failed, could not find image pairs in folder')
                    self.finishedComputation.emit(False)
                    return 
                
                imA = imread(self.imageAList[imageNumber])
                imB = imread(self.imageBList[imageNumber])
    
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

            self.updateSignal.emit(k/self.nPairs*100, '[Batch %i of %i] Processed image pair %i of %i'%(batch+1, self.nBatches, k, self.nPairs))

        self.updateSignal.emit(0, '[Batch %i of %i] Computing Correlation Matrices'%(batch+1, self.nBatches))

        # Compute the correlation matrix
        K_a = np.dot(D_a.transpose(), D_a)
        K_b = np.dot(D_b.transpose(), D_b)

        self.updateSignal.emit(0, '[Batch %i of %i] Computing Filtered A Matrix'%(batch+1, self.nBatches))

        # Comput the Temporal basis for A
        Psi, Lambda, _ = np.linalg.svd(K_a)

        # Compute the Projection Matrix
        PSI_CROP = Psi[:, self.nModes::]
        PROJ = np.dot(PSI_CROP, PSI_CROP.transpose())
        self.D_a_filt = np.dot(D_a, PROJ)

        self.updateSignal.emit(50, '[Batch %i of %i] Computing Filtered B Matrix'%(batch+1, self.nBatches))

        # Compute the Temporal basis for B
        Psi, Lambda, _ = np.linalg.svd(K_b)

        # Compute the Projection Matrix
        PSI_CROP = Psi[:, self.nModes::]
        PROJ = np.dot(PSI_CROP, PSI_CROP.transpose())
        self.D_b_filt = np.dot(D_b, PROJ)

        self.updateSignal.emit(100, '[Batch %i of %i] Finished Computing'%(batch+1, self.nBatches))
        self.finishedComputation.emit(True)


      
    def save_images(self, batch):
        #Make the folder if it doesnt exist
        self.saveFolder.mkdir(exist_ok = True)

        #Get image shape
        (ny, nx) = self.imageShape
        for k in range(0, self.nPairs):
            imageNumber = k+batch*self.nPairs

            #Save A images
            imdA = np.copy(self.D_a_filt[:, k])
            imPODA = np.reshape(imdA, ((ny, nx)))
            imPODA[imPODA < 0] = 0  # Things below 0 are treated as zero
            
            imPODA = np.uint8(imPODA)
            imsave(self.saveFolder / ('A%04da.tif'%imageNumber), imPODA)

            #Save b images
            imdB = np.copy(self.D_b_filt[:, k])
            imPODB = np.reshape(imdB, ((ny, nx)))
            imPODB[imPODB < 0] = 0  # Things below 0 are treated as zero
            
            imPODB = np.uint8(imPODB)
            imsave(self.saveFolder / ('A%04db.tif'%imageNumber), imPODB)

            #Update the signal
            self.updateSignal.emit(k/self.nPairs*100, '[Batch %i of %i] Saving Image Pair %i of %i'%(batch+1, self.nBatches, k, self.nPairs))

        self.updateSignal.emit(100, '[Batch %i of %i] Finished Saving'%(batch+1, self.nBatches))
        self.finishedSaving.emit(True)

    def run(self):   
        if self.continue_pod:
            self.continue_pod = False
            self.continue_batches()
        else:
            self.pod_batch(0)
