import utils
import build

import h5py
import numpy as np
import matplotlib.pyplot as plt

def readH5(path):
    '''
    Given the path to an .h5 file, reads it and returns two volumes: the fixed volume and the volume to align.

    Parameters
     ----------

    path : the path to the stored .h5 file. 

        
    Output
    ----------
        
    fixed_vol : the fixed, or reference volume. Returned as an array.
    vol_to_align : the volume to align to the reference volume. Returned as an array.

    '''
    
    hf = h5py.File(path, 'r')
    fixed_vol = hf.get('fixed')
    vol_to_align = hf.get('move')

    return fixed_vol, vol_to_align

    
def align(fixed_vol, vol_to_align):

    '''
    Runs a basic intensity-based SimpleITK alignment. 

    Parameters
    ----------

    fixed_volume : the reference volume. Expected as an array. 
    vol_to_align : the volume to align. Expected as an array. 

        
    Output
    ----------
    aligned_vol: the aligned version of vol_to_align. Returned as an array. 
    deformation_map: the dense deformation map. Returned as an array. 

    '''

    cfg = utils.load_cfg()
    align = build.alignBuild(cfg)
    align.buildSitkTile()

    try:
        tform = align.computeTransformMap(fixed_vol, vol_to_align)                
        result, deformation = align.warpVolume(vol_to_align, tform)
     
        return result, deformation
                
    except:
        print('Alignment failed')
        return

    
def checkAlignment(fixed_vol, aligned_vol, ROI_min=[0,0,0], ROI_max=[100,2048,2048]):
    '''
    Plots the fixed volume and aligned volume against eachother. 

    Parameters
    ----------

    fixed_volume : the fixed volume.
    aligned_volume : the transformed volume (i.e. the output of the applying the found transformation).
    ROI_min (optional) : minimum pixels for the region of interest.
    ROI_max (optional) : maximum pixels for the region of interest.
    '''
    
    z_inds = np.arange(0, min(fixed_vol.shape[0], aligned_vol.shape[0]), 20)
    fig, ax = plt.subplots(len(z_inds), 4, figsize = (20, 5*len(z_inds)))


    for row, z in enumerate(z_inds):
        ax[row,0].imshow(fixed_vol[z,:,:])
        ax[row,0].set_title('Fixed, z = {}'.format(z))
        ax[row,1].imshow(aligned_vol[z,:,:])
        ax[row,1].set_title('Aligned, z = {}'.format(z))

        ax[row,2].imshow(fixed_vol[z,ROI_min[1]:ROI_max[1],ROI_min[2]:ROI_max[2]])
        ax[row,2].set_title('Fixed (zoomed), z = {}'.format(z))
        ax[row,3].imshow(aligned_vol[z,ROI_min[1]:ROI_max[1],ROI_min[2]:ROI_max[2]])
        ax[row,3].set_title('Aligned (zoomed), z = {}'.format(z))
                
    plt.show()
        