"""Call PDAF after each time step (translation of 3dvar/online_2D_serialmodel/assimilate_pdaf.F90).

Depending on subtype, one of three PDAF routines is called:

* subtype 0:    PDAF3_assimilate_3dvar      (parameterized 3D-Var)
* subtype 1, 2: PDAF3_assimilate_en3dvar    (3D-EnVar)
* subtype 3, 4: PDAF3_assimilate_3dvar_all  (hybrid 3D-Var)
"""
import pyPDAF.PDAF
import pyPDAF.PDAF3
# assimilate_3dvar and assimilate_en3dvar exist in pyPDAF, but are not
# exported in pyPDAF/PDAF3/__init__.py (pyPDAF 1.1), so they are imported from
# the submodule directly.
from pyPDAF.PDAF3.assim import assimilate_3dvar, assimilate_en3dvar

import mod_assimilation as assim
import mod_parallel_pdaf as par
from callback_obs_pdafomi import (init_dim_obs_l_pdafomi, init_dim_obs_pdafomi,
                                  obs_op_adj_pdafomi, obs_op_lin_pdafomi,
                                  obs_op_pdafomi)
from collect_state_pdaf import collect_state_pdaf
from cvt_adj_ens_pdaf import cvt_adj_ens_pdaf
from cvt_adj_pdaf import cvt_adj_pdaf
from cvt_ens_pdaf import cvt_ens_pdaf
from cvt_pdaf import cvt_pdaf
from distribute_state_pdaf import distribute_state_pdaf
from init_dim_l_pdaf import init_dim_l_pdaf
from init_n_domains_pdaf import init_n_domains_pdaf
from next_observation_pdaf import next_observation_pdaf
from prepoststep_3dvar_pdaf import prepoststep_3dvar_pdaf
from prepoststep_ens_pdaf import prepoststep_ens_pdaf


def assimilate_pdaf() -> None:
    """Call the PDAF 3D-Var routine for the selected subtype."""
    status_pdaf = 0
    if assim.subtype == 0:
        # Note: in pyPDAF 1.1 this function has no status argument
        status_pdaf = assimilate_3dvar(
            collect_state_pdaf, distribute_state_pdaf,
            init_dim_obs_pdafomi, obs_op_pdafomi,
            cvt_pdaf, cvt_adj_pdaf, obs_op_lin_pdafomi, obs_op_adj_pdafomi,
            prepoststep_3dvar_pdaf, next_observation_pdaf)
    elif assim.subtype in (1, 2):
        status_pdaf = assimilate_en3dvar(
            collect_state_pdaf, distribute_state_pdaf,
            init_dim_obs_pdafomi, obs_op_pdafomi,
            cvt_ens_pdaf, cvt_adj_ens_pdaf, obs_op_lin_pdafomi, obs_op_adj_pdafomi,
            init_n_domains_pdaf, init_dim_l_pdaf, init_dim_obs_l_pdafomi,
            prepoststep_ens_pdaf, next_observation_pdaf, status_pdaf)
    elif assim.subtype in (3, 4):
        status_pdaf = pyPDAF.PDAF3.assimilate_3dvar_all(
            collect_state_pdaf, distribute_state_pdaf,
            init_dim_obs_pdafomi, obs_op_pdafomi,
            cvt_ens_pdaf, cvt_adj_ens_pdaf, cvt_pdaf, cvt_adj_pdaf,
            obs_op_lin_pdafomi, obs_op_adj_pdafomi,
            init_n_domains_pdaf, init_dim_l_pdaf, init_dim_obs_l_pdafomi,
            prepoststep_ens_pdaf, next_observation_pdaf, status_pdaf)

    if status_pdaf != 0:
        print(f'\n ERROR {status_pdaf:3d} in PDAF3_assimilate - stopping! '
              f'(PE {par.mype_world:4d})')
        pyPDAF.PDAF.abort(1)
