"""Initialise model fields from the state vector (translation of distribute_state_pdaf.F90).

Call-back routine: PDAF hands over one ensemble member (``state_p``) and
we write it into the model field, so that the model can integrate it.
"""
import numpy as np

import mod_model as model


def distribute_state_pdaf(dim_p: int, state_p: np.ndarray) -> np.ndarray:
    """Copy the state vector into the model field."""
    model.field[:, :] = state_p.reshape((model.ny, model.nx), order='F')
    return state_p
