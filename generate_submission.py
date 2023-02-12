import numpy as np
import h5py

## Example of how to generate the .h5 files required for submission. 
## For each species, generrate the .h5 file, put it in a parent directory called "submission" and compress it. 
## Submit submission.zip to species-specific leaderboard.

################### Example Mouse Submission #######################

## Generate deformation map (replace)
deformation_pair1 = np.zeros((81,2048,2048,3))
deformation_pair2 = np.zeros((81,2048,2048,3))
deformation_pair3 = np.zeros((81,2048,2048,3)) 

## Cast to float32 to reduce file size
deformation_pair1 = np.float32(deformation_pair1) 
deformation_pair2 = np.float32(deformation_pair2)
deformation_pair3 = np.float32(deformation_pair3)

## Write to .h5
hf = h5py.File('mouse_test.h5', 'w')
hf.create_dataset('pair5', data=deformation_pair1, compression='gzip')
hf.create_dataset('pair6', data=deformation_pair2, compression='gzip')
hf.create_dataset('pair7', data=deformation_pair3, compression='gzip')
hf.close()

################### Example Zebrafish Submission #######################

## Generate deformation map (replace)
deformation_pair1 = np.zeros((133,2048,2048,3))
deformation_pair2 = np.zeros((133,2048,2048,3))
deformation_pair3 = np.zeros((133,2048,2048,3)) 

## Cast to float32 to reduce file size
deformation_pair1 = np.float32(deformation_pair1) 
deformation_pair2 = np.float32(deformation_pair2)
deformation_pair3 = np.float32(deformation_pair3)

## Write to .h5
hf = h5py.File('zebrafish_test.h5', 'w')
hf.create_dataset('pair5', data=deformation_pair1, compression='gzip')
hf.create_dataset('pair6', data=deformation_pair2, compression='gzip')
hf.create_dataset('pair7', data=deformation_pair3, compression='gzip')
hf.close()

################### Example C. elegans Submission #######################

## Generate deformation map (replace)
deformation_pair1 = np.zeros((559,2048,2048,3))
deformation_pair2 = np.zeros((559,2048,2048,3))
deformation_pair3 = np.zeros((559,2048,2048,3)) 

## Cast to float32 to reduce file size
deformation_pair1 = np.float32(deformation_pair1) 
deformation_pair2 = np.float32(deformation_pair2)
deformation_pair3 = np.float32(deformation_pair3)

## Write to .h5
hf = h5py.File('c_elegan_test.h5', 'w')
hf.create_dataset('pair5', data=deformation_pair1, compression='gzip')
hf.create_dataset('pair6', data=deformation_pair2, compression='gzip')
hf.create_dataset('pair7', data=deformation_pair3, compression='gzip')
hf.close()
