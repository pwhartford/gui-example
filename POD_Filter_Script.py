# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 11:37:58 2019

@author: mendez, torres
"""

import os  # This is to understand which separator in the paths (/ or \)

import matplotlib.image as mpimg
import numpy as np  # This is for doing math
from skimage.io import imread, imshow, imsave  # this is for Matlab users

def generate_filename(folder, number, pair, pic_format):
    """
    simple function to generate filenames
    :param folder: where to look or save
    :param number: number of the picture
    :param pair: a or b
    :param pic_format: format of the image
    :return:
    """
    return folder + os.sep + 'A'+'%03d' % (number + 1) + pair + '.' + pic_format


# Image Cropping, Flipping and pre-processing using the 1POD mode removal
# Fore more advanced version, see https://seis.bristol.ac.uk/~aexrt/PIVPODPreprocessing/
# To do list: Implement Frequency based filter.

# Ensure current working directory
cwd = os.path.dirname(os.path.realpath(__file__))
os.chdir(cwd) #chdir used for change directory
print(os.getcwd())

# Folder in
FOL_IN = 'RAW_IMAGES'
# Processing Images
FOL_OUT = 'Pre_Pro_PIV_IMAGES'  # Where will the result be
if not os.path.exists(FOL_OUT):
    os.mkdir(FOL_OUT)


# To define the crop area you will usually need to load at least one image 
# and plot on it a rectangle
Num = 10  # This is the number of the image
Name=generate_filename(FOL_IN, 10, 'a', 'tif')

Im = imread(Name, as_gray=True)
ny, nx = Im.shape
# Prepare for cropping (at this point you might want to check if the crop is ok)
X1 = 0
X2 = nx
Y1 = 50
Y2 = 950
crop_img = Im[Y1:Y2, X1:X2]

# Perform also the flipping
Crop_FLIP = np.fliplr(crop_img)
imshow(Im)
imshow(crop_img)
imshow(Crop_FLIP)

# We might decide to work with cropped images (and flipped!)
ny, nx = Crop_FLIP.shape


# We can now proceed with the removal of the first POD mode
# This is a good idea only if you have a lot of images; otherwise limit yourself to teh
# Fourier filtering only.
# In this case just comment from the lines ------
# Comment from here to remove the POD processing------------------------ 
########################  POD - 1 Mode Removal ##########################

def process_image_for_matrix_D(FOL_IN, iter, pair, X1, X2, Y1, Y2):
    """
    Function to process image
    :param FOL_IN: str folder in (for filename)
    :param iter: number of iteration (for filename)
    :param pair: str 'a' or 'b' (for filename)
    :param X1: int
    :param X2: int
    :param Y1: int
    :param Y2: int
    :return: np.float64 array
    """
    name = generate_filename(FOL_IN, iter, pair, pic_format="tif")  # Check it out: print(Name)
    print(name)
    Im = imread(name)  # Read the image as uint8 using mpimg
    # Warning, this is the part doing the cropping and the flipping
    # Cropping
    crop_img = Im[Y1:Y2, X1:X2]
    # Perform also the flipping
    Crop_FLIP = np.fliplr(crop_img)
    Imd = np.float64(Crop_FLIP)  # We work with floating number not integers
    ImV = np.reshape(Imd, ((nx * ny, 1)))  # Reshape into a column Vector
    return ImV


n_t = 100  # Number of Image Pairs
D_a = np.zeros((nx * ny, n_t))  # Initialize the Data matrix for image sequences A.
D_b = np.zeros((nx * ny, n_t))  # Initialize the Data matrix for image sequences B.

for k in range(0, n_t):
    # Prepare the Matrix D_a
    ImV = process_image_for_matrix_D(FOL_IN=FOL_IN, iter=k, pair='a', X1=X1, X2=X2, Y1=Y1, Y2=Y2)
    print('Loading ' + str(k) + '/' + str(n_t))  # Print a Message to update the user
    D_a[:, k] = ImV[:, 0]

    # Prepare the Matrix D_b
    ImV = process_image_for_matrix_D(FOL_IN=FOL_IN, iter=k, pair='b', X1=X1, X2=X2, Y1=Y1, Y2=Y2)
    print('Loading ' + str(k) + '/' + str(n_t))  # Print a Message to update the user
    D_b[:, k] = ImV[:, 0]

################ Computing the Filtered Matrices##########################
Ind_S = 1  # Number of modes to remove. If 0, the filter is not active!
# Compute the correlation matrix
print('Computing Correlation Matrices')
K_a = np.dot(D_a.transpose(), D_a)
print('K_a Ready')
K_b = np.dot(D_b.transpose(), D_b)
print('K_b Ready')

# Comput the Temporal basis for A
Psi, Lambda, _ = np.linalg.svd(K_a)

# Compute the Projection Matrix
PSI_CROP = Psi[:, Ind_S::]
PROJ = np.dot(PSI_CROP, PSI_CROP.transpose())
D_a_filt = np.dot(D_a, PROJ)
print('D_a Filt Ready')

# Comput the Temporal basis for B
Psi, Lambda, _ = np.linalg.svd(K_b)

# Compute the Projection Matrix
PSI_CROP = Psi[:, Ind_S::]
PROJ = np.dot(PSI_CROP, PSI_CROP.transpose())
D_b_filt = np.dot(D_b, PROJ)
print('D_b Filt Ready')


# Prepare Exporting the images
def export_images(matrix, folder, n_images, pair, shape):
    """
    :param matrix: np.array matrix to extract the images
    :param folder: str folder out
    :param n_images: int number of images
    :param pair: str "a" or "b"
    :param shape: tuple
    """
    (ny, nx) = shape
    for k in range(0, n_images):
        name = generate_filename(folder, k, pair=pair, pic_format="tif")  # Check it out: print(Name)
        print('Exporting %i'%k)
        Imd_V = matrix[:, k]
        Im = np.reshape(Imd_V, ((ny, nx)))
        Im[Im < 0] = 0  # Things below 0 are treated as zero
        Im2 = np.uint8(Im)
        imsave(name, Im2)

export_images(D_a_filt, FOL_OUT, n_images=n_t, pair='a', shape=(ny, nx))
export_images(D_b_filt, FOL_OUT, n_images=n_t, pair='b', shape=(ny, nx))
