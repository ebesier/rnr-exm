import numpy as np
import scipy.ndimage
from evalutils.exceptions import ValidationError
from scipy.ndimage import map_coordinates
from metrics import *

##### metrics #####
def jacobian_determinant(disp):
    _, _, H, W, D = disp.shape
    
    gradx  = np.array([-0.5, 0, 0.5]).reshape(1, 3, 1, 1)
    grady  = np.array([-0.5, 0, 0.5]).reshape(1, 1, 3, 1)
    gradz  = np.array([-0.5, 0, 0.5]).reshape(1, 1, 1, 3)

    gradx_disp = np.stack([scipy.ndimage.correlate(disp[:, 0, :, :, :], gradx, mode='constant', cval=0.0),
                           scipy.ndimage.correlate(disp[:, 1, :, :, :], gradx, mode='constant', cval=0.0),
                           scipy.ndimage.correlate(disp[:, 2, :, :, :], gradx, mode='constant', cval=0.0)], axis=1)
    
    grady_disp = np.stack([scipy.ndimage.correlate(disp[:, 0, :, :, :], grady, mode='constant', cval=0.0),
                           scipy.ndimage.correlate(disp[:, 1, :, :, :], grady, mode='constant', cval=0.0),
                           scipy.ndimage.correlate(disp[:, 2, :, :, :], grady, mode='constant', cval=0.0)], axis=1)
    
    gradz_disp = np.stack([scipy.ndimage.correlate(disp[:, 0, :, :, :], gradz, mode='constant', cval=0.0),
                           scipy.ndimage.correlate(disp[:, 1, :, :, :], gradz, mode='constant', cval=0.0),
                           scipy.ndimage.correlate(disp[:, 2, :, :, :], gradz, mode='constant', cval=0.0)], axis=1)

    grad_disp = np.concatenate([gradx_disp, grady_disp, gradz_disp], 0)

    jacobian = grad_disp + np.eye(3, 3).reshape(3, 3, 1, 1, 1)
    jacobian = jacobian[:, :, 2:-2, 2:-2, 2:-2]
    jacdet = jacobian[0, 0, :, :, :] * (jacobian[1, 1, :, :, :] * jacobian[2, 2, :, :, :] - jacobian[1, 2, :, :, :] * jacobian[2, 1, :, :, :]) -\
             jacobian[1, 0, :, :, :] * (jacobian[0, 1, :, :, :] * jacobian[2, 2, :, :, :] - jacobian[0, 2, :, :, :] * jacobian[2, 1, :, :, :]) +\
             jacobian[2, 0, :, :, :] * (jacobian[0, 1, :, :, :] * jacobian[1, 2, :, :, :] - jacobian[0, 2, :, :, :] * jacobian[1, 1, :, :, :])
        
    return jacdet


def compute_dice(fixed,moving,moving_warped,labels):
    dice_avg = 0
    count = 0
    dice_label = []
    for i in labels:
        if ((fixed==i).sum()==0) or ((moving==i).sum()==0):
            continue
        dice = compute_dice_coefficient((fixed==i), (moving_warped==i))
        dice_label.append(dice)
        dice_avg += dice
        count += 1     
    dice_avg /= count
    dice_label = np.array(dice_label)
    return dice_avg,dice_label
    
def compute_hd95(fixed,moving,moving_warped,labels):
    hd95_avg = 0
    count = 0
    hd95_label = []
    for i in labels:
        if ((fixed==i).sum()==0) or ((moving==i).sum()==0):
            continue
        hd95 = compute_robust_hausdorff(compute_surface_distances((fixed==i), (moving_warped==i), np.ones(3)), 95.)
        
        # handler for missing labels in the moving_wrapped
        if hd95 == float('inf'):
            z,y,x = fixed.shape 
            hd95=(z**2+y**2+x**2)**0.5
        
        hd95_label.append(hd95)
        hd95_avg += hd95
        count += 1
    hd95_avg /= count
    hd95_label = np.array(hd95_label)
    return hd95_avg, hd95_label

##### validation errors #####
def raise_missing_file_error(fname):
    message = (
        f"The displacement field {fname} is missing. "
        f"Please provide all required displacement fields."
    )
    raise ValidationError(message)
    
def raise_dtype_error(fname, dtype):
    message = (
        f"The displacement field {fname} has a wrong dtype ('{dtype}'). "
        f"All displacement fields should have dtype 'float16'."
    )
    raise ValidationError(message)
    
def raise_shape_error(fname, shape, expected_shape):
    message = (
        f"The displacement field {fname} has a wrong shape ('{shape[0]}x{shape[1]}x{shape[2]}x{shape[3]}'). "
        f"The expected shape of displacement fields for this task is {expected_shape[0]}x{expected_shape[1]}x{expected_shape[2]}x{expected_shape[3]}."
    )
    raise ValidationError(message)

