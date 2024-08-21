# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 16:42:13 2019

@author: Theo
"""

# add two directories that include the new files
# note that we need to import openpiv in a separate, original namespace
# so we can use everything from openpiv as openpiv.filters and whatever is 
# going to replace it will be just filteers (for example)

import os
import matplotlib.pyplot as plt
import numpy as np
from openpiv.windef import piv
from pathlib import Path


plt.close('all')

MAIN_DIR = Path('/media/peter/share/Documents/Data/PIV Data/mehmet')
IMAGE_FILEPATH  = MAIN_DIR / 'POD_Output'



class Settings(object):
    pass  
settings = Settings()

# Data related settings
# Folder with the images to process
settings.filepath_images = str(IMAGE_FILEPATH)

# Folder for the outputs
settings.save_path = str(IMAGE_FILEPATH / 'results_piv')

# Root name of the output Folder for Result Files
settings.save_folder_suffix = 'Test_RAW'

# Format and Image Sequence
# If you write A*a.tif and A*b.tif, it will process everything
# If you write Just A001.tif and A002.tif, it will process only that pair

settings.frame_pattern_a = 'A*a.tif'
settings.frame_pattern_b = 'A*b.tif'  


#ROI 
# (50,300,50,300) #Region of interest: (xmin,xmax,ymin,ymax) or 'full' for full image
settings.roi = 'full'

 
# Image preprocessing
# 'None' for no masking, 'edges' for edges masking, 'intensity' for intensity masking
# WARNING: This part is under development so better not to use MASKS
settings.dynamic_masking_method = False
settings.dynamic_masking_threshold = 0.005
settings.dynamic_masking_filter_size = 7 
settings.static_mask = None
settings.image_mask = False

# Processing Parameters
#Correlation Settings
settings.correlation_method = 'linear'  # 'circular' or 'linear'
settings.normalized_correlation=False

#Number of passes
settings.num_iterations = 1  # select the number of PIV passes

# Interrogation window size for each pass. 
# For the moment, it should be a power of 2 
settings.windowsizes = (32, 16, 8) # if longer than n iteration the rest is ignored

# The overlap of the interroagtion window for each pass.
settings.overlap = (16, 8, 4) # This is 50% overlap

# Has to be a value with base two. In general window size/2 is a good choice.
# methode used for subpixel interpolation: 'gaussian','centroid','parabolic'
settings.subpixel_method = 'gaussian'

# Order of the image interpolation for the window deformation
settings.deformation_method = 'symmetric'
settings.interpolation_order = 3

#Scaling Factor - camera pose settings (calibrate for this)
settings.scaling_factor = 12e3  # scaling factor pixel/meter (i.e. 45 micron/pixel)
settings.dt = 100e-6 # time between to frames (in seconds)

#Signal to noise ratio options (only for the last pass)
# It is possible to decide if the S/N should be computed (for the last pass) or not
settings.extract_sig2noise = True  # 'True' or 'False' (only for the last pass)

# Method used to calculate the signal to noise ratio 'peak2peak' or 'peak2mean'
settings.sig2noise_method = 'peak2peak'

# Select the width of the mask to avoid pixels next to the main peak
settings.sig2noise_mask = 2
# If extract_sig2noise==False the values in the signal to noise ratio
# output column are set to NaN

# Vector validation options
# choose if you want to do validation of the first pass: True or False
settings.validation_first_pass = True
# only effecting the first pass of the interrogation the following passes
# in the multipass will be validated

# Validation Parameters
# The validation is done at each iteration based on three filters.
# The first filter is based on the min/max ranges. Observe that these values are defined in
# terms of minimum and maximum displacement in pixel/frames.
settings.min_max_u_disp = (-30, 30)
settings.min_max_v_disp = (-30, 30)

# The second filter is based on the global STD threshold
settings.std_threshold = 10 # threshold of the std validation

# The third filter is the median test (not normalized at the moment)
settings.median_threshold = 1  # threshold of the median validation
settings.median_size = 1 #defines the size of the local median
# On the last iteration, an additional validation can be done based on the S/N.
'Validation based on the signal to noise ratio'
# Note: only available when extract_sig2noise==True and only for the last
# pass of the interrogation
# Enable the signal to noise ratio validation. Options: True or False
settings.sig2noise_validate = True # This is time consuming
# minmum signal to noise ratio that is need for a valid vector
settings.sig2noise_threshold = 1
settings.use_vectorized = False

'Outlier replacement or Smoothing options'
# Replacment options for vectors which are masked as invalid by the validation
settings.replace_vectors = True # Enable the replacment. Chosse: True or False
settings.smoothn=True #Enables smoothing of the displacemenet field
settings.smoothn_p=0.5 # This is a smoothing parameter
# select a method to replace the outliers: 'localmean', 'disk', 'distance'
settings.filter_method = 'localmean'
# maximum iterations performed to replace the outliers
settings.max_filter_iteration = 4
settings.filter_kernel_size = 2  # kernel size for the localmean method

### Plot Options ### 
# Select if you want to save the plotted vectorfield: True or False
settings.save_plot = False

# Choose wether you want to see the vectorfield or not :True or False
settings.show_all_plots = False
settings.show_plot = False
settings.scale_plot = 100 # select a value to scale the quiver plot of the vectorfield
# run the script with the given settings
settings.counter = 1
settings.invert = False

settings.fmt = '%.4e'


#Main function, runs piv with given settings 
def main(): 
    piv(settings)

if __name__=='__main__':
    main()
