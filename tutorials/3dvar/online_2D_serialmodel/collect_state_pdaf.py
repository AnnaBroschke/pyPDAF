"""Initialise the state vector from model fields (translation of collect_state_pdaf.F90).

Call-back routine: before the analysis, PDAF collects the forecast of
each ensemble member from the model field.
"""
import numpy as np

import mod_model as model


def collect_state_pdaf(dim_p: int, state_p: np.ndarray) -> np.ndarray:
    """Copy the model field into the state vector."""
    state_p[:] = model.field.ravel(order='F')
    return state_p
