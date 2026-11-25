"""Local state dimension (translation of init_dim_l_pdaf.F90).

Call-back routine for the local filters. It sets the dimension of the local
state vector, the coordinates of the local analysis domain (used later in
init_dim_obs_l) and the index of the local state in the global state.
"""
import numpy as np
import pyPDAF.PDAFlocal

import mod_assimilation as assim
import mod_model as model


def init_dim_l_pdaf(step: int, domain_p: int, dim_l: int) -> int:
    """Initialise the local state dimension for domain ``domain_p`` (1-based)."""
    # Here one grid point is one local domain
    dim_l = 1

    # Coordinates of the local analysis domain (x = column, y = row; 1-based)
    assim.coords_l[0] = np.ceil(domain_p / model.ny)
    assim.coords_l[1] = domain_p - (assim.coords_l[0] - 1) * model.ny

    # Index of the local state vector element in the global state vector
    id_lstate_in_pstate = np.array([domain_p], dtype=np.intc)
    pyPDAF.PDAFlocal.set_indices(dim_l, id_lstate_in_pstate)

    return dim_l
