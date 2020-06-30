'''
npstructs.py
A collection of tools for analyzing laser induced assemblies (structures) of silver nanoparticles
All rights reserved (c) 2020 Yong Wang
'''

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pims
import skimage, skimage.io, skimage.morphology
import skimage.filters, skimage.feature
import skimage.measure
from scipy import ndimage as ndi
from skimage.segmentation import watershed
import pandas as pd
import multiprocessing as mps



def comp2img(img1, img2, cmap1='gray', cmap2='gray', vminmax1=None, vminmax2=None):
    ''' compare 2 images side by side
    '''
    plt.figure(figsize=(8,4))
    plt.subplot(121)
    if vminmax1 is None:
        plt.imshow(img1, cmap=cmap1)
    else:
        plt.imshow(img1, cmap=cmap1, vmin=vminmax1[0], vmax=vminmax1[1])
    plt.subplot(122)
    if vminmax2 is None:
        plt.imshow(img2, cmap=cmap2)
    else:
        plt.imshow(img2, cmap=cmap2, vmin=vminmax2[0], vmax=vminmax2[1])

def background_subtraction(image, ball_size=9):
    ''' rolling-ball background subtraction
    PARAMETERS
        image:      (array) input image 
        ball_size:  (int) ball size (in unit of pixels)
    RETURNS
        image_rmbg: (array) output image with background removed
    '''
    image_rmbg = skimage.morphology.white_tophat(image, selem=skimage.morphology.disk(ball_size))
    return image_rmbg

def smooth_image(image, sigma=1, times=1):
    ''' smooth image by x times (using gaussian filter)
    PARAMETERS
        image:  (array) input image
        sigma:  (int/float) size of the gaussian filter
        times:  (int) number of times for smoothing
    RETURNS
        image_sm: (array) output image after smoothing
    '''
    image_sm = image.copy()
    for i in range(times):
        image_sm = skimage.filters.gaussian(image_sm,sigma=sigma)
    return image_sm

def scale_image_intensity(image, scfactor=1.0):
    ''' scale the intensity of an image
    '''
    return image*scfactor

def bwimage_by_threshold(image, threshold=180):
    ''' create a black/white image by applying a threshold
    '''
    return (image>=threshold)*1.0

def preprocess_image(image, ball_size=9, sigma=1, times=2, scfactor=1e5,
                    threshold=180, output_detail=False):
    ''' preprocess an image and generate a black/white image of structures, which will be used for finding structures in `find_structs(...)`
    Steps of the preprocess include:
        1) background subtraction by rolling-ball algorithm
        2) image smoothing using Gaussian filters (single time, or multiple times)
        3) background subtraction by rolling-ball algorithm once again
        4) scaling intensity
        5) applying threshold to generate the black/white image
    PARAMETERS
        image:      (array) image (a single frame of a movie)
        ball_size:  (int) ball size for the background subtraction using the rolling-ball algorithm
        sigma:      (int/float) sigma for the gaussian filters for smoothing
        times:      (int) number of times for applying the gaussian filters for smoothing
        scfactor:   (float) scaling factor for intensity scaling
        threshold:  (float) threshold for generating the black/white image
        output_detail:  (bool) indicate whether to return details
    RETURNS
        if output_detail is False:
          bwimage:  (numpy.array) black/white image
        if output_detail is True:
          detailed_output: (bwimage, image_rmbg, image_sm, image_sm_rmbg, image_sm_rmbg_sc)

    '''
    image_rmbg = background_subtraction(image, ball_size)
    image_sm = smooth_image(image_rmbg, sigma, times)
    image_sm_rmbg = background_subtraction(image_sm, ball_size)
    image_sm_rmbg_sc = scale_image_intensity(image_sm_rmbg, scfactor)
    bwimage = bwimage_by_threshold(image_sm_rmbg_sc, threshold)
    if output_detail:
        return (bwimage, image_rmbg, image_sm, image_sm_rmbg, image_sm_rmbg_sc)
    else:
        return bwimage



