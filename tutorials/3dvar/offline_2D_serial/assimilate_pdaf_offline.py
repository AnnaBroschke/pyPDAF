"""Perform the 3D-Var analysis (translation of 3dvar/offline_2D_serial/assimilate_pdaf_offline.F90).

Depending on subtype, one of three PDAF routines is called:

* subtype 0:    PDAF3_assim_offline_3dvar      (parameterized 3D-Var)
* subtype 1, 2: PDAF3_assim_offline_en3dvar    (3D-EnVar)
* subtype 3, 4: PDAF3_assim_offline_3dvar_all  (hybrid 3D-Var)
"""
import pyPDAF.PDAF
import pyPDAF.PDAF3
# assim_offline_3dvar and assim_offline_en3dvar exist in pyPDAF, but are not
# exported in pyPDAF/PDAF3/__init__.py (pyPDAF 1.1), so they are imported from
# the submodule directly.
from pyPDAF.PDAF3.assim import assim_offline_3dvar, assim_offline_en3dvar

import mod_assimilation as assim
import mod_parallel_pdaf as par
from callback_obs_pdafomi import (init_dim_obs_l_pdafomi, init_dim_obs_pdafomi,
                                  obs_op_adj_pdafomi, obs_op_lin_pdafomi,
                                  obs_op_pdafomi)
from cvt_adj_ens_pdaf import cvt_adj_ens_pdaf
from cvt_adj_pdaf import cvt_adj_pdaf
from cvt_ens_pdaf import cvt_ens_pdaf
from cvt_pdaf import cvt_pdaf
from init_dim_l_pdaf import init_dim_l_pdaf
from init_n_domains_pdaf import init_n_domains_pdaf
from prepoststep_3dvar_offline import prepoststep_3dvar_offline
from prepoststep_ens_offline import prepoststep_ens_offline


def assimilate_pdaf_offline() -> None:
    """Call the PDAF 3D-Var routine for the selected subtype."""
    status_pdaf = 0
    if assim.subtype == 0:
        status_pdaf = assim_offline_3dvar(
            init_dim_obs_pdafomi, obs_op_pdafomi,
            cvt_pdaf, cvt_adj_pdaf, obs_op_lin_pdafomi, obs_op_adj_pdafomi,
            prepoststep_3dvar_offline)
    elif assim.subtype in (1, 2):
        status_pdaf = assim_offline_en3dvar(
            init_dim_obs_pdafomi, obs_op_pdafomi,
            cvt_ens_pdaf, cvt_adj_ens_pdaf, obs_op_lin_pdafomi, obs_op_adj_pdafomi,
            init_n_domains_pdaf, init_dim_l_pdaf, init_dim_obs_l_pdafomi,
            prepoststep_ens_offline)
    elif assim.subtype in (3, 4):
        status_pdaf = pyPDAF.PDAF3.assim_offline_3dvar_all(
            init_dim_obs_pdafomi, obs_op_pdafomi,
            cvt_ens_pdaf, cvt_adj_ens_pdaf, cvt_pdaf, cvt_adj_pdaf,
            obs_op_lin_pdafomi, obs_op_adj_pdafomi,
            init_n_domains_pdaf, init_dim_l_pdaf, init_dim_obs_l_pdafomi,
            prepoststep_ens_offline)

    if status_pdaf != 0:
        print(f'\n ERROR {status_pdaf:3d} during assimilation with PDAF '
              f'- stopping! (PE {par.mype_world:4d})')
        pyPDAF.PDAF.abort(1)
