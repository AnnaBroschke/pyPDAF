"""One time step of the tutorial model (shared by integrate.py and integrate_pdaf.py).

Both fields are shifted by one grid point in y-direction (periodic).
"""
import numpy as np

import mod_model as model


def model_step() -> None:
    """Shift both fields by one row (periodic) in place."""
    model.field[:, :] = np.roll(model.field, 1, axis=0)
    model.fieldB[:, :] = np.roll(model.fieldB, 1, axis=0)
