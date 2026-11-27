"""Model variables (translation of online_2D_parallelmodel/mod_model.F90).

Each process holds ``nx_p`` columns of the field (``field_p``, shape (ny, nx_p)).
"""
import numpy as np

nx: int = 0                  # Size of 2D grid in x-direction
ny: int = 0                  # Size of 2D grid in y-direction
nx_p: int = 0                # Process-local size in x-direction
total_steps: int = 0         # Total number of time steps
field_p: np.ndarray = np.zeros((0, 0))   # Process-local model field, shape (ny, nx_p)
