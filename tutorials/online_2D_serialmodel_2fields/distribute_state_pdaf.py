"""Initialise model fields from the state vector (translation of distribute_state_pdaf.F90).

Both fields A and B are taken from their part of the state vector.
"""
import numpy as np

import mod_model as model
from mod_statevector_pdaf import id, sfields


def distribute_state_pdaf(dim_p: int, state_p: np.ndarray) -> np.ndarray:
    """Copy the state vector into the model fields."""
    shape = (model.ny, model.nx)
    model.field[:, :] = state_p[sfields[id.fieldA].slice].reshape(shape, order='F')
    model.fieldB[:, :] = state_p[sfields[id.fieldB].slice].reshape(shape, order='F')
    return state_p
