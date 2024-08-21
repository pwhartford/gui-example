#%% Settings/Imports
import matplotlib.pyplot as plt 
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.cm as cm 
import numpy as np 
from pathlib import Path 
import scipy as sp 
plt.rcParams['text.usetex'] = True


#Folder Settings 
# MAIN_DIR = Path('/media/peter/share/Documents/GitHub/VKI/homework/NSIP1/PIV_Data/Results_PIV_5ms_step/Open_PIV_results_32_Test_RAW/')
# DATA_DIR_1 = MAIN_DIR / '10.29.2023/step/low_velocity/200mus/cut/filtered/results_piv/Open_PIV_results_32_Test_RAW'
# DATA_DIR_2 = MAIN_DIR / '10.29.2023/step/low_velocity/200mus/cut/filtered/results_piv/Open_PIV_results_32_Test_RAW'
# MAIN_DIR = Path('/media/peter/share/Documents/Data/PIV Data/mehmet/POD_Output/results_piv/Open_PIV_results_32_Test_RAW')
MAIN_DIR = Path('/media/peter/share/Documents/Data/PIV Data/mehmet/POD_Output/results_piv/OpenPIV_results_32_Test_RAW')
# TITLE_1 = '$3\;m/s$'
# TITLE_2 = '$6\;m/s$'

FILETYPE = '.txt'

DATA_DIR_1 = MAIN_DIR 


#DATA Settingsx``
NUM_FRAMES = 100
SEPARATION_TIME_1 = 200e-6
SEPARATION_TIME_2 = 200e-6

FIGURE_NAMES = 'step_3_6_comparison'


#Plot settings 
SAVE_PLOTS = False
SAVE_DIR = DATA_DIR_1.parent
COLORMAP = plt.get_cmap('Dark2',8)

CONTOUR_COLORMAP = plt.get_cmap('magma')
LEVELS = 10


