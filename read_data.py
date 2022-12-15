import h5py

def readH5(path):
    '''
    Given the path to an .h5 file, reads it and returns two volumes: the fixed volume and the volume to align.

    Parameters
     ----------

    path (string): the path to the stored .h5 file. 

        
    Output
    ----------
        
    fixed_vol (np.array): the fixed, or reference volume.
    vol_to_align (np.array): the volume to align to the reference volume. 
    '''
    
    hf = h5py.File(path, 'r')
    fixed_vol = hf.get('fixed')
    vol_to_align = hf.get('move')

    return fixed_vol, vol_to_align
