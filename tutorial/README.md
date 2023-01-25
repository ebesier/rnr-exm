## Getting Started

1. Clone this repository and navigate to it in your terminal. 

2. Set up a virtual environment with SimpleITK installed. 

```
# Create and activate a conda environment 
conda create -n exm-toolbox python==3.7 -y 
conda activate exm-toolbox'

# Install SimpleITK
%conda install -c https://conda.anaconda.org/simpleitk SimpleITK
```

3. Install SimpleElastix. SimpleElastix provides a simplified, universal, and efficient way of registering two volumes/slices. SimpleElastix builds on SimpleITK.

```

# Install SimpleElastix

# May need install the higher version of Cmake
!git clone https://github.com/SuperElastix/SimpleElastix
!mkdir SimpleElastix_build
!cd SimpleElastix_build
!cmake ../SimpleElastix/SuperBuild
# Can take hours to compile
# -j4: 4 threads. Do as many threads as needed
!make -j4

# Build and install Python package (current dir: `SimpleElastix_build/`)
!cd SimpleITK-build/Wrapping/Python
!python Packaging/setup.py install

# Add path of SITK python wrappings to the `.bashrc` file
export PYTHONPATH=$(pwd)

# Install ExM package 
%pip install -r requirements.txt 

# Install ipywidgets
# Interact method will be used for visualizing volume slices
%conda install -c conda-forge ipywidgets=7.6.0

```

4. Launch Jupyter notebooks by running `jupyter notebook`. Open the .ipynb file called 'baseline_tutorial'. 