def find_structs(bwimage, dilation_size=3, erosion_size=4, min_struct_size=32, output_detail=False):
    ''' find structures from a black-white image
    PARAMETERS
        bwimage:        (array) black/white image from which the structures will be found
        dilation_size:  (int) pixel number for dilation when trying to fill gaps in edges
        erosion_size:   (int) pixel number for erosion when trying to shrink the filled objects
        min_struct_size:(int) minimum size of structures in order to be considered
        output_detail:  (bool) indicate whether to return details
    RETURNS
        if output_detail is False:
          struct_labels:  (numpy.array) labels of structures, same size of the image
        if output_detail is True:
          detailed_output: tuple of (struct_labels, edges, dilated, smallobjremoved, filled, erosed, smallobjremoved2, markers)
    '''
    # find raw edges
    edges = skimage.filters.sobel(bwimage) > 0
    # dilate edges to fill possible gaps
    dilated = skimage.morphology.dilation(edges, skimage.morphology.square(dilation_size))
    # remove small objects of dilated edges
    smallobjremoved = skimage.morphology.remove_small_objects(dilated.astype(bool), min_size=min_struct_size)
    # fill the edges
    filled = 1 - skimage.morphology.flood(smallobjremoved.astype('uint16'), (0,0))
    # erose the filled structs
    erosed = skimage.morphology.erosion(filled, skimage.morphology.square(erosion_size))
    # remove small objects of erosed structs
    smallobjremoved2 = skimage.morphology.remove_small_objects(erosed.astype(bool), min_size=min_struct_size)
    # label the structs
    markers = ndi.label(smallobjremoved2)[0]
    struct_labels = watershed(np.zeros_like(smallobjremoved2), markers, mask=smallobjremoved2)
    # return 
    if output_detail:
        return (struct_labels, edges, dilated, smallobjremoved, filled, erosed, smallobjremoved2, markers)
    else:
        return struct_labels

def annotate_structs(image, struct_labels, fig=None, vmin=None, vmax=None, add_text=False):
    ''' annotate the structures of silver nanoparticles on top of the image
    PARAMETERS
        image:          (array) image from which the structures are found
        struct_labels:  (numpy.array) labels of structures, same size of the image, obtained from `find_structs(...)`
        fig:            (int) figure id on which the figure is shown
        vmin/vmax:      (float) intensity parameters for showing the image. See `matplotplib.pyplot.imshow`
        add_text:       (bool) add text (structure id) to the annotated figure if add_text is True
    RETURNS
        fig:            (int) figure id on which the figure is shown, could be useful if one wants to modify the figure
    '''
    if fig is None:
        fig = plt.figure(figsize=(6,6))
    else:
        fig = plt.figure(fig)
    plt.imshow(image, cmap='gray', vmin=vmin, vmax=vmax)
    contours = skimage.measure.find_contours(struct_labels, 0)
    for n, contour in enumerate(contours):
        p = plt.plot(contour[:,1], contour[:,0])
        c = np.array(mpl.colors.to_rgb(p[0].get_color()))
        if add_text is True:
            plt.text(np.mean(contour[:,1]), np.mean(contour[:,0]), '%d'%n,
                     horizontalalignment='center', verticalalignment='center',
                     fontsize=9, color=[1-c[0], 1-c[1], c[2]])
    return fig

def get_struct_sizes(struct_labels):
    ''' get the sizes of the structures of silver nanoparticles
    PARAMETERS
        struct_labels:  (numpy.array) labels of structures, same size of the image, obtained from `find_structs(...)`
    RETURNS
        sizes:          (numpy.array:int) sizes of the structures
    '''
    n_structs = np.max(struct_labels)
    if n_structs == 0:
        return [0]
    sizes = []
    for i in range(1, n_structs):
        sizes.append(np.sum(struct_labels==i))
    return sizes

