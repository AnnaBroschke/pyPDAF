"""One time step of the tutorial model (shared by integrate.py and integrate_pdaf.py).

The field is shifted in y-direction. Since the domain is decomposed in
x-direction, each process can do this for its columns without communication.
"""
import numpy as np

import mod_model as model


def model_step() -> None:
    """Shift the process-local field by one row (periodic) in place."""
    model.field_p[:, :] = np.roll(model.field_p, 1, axis=0)
