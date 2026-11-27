"""Model grid variables (translation of mod_model_pdaf.F90).

``local_dims`` holds the process-local state dimension of each process
(domain decomposition, set in initialize.py).
"""
import numpy as np

nx: int = 0                                   # Size of 2D grid in x-direction
ny: int = 0                                   # Size of 2D grid in y-direction
local_dims: np.ndarray = np.zeros(0, dtype=int)   # Local state dimensions of all processes


def offset(rank: int) -> int:
    """Offset of the local state of process ``rank`` in the global state vector.

    Fortran: ``off_p = SUM(local_dims(1:mype_filter))``
    """
    return int(np.sum(local_dims[:rank]))