def get_struct_cms(struct_labels, to_plot=False):
    ''' get the center-of-masses of the structures of silver nanoparticles
    PARAMETERS
        struct_labels:  (numpy.array) labels of structures, same size of the image, obtained from `find_structs(...)`
        to_plot:        (bool) plot the center-of-masses if to_plot is True
    RETURNS
        cms:            (numpy.array) position [x,y] of the center-of-masses
    '''
    contours = skimage.measure.find_contours(struct_labels, 0)
    cms = []
    if to_plot is True:
        plt.figure(figsize=(6,6))
    for n, contour in enumerate(contours):
        cms.append([np.mean(contour[:,0]), np.mean(contour[:,1])])
        if to_plot is True:
            c = plt.plot(contour[:,0], contour[:,1], '-')
            plt.plot([np.mean(contour[:,0])], [np.mean(contour[:,1])],
                    'x', color=c[0].get_color())
    if to_plot is True:
        plt.gca().set_aspect(1)
    return np.array(cms)

def polyarea(x, y):
    ''' calculate the area of a polygon (specified by vertices x, y) using the Shoelace formula
    '''
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def locate(struct_labels, frame=0):
    ''' locate the positions structures and record the sizes, as well as which frame the structures are located
    PARAMETERS
        struct_labels:  (numpy.array) labels of structures, same size of the image, obtained from `find_structs(...)`
        frame:          (int) the corresponding frame of `struct_labels`
    RETURNS
        structs:        (pandas.DataFrame) position and size of the np-structures, with columns=['x','y','size','frame']
    '''
    contours = skimage.measure.find_contours(struct_labels, 0)
    res = []
    for contour in contours:
        res.append([np.mean(contour[:,0]), 
                    np.mean(contour[:,1]),
                    polyarea(contour[:,0], contour[:,1]),
                    frame])
    if len(res)>0:
        res = np.array(res)
        res = pd.DataFrame(res, columns=['x','y','size','frame'])
        res = res.astype({'frame':'int'})
        return res
    else:
        return pd.DataFrame()


def get_starting_frame(frames, threshold=500):
    ''' get the starting frame in the movie (frames) by applying a threshold to the max intensity of the frame
    PARAMETERS
        frames:     (array of frame) frames returned from `pims.open('...')`
        threshold:  (float) threshold on the max intensity for a frame to be treated when the shutter is open
    RETURNS
        starting_frame: (int) the starting frame when the shutter is open (not the first frame when np-structures are formed)
    '''
    for i in range(len(frames)-1):
        if np.max(frames[i]) < threshold and np.max(frames[i+1])>=threshold:
            return (i+1)

def locate_nps_single_image(
        raw_image, frame_id, ball_size=9, sigma=1,
        times=2, scfactor=1e5, threshold=180,
        dilation_size=1, erosion_size=5, min_struct_size=32):
    ''' wrapper for locating nps in a single image - needed for locate_nps_multiple_images
    '''
    bwimage = preprocess_image(raw_image, ball_size=ball_size, sigma=sigma,
                                times=times, scfactor=scfactor, threshold=threshold,
                                output_detail=False)
    struct_labels = find_structs(bwimage, dilation_size=dilation_size,
                                    erosion_size=erosion_size, min_struct_size=min_struct_size,
                                    output_detail=False)
    structs = locate(struct_labels, frame=frame_id)
    return (structs, struct_labels)

def locate_nps_multiple_images(
        images, ball_size=9, sigma=1,
        times=2, scfactor=1e5, threshold=180,
        dilation_size=1, erosion_size=5, min_struct_size=32):
    ''' locate nps in multiple images using multiprocessing
    '''
    args = [(img, f, ball_size, sigma, times, scfactor, threshold,dilation_size, erosion_size, min_struct_size) for f, img in enumerate(images)]
    pool = mps.Pool(mps.cpu_count())
    results = pool.starmap(locate_nps_single_image, args)
    pool.close()
    return results


