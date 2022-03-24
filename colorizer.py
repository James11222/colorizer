import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from astropy.io import fits
from scipy.ndimage import interpolation as interp
from skimage.registration import phase_cross_correlation
import glob

#---------------------------------------------

import argparse

parser = argparse.ArgumentParser(description='Color Image Script')

parser.add_argument('-obj_name', type=str, required=True,
                    help='Store the name of the object observed in string format.')

parser.add_argument('-no_sat_clip', type=bool,
                   help='Store the boolean flag for saturation clipping.')
                    
parser.add_argument('-noise_level', type=float,
                    help="""lower limit of single-color noise level. 
                    Lowering this will remove more noise but also possibly more actual data.""")

parser.add_argument('-bg_level', type=float, 
                    help="""upper limit of the background color
                    (e.g. red- and blue- color level when removing green-color noise)
                    Increasing this will remove more noise, but possibly more actual data.""")

parser.add_argument('-sat_factor', type=int,
                    help="""This number can range from 1 to 10, 10 being the most 
                    saturated/exposed and 1 being the least. the default is 5.""")
                    

results = parser.parse_args()

print('Object Name = {0}'.format(results.obj_name))

if results.no_sat_clip:
    print('No Saturation Clipping = {0}'.format(results.no_sat_clip))
else:
    results.no_sat_clip=False
    
if results.noise_level:
    print('Lower Limit for Noise = {0}'.format(results.noise_level))
else:
    results.noise_level=0.3
    
if results.bg_level:
    print('Upper Limit of Background Color = {0}'.format(results.bg_level))
else:
    results.bg_level=0.8
    
if results.sat_factor:
    print("Saturation Factor is {0}".format(results.sat_factor))
else:
    results.sat_factor=5


#-----------------------------------------------

def img_scale_log(inputArray, scale_min, scale_max, no_sat_clip=False):
    """
    Scale the image data to log scale and clean up data.
    """
    
    imageData=np.array(inputArray, copy=True)

    if not no_sat_clip:
        # saturation clipping: set sat_clip to False to turn off
        saturation_threshold = 60000 #anything brighter than this is considered as CR and is changed to 0
        indices0 = imageData >= saturation_threshold
        imageData[indices0] = 1e-10
    
    if scale_min == None:
        scale_min = imageData.min()
    if scale_max == None:
        scale_max = imageData.max()
        
    factor = np.log10(scale_max) - np.log10(scale_min)
    lower_lim = np.log10(scale_min)
    
    imageData = (np.log10(imageData)-lower_lim)/factor
    
    indices1 = imageData <= 1e-10 
    indices2 = imageData == -np.inf
    indices3 = imageData >= 1
    
    imageData[indices1] = 1e-10
    imageData[indices2] = 1e-10
    imageData[indices3] = 1

    return imageData


#import files from same directory
R_file = glob.glob("*" +results.obj_name + ".R.fit")[0]
G_file = glob.glob("*" +results.obj_name + ".V.fit")[0]
B_file = glob.glob("*" +results.obj_name + ".B.fit")[0]

print("Importing your RGB Color files. This should be the R, V, B filters on Nickel. \n")
print(f"R Color File: {R_file}")
print(f"G Color File: {G_file}")
print(f"B Color File: {B_file}")

Rdata = fits.getdata(R_file)
Gdata = fits.getdata(G_file)
Bdata = fits.getdata(B_file)

# correct pointing offset automatically (using Bdata as a reference)
shift, error, diffphase = phase_cross_correlation(Bdata.astype('int'), Rdata.astype('int'))
new_R = interp.shift(Rdata, shift)
shift, error, diffphase = phase_cross_correlation(Bdata.astype('int'), Gdata.astype('int'))
new_G = interp.shift(Gdata, shift)

R = new_R
G = new_G
B = Bdata


y,bins = np.histogram(Rdata.flatten(),bins=1000,range=(0,np.mean(Rdata.flatten())+1*np.std(Rdata.flatten())))
peakR = ((bins[1:]+bins[:-1])/2)[y==y.max()]


y,bins = np.histogram(Gdata.flatten(),bins=1000,range=(0,np.mean(Gdata.flatten())+1*np.std(Gdata.flatten())))
peakG = ((bins[1:]+bins[:-1])/2)[y==y.max()]


