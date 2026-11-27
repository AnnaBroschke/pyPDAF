"""Local state dimension (translation of online_2D_parallelmodel/init_dim_l_pdaf.F90).

For the coordinates of the local domain, the offset of the process-local
part (nx_p columns per process) is added.
"""
import numpy as np
import pyPDAF.PDAFlocal

import mod_assimilation as assim
import mod_model as model
import mod_parallel_pdaf as par


def init_dim_l_pdaf(step: int, domain_p: int, dim_l: int) -> int:
    """Initialise the local state dimension for domain ``domain_p`` (1-based, local)."""
    dim_l = 1

    off_p = par.mype_filter * model.nx_p * model.ny

    assim.coords_l[0] = np.ceil((domain_p + off_p) / model.ny)
    assim.coords_l[1] = (domain_p + off_p) - (assim.coords_l[0] - 1) * model.ny

    id_lstate_in_pstate = np.array([domain_p], dtype=np.intc)
    pyPDAF.PDAFlocal.set_indices(dim_l, id_lstate_in_pstate)

    return dim_l
