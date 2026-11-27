"""Call PDAF after each time step (translation of assimilate_pdaf.F90).

PDAF3_assimilate counts the time steps. When the forecast phase is
complete it collects the ensemble, performs the analysis and distributes
the new ensemble back to the model tasks.
"""
import pyPDAF.PDAF
import pyPDAF.PDAF3

import mod_parallel_pdaf as par
from callback_obs_pdafomi import (init_dim_obs_l_pdafomi, init_dim_obs_pdafomi,
                                  obs_op_pdafomi)
from collect_state_pdaf import collect_state_pdaf
from distribute_state_pdaf import distribute_state_pdaf
from init_dim_l_pdaf import init_dim_l_pdaf
from init_n_domains_pdaf import init_n_domains_pdaf
from next_observation_pdaf import next_observation_pdaf
from prepoststep_pdaf import prepoststep_pdaf


def assimilate_pdaf() -> None:
    """Call PDAF3_assimilate."""
    status_pdaf = 0
    status_pdaf = pyPDAF.PDAF3.assimilate(collect_state_pdaf,
                                          distribute_state_pdaf,
                                          init_dim_obs_pdafomi,
                                          obs_op_pdafomi,
                                          init_n_domains_pdaf,
                                          init_dim_l_pdaf,
                                          init_dim_obs_l_pdafomi,
                                          prepoststep_pdaf,
                                          next_observation_pdaf,
                                          status_pdaf)

    if status_pdaf != 0:
        print(f'\n ERROR {status_pdaf:3d} in PDAF3_assimilate '
              f'- stopping! (PE {par.mype_world:4d})')
        pyPDAF.PDAF.abort(1)
