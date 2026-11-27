"""Initialise the state vector from model fields (translation of collect_state_pdaf.F90).

Both fields A and B are written into their part of the state vector.
"""
import numpy as np

import mod_model as model
from mod_statevector_pdaf import id, sfields


def collect_state_pdaf(dim_p: int, state_p: np.ndarray) -> np.ndarray:
    """Copy the model fields into the state vector."""
    state_p[sfields[id.fieldA].slice] = model.field.ravel(order='F')
    state_p[sfields[id.fieldB].slice] = model.fieldB.ravel(order='F')
    return state_p
