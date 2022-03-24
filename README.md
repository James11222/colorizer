# Colorizer.py

A python script to stack BVRI image data into a colorized image. This is adapted from code originally written by Yukei Murakami's Repo [fits_quickRGB](https://github.com/SterlingYM/fits_quickRGB). This code is just a semi-automated script version of that code. 

## Basic Usage:

Start by placing your `.fits` files in the same directory as this script. You should have 1 B filter image, 1 V filter image, and 1 R filter image in the same directory formatted such that the directory looks something like:

```
n220323.d138.2022crv.R.fit
n220323.d137.2022crv.V.fit
n220323.d136.2022crv.B.fit
```
The I filter is not needed for this script. We also note that the naming format should be `*.obj_name.filter.fit` Once the data is properly loaded into the same directory as the script. Just run the following on the command line:

`python3 colorizer.py -obj_name 2022crv`

Note the name given must match the name in the files. 

By default the code performs saturation clipping, to avoid this add a command line argument `-no_sat_clip` and set it to `True`. You can also adjust the noise level threshold and the background level threshold by adding command line arguments `-noise_level` and `-bg_level` which can be floats from 0.0 to 1.0. An example of this is

 `python3 colorizer.py -obj_name 2022crv -noise_level 0.3 -bg_level 0.8 -no_sat_clip True`

An image should appear on your screen somewhere. Press the save button and save the figure to your preferred file name. By default the code also saves the image data in the form of a numpy array with the name `obj_name_img_array.npy` which can be loaded in with a simple `np.load()` call and plotted using `plt.imshow()`. This can be used for more sophisticated plotting and markups. Below are is an example of what the initial input starts as and what the final result is. 

The sample data is provided by the Filippenko Group at UC Berkeley originally taken by myself and Kingsley Ehrich on the Nickel 1m Telescope at Lick Observatory. 

![Images_Slices](https://github.com/James11222/colorizer/blob/main/Images/img_slices.png?raw=true)

<p align="center">
<img src="https://github.com/James11222/colorizer/blob/main/Images/2022crv.png?raw=true" alt="Image Stacked" width="50%"/>
</p>





