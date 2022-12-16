import os
import warnings
import argparse
from yacs.config import CfgNode
import SimpleITK as sitk

# -----------------------------------------------------------------------------
# Config definition
# -----------------------------------------------------------------------------
_C = CfgNode()

# -----------------------------------------------------------------------------
# System
# -----------------------------------------------------------------------------
_C.SYSTEM = CfgNode()

# -----------------------------------------------------------------------------
# Align
# -----------------------------------------------------------------------------
_C.ALIGN = CfgNode()

# Elastix params
_C.ALIGN.RESOLUTION = [1.625,1.625,4.0]
_C.ALIGN.TRANSFORM_TYPE = ['rigid']
_C.ALIGN.TYPE = 'intensity'
_C.ALIGN.NumberOfSamplesForExactGradient = '100000'
_C.ALIGN.MaximumNumberOfIterations = '2000'
_C.ALIGN.MaximumNumberOfSamplingAttempts = '100'
_C.ALIGN.FinalBSplineInterpolationOrder = '1'

def get_cfg_defaults():
    """Get a yacs CfgNode object with default values for my_project."""
    # Return a clone so that the defaults will not be altered
    # This is for the "local variable" use pattern
    return _C.clone()

def load_cfg(config_file = None, freeze=True, add_cfg_func=None):
    """Load configurations.
    """
    # Set configurations
    cfg = get_cfg_defaults()
    if add_cfg_func is not None:
        add_cfg_func(cfg)
    if config_file is not None:
        cfg.merge_from_file(config_file)

    if freeze:
        cfg.freeze()
    else:
        warnings.warn("Configs are mutable during the process, "
                      "please make sure that is expected.")
    return cfg

def save_all_cfg(cfg: CfgNode, output_dir: str):
    """Save configs in the output directory.
    """
    # Save config.yaml in the experiment directory after combine all
    # non-default configurations from yaml file and command line.
    path = os.path.join(output_dir, "config.yaml")
    with open(path, "w") as f:
        f.write(cfg.dump())
    print("Full config saved to {}".format(path))
