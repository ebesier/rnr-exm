import torch
import torchfields
import numpy as np
import matplotlib.pyplot as plt
import torch.nn.functional as F
import torch
from torchvision.io import read_image
from scipy.spatial.transform import Rotation as R
from scipy.ndimage import gaussian_filter
import multiprocessing as mp
import argparse
import h5py
import functools

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


def apply_gaussian_filter(sigma, volume):
  # Apply the gaussian filter to a slice of the volume
  return gaussian_filter(volume, sigma, mode='reflect', cval=0)


def non_rigid_deformation(input_path,num_of_parallel_porcesses, num_local_deformations, noise_level, gaussian_sigma):

  fixed_vol, vol_to_align = readH5(input_path)

  input = fixed_vol
  input = np.asarray(input,dtype = 'float')
  input = torch.tensor(input)

  # Adjust dimension for torch convention
  input = input.unsqueeze(dim=0)
  input = input.unsqueeze(dim=0)
  N, C, Z_in, H_in, W_in = input.shape 
  print('input shape', input.shape)

  # ----- Basic Grid ---------------
  Z_out, H_out, W_out = Z_in, H_in, W_in # Adjust output size here
  zs = torch.linspace(-1,1,Z_out).double()
  xs = torch.linspace(-1,1,H_out).double()
  ys = torch.linspace(-1,1,W_out).double()
  z, x, y = torch.meshgrid(zs, xs, ys, indexing = 'ij')
  grid_basic = torch.stack((y,x,z),dim=-1)

  N = num_local_deformations
    
  # + 120 and - 120 ensures anchor points are not on border
  anchor_points = np.stack((np.random.randint(0, high=Z_in, size=N),np.random.randint(0 + 120, high= H_in - 120, size=N),np.random.randint(0 + 120, high= W_in - 120, size=N),np.random.randint(50, high=100, size=N)), axis = 1)

  noise = np.zeros_like(grid_basic)
  for z,x,y,intensity in anchor_points:
      noise[z,x,y] = intensity

  # Create a Pool with N worker processes
  with mp.Pool(num_of_parallel_porcesses) as p:
    # Split the 3D volume into chunks along the first axis (axis 0)
    chunks = np.array_split(noise, num_of_parallel_porcesses, axis=0)
    # Apply the gaussian filter to each chunks in parallel
    filtered_chunks = p.map(functools.partial(apply_gaussian_filter,gaussian_sigma), chunks)

  # Merge the filtered chunks back into a single 3D volume
  noise = np.concatenate(filtered_chunks, axis=0)
  noise = torch.tensor(noise)

  weight = noise_level
  weighted_noise = torch.mul(noise, weight)

  grid = torch.add(grid_basic, weighted_noise) # Vary this number to get different degree of noise
  grid = torch.unsqueeze(grid,dim = 0)

  # ---- Apply the transformation -------------
  output= F.grid_sample(input, grid, align_corners=True)
  print('output shape', output.shape)
    
  return weighted_noise, output
