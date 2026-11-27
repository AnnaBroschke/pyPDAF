"""Local state dimension (translation of init_dim_l_pdaf.F90).

A local analysis domain is one grid point. Since there are two fields, the
local state vector contains two elements: field A and field B at this point.
"""
import numpy as np
import pyPDAF.PDAFlocal

import mod_assimilation as assim
import mod_model as model
import mod_statevector_pdaf as sv


def init_dim_l_pdaf(step: int, domain_p: int, dim_l: int) -> int:
    """Initialise the local state dimension for domain ``domain_p`` (1-based)."""
    # One grid point, all fields
    dim_l = sv.n_fields

    # Coordinates of the local analysis domain (x = column, y = row; 1-based)
    assim.coords_l[0] = np.ceil(domain_p / model.ny)
    assim.coords_l[1] = domain_p - (assim.coords_l[0] - 1) * model.ny

    # Indices (1-based) of the local state elements in the global state vector
    id_lstate_in_pstate = np.array([domain_p + f.off for f in sv.sfields],
                                   dtype=np.intc)
    pyPDAF.PDAFlocal.set_indices(dim_l, id_lstate_in_pstate)

    return dim_l