y,bins = np.histogram(Bdata.flatten(),bins=1000,range=(0,np.mean(Bdata.flatten())+1*np.std(Bdata.flatten())))
peakB = ((bins[1:]+bins[:-1])/2)[y==y.max()]



def Generate_Image(R,G,B, noise_level=0.8, bg_level=0.3, sat_factor=5):
    """
    A function to generate the image from the RGB data.
    
    ARGS:
    
    -noise_level: [float] lower limit of single-color noise level. Lowering this will remove more noise
                  but also possibly more actual data.
                  
    -bg_level: [float] upper limit of the background color
               (e.g. red- and blue- color level when removing green-color noise)
               Increasing this will remove more noise, but possibly more actual data.
    
    """
    
    # reference: Jessica Lu's blog post
    # https://www.astrobetter.com/blog/2010/10/22/making-rgb-images-from-fits-files-with-pythonmatplotlib/
    # scale_min: 'black' level. This is usually histogram peak + small offset.
    # scale_max: 'white' level. Lowering this will cause more saturation, but will make the image brighter.
    
    sat_coeff = ((10 - sat_factor) / 10) + 1.5
    
    
    img = np.zeros((R.shape[0], R.shape[1], 3), dtype=float)
    img[:,:,0] = img_scale_log(R, scale_min=peakR + 0.01 * peakR, scale_max=sat_coeff*peakR, no_sat_clip=results.no_sat_clip)
    img[:,:,1] = img_scale_log(G, scale_min=peakG + 0.01 * peakG, scale_max=sat_coeff*peakG, no_sat_clip=results.no_sat_clip)
    img[:,:,2] = img_scale_log(B, scale_min=peakB + 0.01 * peakB, scale_max=sat_coeff*peakB, no_sat_clip=results.no_sat_clip)


    # Color noise reduction
    # detect noise when single color value is too different from other two colors 
    indices_Rnoise = (img[:,:,0]>=noise_level) & ((img[:,:,1]<=bg_level) & (img[:,:,2]<=bg_level))
    indices_Gnoise = (img[:,:,1]>=noise_level) & ((img[:,:,0]<=bg_level) & (img[:,:,2]<=bg_level))
    indices_Bnoise = (img[:,:,2]>=noise_level) & ((img[:,:,1]<=bg_level) & (img[:,:,0]<=bg_level))

    img[indices_Rnoise] = 0
    img[indices_Gnoise] = 0
    img[indices_Bnoise] = 0
    
    #uncomment below for detailed RGB split view:
    
    # fig,((ax1,ax2,ax3),(ax4,ax5,ax6)) = plt.subplots(2,3,figsize=(18,12))
    # ax1.imshow(img[:,:,0],cmap='gray')
    # ax1.set_title('R')
    # ax2.imshow(img[:,:,1],cmap='gray')
    # ax2.set_title('G')
    # ax3.imshow(img[:,:,2],cmap='gray')
    # ax3.set_title('B')
    # # img[:,:,1] = rolled
    # ax4.hist(np.array(img[:,:,0]).flatten(),bins=300,color="red")
    # ax4.set_ylim(0,3000)
    # ax5.hist(np.array(img[:,:,1]).flatten(),bins=300,color="limegreen")
    # ax5.set_ylim(0,3000)
    # ax6.hist(np.array(img[:,:,2]).flatten(),bins=300,color="cyan")
    # ax6.set_ylim(0,3000)
    # plt.tight_layout()
    # plt.savefig("debug2.png")
    
    return img


def plot_img(img,obj_name):
    """
    A simple plotting function. For some reason plt.savefig doesn't properly plot the image,
    instead save the image when it appears on screen.
    """
    f, ax = plt.subplots(1,1,figsize=(8,8))
    ax.set_title(obj_name, fontsize=45)
    ax.imshow(img)
    ax.set_xticks([])
    ax.set_yticks([])
    f.tight_layout()
    # plt.show()
    plt.savefig(obj_name + '.png',dpi=300, bbox_inches="tight")
    
    
if __name__ == "__main__":
    full_img = Generate_Image(R,G,B, sat_factor=results.sat_factor)
    np.save(results.obj_name + "_img_array.npy", full_img) #save the data in an image array for further plotting!
    plot_img(full_img, results.obj_name)