#% Load Data - Returns Relevant Arrays 
def load_data(data_dir, sep_time): 
    #Get File List
    files = [f for f in data_dir.glob('*%s'%FILETYPE)]

    #Load frame 1 data
    data_frame_1 = np.genfromtxt(files[0])


    nxny = data_frame_1.shape[0]  # is the to be doubled at the end we will have n_s=2 * n_x * n_y
    n_s = 2 * nxny

    ## Reconstruct Mesh from file
    X_S = data_frame_1[:, 0]
    Y_S = data_frame_1[:, 1]

    # Number of n_X/n_Y from forward differences
    GRAD_Y = np.diff(Y_S)
    IND_X = np.where(GRAD_Y != 0)
    DAT = IND_X[0]

    n_y = DAT[0] + 1

    # Reshaping the grid from the data
    n_x = (nxny // (n_y))  # Carefull with integer and float!

    #Reshape to mesh - and multiply by 1e3 for mm 
    Xg = (X_S.reshape((n_x, n_y)))*1e3
    Yg = (Y_S.reshape((n_x, n_y)))*1e3  # This is now the mesh

    #Initialize zero arrays for data
    vel_mag_data = np.zeros((Xg.shape[0], Xg.shape[1], NUM_FRAMES+1))
    vel_x_data = np.zeros((Xg.shape[0], Xg.shape[1], NUM_FRAMES+1))
    vel_y_data = np.zeros((Xg.shape[0], Xg.shape[1], NUM_FRAMES+1))
    s2n_data = np.zeros((Xg.shape[0], Xg.shape[1], NUM_FRAMES+1))

    #Load all velocities and put into arrays 
    i = 0
    for frame in files:
        #Get data from txt file 
        data = np.genfromtxt(frame)

        #Scale velocity by separation time 
        V_x = data[:,2] / sep_time
        V_y = data[:,3] / sep_time
        s2n = data[:,4]
        

        #Reshape Velocity into magnitude and individual components
        Mod = np.sqrt(V_x ** 2 + V_y ** 2)
        Vxg = (V_x.reshape((n_x, n_y)))
        Vyg = (V_y.reshape((n_x, n_y)))
        Magn = (Mod.reshape((n_x, n_y)))
        s2n = s2n.reshape((n_x, n_y))
        
        #Concatenate array into relevant data
        vel_mag_data[:,:, i] = Magn 
        vel_x_data[:,:, i] = Vxg 
        vel_y_data[:,:, i] = Vyg
        s2n_data[:,:, i] = s2n 

        i+=1

    return Xg, Yg, vel_mag_data, vel_x_data, vel_y_data, s2n_data


#Load data for both directories 
Xg1, Yg1, vel_mag_data_1, vel_x_data_1, vel_y_data_1, s2n_data_1 = load_data(DATA_DIR_1, SEPARATION_TIME_1)
# Xg2, Yg2, vel_mag_data_2, vel_x_data_2, vel_y_data_2, s2n_data_2 = load_data(DATA_DIR_2, SEPARATION_TIME_2)


def contour_figure(grid_1, grid_2, data_1, data_2, labels, colormap = CONTOUR_COLORMAP, levels = LEVELS):
    fig, [ax_1, ax_2] = plt.subplots(1, 2)
    fig.tight_layout(pad = 4)

    vmin = np.min([np.min(data_1), np.min(data_2)])
    vmax = np.max([np.max(data_1), np.max(data_2)])

    contour_1 = ax_1.contourf(grid_1[0], grid_1[1], data_1, levels, cmap = colormap, vmin = vmin, vmax = vmax)
    contour_2 = ax_2.contourf(grid_2[0], grid_2[1], data_2, levels, cmap = colormap, vmin = vmin, vmax = vmax)

    divider = make_axes_locatable(ax_2)
    cax = divider.append_axes('right', size='5%', pad=0.1)

    ax_1.set_aspect('equal')
    ax_2.set_aspect('equal')

    ax_1.set_xlabel(labels[0])
    ax_1.set_ylabel(labels[1])

    ax_2.set_xlabel(labels[0])
    ax_2.set_ylabel(labels[1])

    colorbar = fig.colorbar(contour_2, cax = cax)
    colorbar.set_label(labels[2])

    ax_1.set_title(TITLE_1)
    ax_2.set_title(TITLE_2)

    return fig, ax_1, ax_2


#% Compute and Plot Mean Flow 
mean_vel_mag_1 = np.mean(vel_mag_data_1, 2)
# mean_vel_mag_2 = np.mean(vel_mag_data_2, 2)

Uinfty_1 = np.max(mean_vel_mag_1)
# Uinfty_2 = np.max(mean_vel_mag_2)

normalized_mean_vel_mag_1 = mean_vel_mag_1/(Uinfty_1)
# normalized_mean_vel_mag_2 = mean_vel_mag_2/(Uinfty_2)

print('Maximum Velocity 1: %0.3f'%Uinfty_1)
# print('Maximum Velocity 2 %0.3f'%Uinfty_2)

mean_vel_labels =  ['X Position $[mm]$', 'Y Position $[mm]$', 'Instantaneous Velocity $[U/U_\infty]$']

mean_vel_labels =  ['X Position $[mm]$', 'Y Position $[mm]$', 'Normalized Mean Velocity $[U/U_\infty]$']
# mean_vel_figure, mean_vel_ax1, mean_vel_ax2 = contour_figure([Xg1, Yg1], [Xg2, Yg2], normalized_mean_vel_mag_1, normalized_mean_vel_mag_2,mean_vel_labels)

# mean_vel_figure, mean_vel_ax1, mean_vel_ax2 = contour_figure([Xg1, Yg1], [Xg2, Yg2], vel_mag_data_1[:,:,0]/Uinfty_1, vel_mag_data_1[:,:,1]/Uinfty_1,mean_vel_labels)
fig, ax_1 = plt.subplots()
fig.tight_layout(pad = 4)

vmin = np.min(mean_vel_mag_1)
vmax = np.max(mean_vel_mag_1)

contour_1 = ax_1.contourf(Xg1, Yg1, mean_vel_mag_1, 50, cmap = 'viridis', vmin = vmin, vmax = vmax)
# contour_2 = ax_2.contourf(grid_2[0], grid_2[1], data_2, levels, cmap = colormap, vmin = vmin, vmax = vmax)

# cbar = fig.colorbar(contour_1)

sample = 1

# ax_1.quiver(Xg1[0:Xg1.shape[0]:sample, 0:Xg1.shape[1]:sample], Yg1[0:Xg1.shape[0]:sample, 0:Xg1.shape[1]:sample], vel_x_data_1[1:Xg1.shape[0]:sample, 1:Xg1.shape[1]:sample,1], vel_y_data_1[0:Xg1.shape[0]:sample, 0:Xg1.shape[1]:sample,1], scale = 200, color = COLORMAP(0))
# mean_vel_ax2.quiver(Xg2[0:Xg2.shape[0]:sample, 0:Xg2.shape[1]:sample], Yg2[0:Xg2.shape[0]:sample, 0:Xg2.shape[1]:sample], vel_x_data_2[1:Xg2.shape[0]:sample, 1:Xg2.shape[1]:sample,1], vel_y_data_2[0:Xg2.shape[0]:sample, 0:Xg2.shape[1]:sample,1], scale = 200, color = COLORMAP(0))

if SAVE_PLOTS:
    mean_vel_figure.savefig(str(MAIN_DIR / 'results') + '/'  + FIGURE_NAMES + '_mean_velocity.jpg', dpi = 500, format = 'jpg')

#%% Compute Turbulence Intensity 
# TI_1 = np.std(vel_mag_data_1, 2)/Uinfty_1*100
# TI_2 = np.std(vel_mag_data_2, 2)/Uinfty_2*100


ti_labels =  ['X Position $[mm]$', 'Y Position $[mm]$', 'Turbulence Intensity $[\%]$']
ti_figure, ti_ax1, ti_ax2 = contour_figure([Xg1, Yg1], [Xg2, Yg2], TI_1, TI_2, ti_labels)


if SAVE_PLOTS:
    ti_figure.savefig(str(MAIN_DIR / 'results') + '/'  + FIGURE_NAMES + '_turbulence_intensity.jpg', dpi = 500, format = 'jpg')


#% Compute Signal to Noise Ratio 
s2n_1 = np.mean(s2n_data_1, 2)
s2n_2 = np.mean(s2n_data_2, 2)

s2n_labels =  ['X Position $[mm]$', 'Y Position $[mm]$', 'Signal to Noise Ratio']
s2n_figure, s2n_ax1, s2n_ax2 = contour_figure([Xg1, Yg1], [Xg2, Yg2], s2n_1, s2n_2, s2n_labels, cm.get_cmap('Greys'), 100)



if SAVE_PLOTS:
    s2n_figure.savefig(str(MAIN_DIR / 'results') + '/'  + FIGURE_NAMES + '_s2n_ratio.jpg', dpi = 500, format = 'jpg')

#%%Velocity Profile Plotting
#Extract three velocity profiles. Plot them in self similar forms

# First we select some profiles based on the X=10,20,30 mm
X_locs = np.array([10, 50, 100])

# Find the corresponding indices: first we take the X axis.
x_indices_1 = []
x_indices_2 = []
# We identify the indices in the mesh where x is the closest to the desired value
# We will store the profiles in a matrix

for k in range(len(X_locs)):
    x_indices_1.append(np.where((Xg1[0,:]<X_locs[k]+1) & (Xg1[0,:]>X_locs[k]-1))[0][0])
    x_indices_2.append(np.where((Xg2[0,:]<X_locs[k]+1) & (Xg2[0,:]>X_locs[k]-1))[0][0])


#Calculate flat plate Re 
L_plate = 610 #mm 
nu_air = 1.48e-5 #m^2/s

Re_plate_1 = (X_locs+600)/1e3*Uinfty_1/nu_air
Re_plate_2 = (X_locs+600)/1e3*Uinfty_2/nu_air



#Calculate mean U 
U_mean_1 = np.mean(vel_x_data_1[:,x_indices_1], 2)
U_mean_2 = np.mean(vel_x_data_2[:,x_indices_2], 2)

yhat_indices_1 = []
yhat_indices_2 = []

for i in range(U_mean_1.shape[1]):
    if np.where(U_mean_1[:,i]>0.99*Uinfty_1)[0].shape[0] == 0: 
        yhat_indices_1.append(0)
    else:
        yhat_indices_1.append(np.max(np.where(U_mean_1[:,i]>0.99*Uinfty_1)))

for i in range(U_mean_2.shape[1]):
    if np.where(U_mean_2[:,i]>0.99*Uinfty_2)[0].shape[0] == 0: 
        yhat_indices_2.append(0)
    else:
        yhat_indices_2.append(np.max(np.where(U_mean_2[:,i]>0.99*Uinfty_2)))

delta_1 = Yg1[yhat_indices_1,x_indices_1]
delta_2 = Yg1[yhat_indices_2,x_indices_2]

yhat_1 = Yg1[:,x_indices_1]/delta_1
yhat_2 = Yg2[:,x_indices_2]/delta_2

blasius_1 = (X_locs+600)*0.375*Re_plate_1**(-1/5)/delta_1
blasius_2 = (X_locs+600)*0.375*Re_plate_2**(-1/5)/delta_2

bl_figure, [bl_ax_1, bl_ax_2] = plt.subplots(1,2)

bl_ax_1.set_prop_cycle(marker=['X', '*', '.'])
bl_ax_2.set_prop_cycle(marker=['X', '*', '.'])

linestyles = ['dashed', 'dotted', 'dashdot']
for i in range(len(x_indices_1)):
    # bl_ax_1.plot([np.min(U_mean_1)/Uinfty_1, np.max(U_mean_1)/Uinfty_1], np.ones(2)*blasius_1[i], color = COLORMAP(i), linestyle = 'dashed', marker = 'none')
    bl_ax_1.plot(U_mean_1[:,i]/Uinfty_1, yhat_1[:,i], color = COLORMAP(i), linestyle = 'none', markersize = 3)

for i in range(len(x_indices_2)):
    # bl_ax_2.plot([np.min(U_mean_2)/Uinfty_2, np.max(U_mean_2)/Uinfty_2], np.ones(2)*blasius_2[i], color = COLORMAP(i), linestyle = 'dashed', marker = 'none')
    bl_ax_2.plot(U_mean_2[:,i]/Uinfty_2, yhat_2[:,i], color = COLORMAP(i), linestyle = 'none', markersize = 3)

bl_ax_1.set_xlabel('Normalized Velocity $[u/U_\infty]$')
bl_ax_2.set_xlabel('Normalized Velocity $[u/U_\infty]$')

bl_ax_1.set_ylabel('Normalized Y Position $[Y/\delta]$')
bl_ax_2.set_ylabel('Normalized Y Position $[Y/\delta]$')

bl_ax_1.set_title(TITLE_1)
bl_ax_2.set_title(TITLE_2)

legend_list = []
for x in X_locs:
    # legend_list.append('Blasius: $%i\;[mm]$'%x)
    legend_list.append('Profile: $%i \;[mm]$'%x)

bl_ax_1.legend(legend_list)
bl_ax_2.legend(legend_list)



bl_figure.tight_layout(pad=2)
# bl_ax_1.set_aspect('equal')
# bl_ax_2.set_aspect('equal')

if SAVE_PLOTS:
    bl_figure.savefig(str(MAIN_DIR / 'results') + '/'  + FIGURE_NAMES + '_bl_profile.jpg', dpi = 500, format = 'jpg')

#%%
for i in range(U_mean_1.shape[1]):
    delta_star = np.trapz(Yg1[:,i],1-U_mean_1[:,i]/Uinfty_1)
    theta = np.trapz(Yg1[:,i],U_mean_1[:,i]/Uinfty_1*(1-U_mean_1[:,i]/Uinfty_1))
    H = delta_star/theta
    print('Delta Star: %s'%np.trapz(Yg1[:,i],1-U_mean_1[:,i]/Uinfty_1))
    print('Theta: %s'%np.trapz(Yg1[:,i],U_mean_1[:,i]/Uinfty_1*(1-U_mean_1[:,i]/Uinfty_1)))
    print('H: %s'%H)