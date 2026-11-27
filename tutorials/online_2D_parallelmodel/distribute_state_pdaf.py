"""Initialise the process-local model field from the state vector
(translation of online_2D_parallelmodel/distribute_state_pdaf.F90)."""
import numpy as np

import mod_model as model


def distribute_state_pdaf(dim_p: int, state_p: np.ndarray) -> np.ndarray:
    """Copy the process-local state vector into field_p."""
    model.field_p[:, :] = state_p.reshape((model.ny, model.nx_p), order='F')
    return state_p
