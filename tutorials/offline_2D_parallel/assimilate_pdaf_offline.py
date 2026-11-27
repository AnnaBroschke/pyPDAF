"""Perform the analysis step (translation of assimilate_pdaf_offline.F90).

PDAF3_assim_offline executes the analysis step. The call-back routines
are passed as Python functions. For global filters (e.g. ESTKF) the
routines for localisation are not called, but must still be provided.
"""
import pyPDAF.PDAF
import pyPDAF.PDAF3

import mod_parallel_pdaf as par
from callback_obs_pdafomi import (init_dim_obs_l_pdafomi, init_dim_obs_pdafomi,
                                  obs_op_pdafomi)
from init_dim_l_pdaf import init_dim_l_pdaf
from init_n_domains_pdaf import init_n_domains_pdaf
from prepoststep_ens_offline import prepoststep_ens_offline


def assimilate_pdaf_offline() -> None:
    """Call PDAF3_assim_offline."""
    status_pdaf = 0
    status_pdaf = pyPDAF.PDAF3.assim_offline(init_dim_obs_pdafomi,
                                             obs_op_pdafomi,
                                             init_n_domains_pdaf,
                                             init_dim_l_pdaf,
                                             init_dim_obs_l_pdafomi,
                                             prepoststep_ens_offline,
                                             status_pdaf)

    if status_pdaf != 0:
        print(f'\n ERROR {status_pdaf:3d} during assimilation with PDAF '
              f'- stopping! (PE {par.mype_world:4d})')
        pyPDAF.PDAF.abort(1)
