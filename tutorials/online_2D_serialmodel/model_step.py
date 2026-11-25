"""One time step of the tutorial model (shared by integrate.py and integrate_pdaf.py).

The model simply shifts the field by one grid point in y-direction
(periodic). Fortran::

    DO j = 1, nx
       store = field(ny, j)
       DO i = ny-1, 1, -1
          field(i+1, j) = field(i, j)
       END DO
       field(1, j) = store
    END DO
"""
import numpy as np

import mod_model as model


def model_step() -> None:
    """Shift the field by one row (periodic) in place."""
    model.field[:, :] = np.roll(model.field, 1, axis=0)
