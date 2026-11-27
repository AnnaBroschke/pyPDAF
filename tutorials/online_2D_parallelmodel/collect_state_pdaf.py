"""Initialise the state vector from the process-local model field
(translation of online_2D_parallelmodel/collect_state_pdaf.F90)."""
import numpy as np

import mod_model as model


def collect_state_pdaf(dim_p: int, state_p: np.ndarray) -> np.ndarray:
    """Copy field_p into the process-local state vector."""
    state_p[:] = model.field_p.ravel(order='F')
    return state_p
