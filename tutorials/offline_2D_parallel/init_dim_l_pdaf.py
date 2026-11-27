"""Local state dimension (translation of offline_2D_parallel/init_dim_l_pdaf.F90).

``domain_p`` counts the local analysis domains of this process. For the
coordinates of the domain, the offset of the process-local state in the
global state vector is added.
"""
import numpy as np
import pyPDAF.PDAFlocal

import mod_assimilation as assim
import mod_model_pdaf as model
import mod_parallel_pdaf as par


def init_dim_l_pdaf(step: int, domain_p: int, dim_l: int) -> int:
    """Initialise the local state dimension for domain ``domain_p`` (1-based, local)."""
    dim_l = 1

    # Global index of this grid point
    off_p = model.offset(par.mype_filter)

    # Coordinates of the local analysis domain (x = column, y = row; 1-based)
    assim.coords_l[0] = np.ceil((domain_p + off_p) / model.ny)
    assim.coords_l[1] = (domain_p + off_p) - (assim.coords_l[0] - 1) * model.ny

    # Index in the process-local state vector (no offset)
    id_lstate_in_pstate = np.array([domain_p], dtype=np.intc)
    pyPDAF.PDAFlocal.set_indices(dim_l, id_lstate_in_pstate)

    return dim_l
