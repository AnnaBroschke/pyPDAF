"""Model variables (translation of mod_model.F90).

Compared to online_2D_serialmodel there is a second field ``fieldB``.
All files use ``import mod_model as model`` (Fortran: mod_model_pdaf).
"""
import numpy as np

nx: int = 0                  # Size of 2D grid in x-direction
ny: int = 0                  # Size of 2D grid in y-direction
total_steps: int = 0         # Total number of time steps
field: np.ndarray = np.zeros((0, 0))    # Model field A, shape (ny, nx)
fieldB: np.ndarray = np.zeros((0, 0))   # Model field B, shape (ny, nx)
