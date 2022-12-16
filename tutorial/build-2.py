import sitk_tile
import SimpleITK as sitk
from yacs.config import CfgNode

class alignBuild(sitk_tile.sitkTile):
    ''' build obj that inherits sitktile
    '''

    def __init__(self, cfg: CfgNode):

        self.cfg = cfg
        self.transform_type = self.cfg.ALIGN.TRANSFORM_TYPE
        self.parameter_map = None

        sitk_tile.sitkTile.__init__(self, self.cfg)

    def createParameterMap(self, cfg = None, transform_type = None):
        ''' creates parameter map from confiugration object passed to function
        '''
        if cfg is not None:
            self.cfg = cfg

        if transform_type is not None:
            self.transform_type = transform_type

        if len(self.cfg.ALIGN.TRANSFORM_TYPE) == 1:
            parameter_map = sitk.GetDefaultParameterMap(self.cfg.ALIGN.TRANSFORM_TYPE[0])
            parameter_map['NumberOfSamplesForExactGradient'] = [self.cfg.ALIGN.NumberOfSamplesForExactGradient]
            parameter_map['MaximumNumberOfIterations'] = [self.cfg.ALIGN.MaximumNumberOfIterations]
            parameter_map['MaximumNumberOfSamplingAttempts'] = [self.cfg.ALIGN.MaximumNumberOfSamplingAttempts]
            parameter_map['FinalBSplineInterpolationOrder'] = [self.cfg.ALIGN.FinalBSplineInterpolationOrder]
        else:
            parameter_map = sitk.VectorOfParameterMap()
            for trans in self.transform_type:
                parameter_map.append(self.createParameterMap(trans))
        
        return parameter_map

    def buildSitkTile(self, cfg = None, transform_type = None):
        ''' builds sitktile obj by setting resulution and parameter map
        '''

        if cfg is not None:
            self.cfg = cfg
        
        if transform_type is not None:
            self.transform_type = transform_type

        self.setResolution()

        self.parameter_map = self.createParameterMap()

        self.elastix.SetParameterMap(self.parameter_map)
