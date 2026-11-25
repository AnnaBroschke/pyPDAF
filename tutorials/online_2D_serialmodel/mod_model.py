"""Model variables (translation of mod_model.F90).

In Fortran, mod_model_pdaf.F90 only re-exports mod_model. In Python all
files use ``import mod_model as model`` directly.
"""
import numpy as np

nx: int = 0                  # Size of 2D grid in x-direction
ny: int = 0                  # Size of 2D grid in y-direction
total_steps: int = 0         # Total number of time steps
field: np.ndarray = np.zeros((0, 0))   # Model field, shape (ny, nx)
