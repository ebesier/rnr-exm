import SimpleITK as sitk
import numpy as np
from yacs.config import CfgNode
import cv2 as cv
import os

class sitkTile:
    # 1. estimate transformation between input volumes
    # 2. warp one volume with the transformation
    def __init__(self, cfg: CfgNode):
        self.elastix = sitk.ElastixImageFilter()
        self.transformix = sitk.TransformixImageFilter()
        self.cfg = cfg
        self.resolution = None
        self.parameter_map = None
        self.transform_type = None
        self.num_iteration = None
    
    def setResolution(self, resolution= None):
        '''set resolution for sitk, always in x,y,z order
        '''
        # xyz-order
        if resolution is not None:
            self.resolution = resolution
        else: 
            self.resolution = self.cfg.ALIGN.RESOLUTION
    
    def updateParameterMap(self, parameter_map=None):
        ''' update param map if needed
        '''
        if parameter_map is not None:
            self.parameter_map = parameter_map
        self.elastix.SetParameterMap(self.parameter_map)

    def getParameterMap(self):
        ''' return param map currently being used
        '''
        return self.parameter_map

    def readTransformMap(self, filename):
        ''' read tform map from .txt file
        '''
        return sitk.ReadParameterFile(filename)

    def writeTransformMap(self, filename, transform_map):
        ''' write tform map to .txt file
        '''
        return sitk.WriteParameterFile(transform_map, filename)
    
    def convertSitkImage(self, vol_np, res_np = None):
        ''' convert numpy array to sitk vol
        '''

        vol = sitk.GetImageFromArray(vol_np)

        if res_np is not None:
            vol.SetSpacing(res_np)
        else:
            vol.SetSpacing(self.resolution)

        return vol
    
    
    def computeTransformMap(self, fix_dset, move_dset, 
                            res_fix=None, res_move=None, 
                            log = 'file', log_path = './sitk_log/'):
        
        ''' computes a transformaton matrix given two volumes and a set of masks
        returns a transformation matrix for the given volumes
        note that the log will be overwritten, see github for a solution with subprocesses:
        https://github.com/SuperElastix/SimpleElastix/issues/104
        '''
        
        if log == 'console':
            self.elastix.SetLogToConsole(True)
            self.elastix.SetLogToFile(False)
        elif log == 'file':
            self.elastix.SetLogToConsole(False)
            self.elastix.SetLogToFile(True)
            if os.path.isdir(log_path):
                self.elastix.SetOutputDirectory(log_path)
            else:
                os.mkdir(log_path)
                self.elastix.SetOutputDirectory(log_path)
        elif log is None:
            self.elastix.SetLogToFile(False)
            self.elastix.SetLogToConsole(False)
        else:
            raise KeyError(f'log must be console, file, or None not {log}')

        if res_fix is None:
            res_fix = self.resolution
        if res_move is None:
            res_move = self.resolution

        # 2. load volume
        vol_fix = self.convertSitkImage(fix_dset, res_fix)
        self.elastix.SetFixedImage(vol_fix)

        vol_move = self.convertSitkImage(move_dset, res_move)
        self.elastix.SetMovingImage(vol_move)
            
        # 3. compute transformation
        self.elastix.Execute()

        # 4. output transformation parameter
        return self.elastix.GetTransformParameterMap()[0]
        
    def warpVolume(self, vol_move, transform_map, res_move=None, log = 'file', log_path = './transformix_log'):
        
        '''
        Warps a given volume using transformix and a given transformation matrix
        
        '''
        
        if log == 'console':
            self.transformix.SetLogToConsole(True)
            self.transformix.SetLogToFile(False)
        elif log == 'file':
            self.transformix.SetLogToConsole(False)
            self.transformix.SetLogToFile(True)
            if os.path.isdir(log_path):
                self.transformix.SetOutputDirectory(log_path)
            else:
                os.mkdir(log_path)
                self.transformix.SetOutputDirectory(log_path)
        elif log is None:
            self.transformix.SetLogToFile(False)
            self.transformix.SetLogToConsole(False)
        else:
            raise KeyError(f'log must be console, file, or None not {log}')
            
            
        self.transformix.ComputeDeformationFieldOn()  
        self.transformix.SetTransformParameterMap(transform_map)
        self.transformix.SetMovingImage(self.convertSitkImage(vol_move, res_move))
        self.transformix.Execute()
        deformation = sitk.GetArrayFromImage(self.transformix.GetDeformationField())
        
        out = sitk.GetArrayFromImage(self.transformix.GetResultImage())
        return out, deformation
