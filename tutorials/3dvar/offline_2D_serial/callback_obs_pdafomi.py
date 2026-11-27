"""Call-back routines for PDAFomi (translation of callback_obs_pdafomi.F90).

These routines are called by PDAF. They call the corresponding routines of
each observation type. Note that in Python, values that are INTENT(out) or
INTENT(inout) in Fortran are *returned*.

Difference to Fortran: As in the pyPDAF examples, the calls in obs_op and
init_dim_obs_l are guarded by the assim_X flags, so that observation types
that were never initialised are not touched. The result is identical, since
PDAFomi skips observation types with doassim=0 anyway.
"""
import numpy as np

import obs_A_pdafomi as obs_A
import obs_B_pdafomi as obs_B
import obs_C_pdafomi as obs_C


def init_dim_obs_pdafomi(step: int, dim_obs: int) -> int:
    """Determine the full dimension of the observation vector."""
    dim_obs = 0
    if obs_A.assim_A:
        dim_obs += obs_A.init_dim_obs_A(step, 0)
    if obs_B.assim_B:
        dim_obs += obs_B.init_dim_obs_B(step, 0)
    if obs_C.assim_C:
        dim_obs += obs_C.init_dim_obs_C(step, 0)
    return dim_obs


def obs_op_pdafomi(step: int, dim_p: int, dim_obs: int,
                   state_p: np.ndarray, ostate: np.ndarray) -> np.ndarray:
    """Apply the observation operators of all observation types."""
    if obs_A.assim_A:
        ostate = obs_A.obs_op_A(dim_p, dim_obs, state_p, ostate)
    if obs_B.assim_B:
        ostate = obs_B.obs_op_B(dim_p, dim_obs, state_p, ostate)
    if obs_C.assim_C:
        ostate = obs_C.obs_op_C(dim_p, dim_obs, state_p, ostate)
    return ostate


def init_dim_obs_l_pdafomi(domain_p: int, step: int, dim_obs: int,
                           dim_obs_l: int) -> int:
    """Determine the dimension of the local observation vector."""
    if obs_A.assim_A:
        dim_obs_l = obs_A.init_dim_obs_l_A(domain_p, step, dim_obs, dim_obs_l)
    if obs_B.assim_B:
        dim_obs_l = obs_B.init_dim_obs_l_B(domain_p, step, dim_obs, dim_obs_l)
    if obs_C.assim_C:
        dim_obs_l = obs_C.init_dim_obs_l_C(domain_p, step, dim_obs, dim_obs_l)
    return dim_obs_l


def obs_op_lin_pdafomi(step: int, dim_p: int, dim_obs: int,
                       state_p: np.ndarray, ostate: np.ndarray) -> np.ndarray:
    """Linearized observation operator (for 3D-Var).

    The observation operators of this tutorial are linear, so the same
    routines as in obs_op_pdafomi are used.
    """
    if obs_A.assim_A:
        ostate = obs_A.obs_op_A(dim_p, dim_obs, state_p, ostate)
    if obs_B.assim_B:
        ostate = obs_B.obs_op_B(dim_p, dim_obs, state_p, ostate)
    if obs_C.assim_C:
        ostate = obs_C.obs_op_C(dim_p, dim_obs, state_p, ostate)
    return ostate


def obs_op_adj_pdafomi(step: int, dim_p: int, dim_obs: int,
                       ostate: np.ndarray, state_p: np.ndarray) -> np.ndarray:
    """Adjoint observation operator (for 3D-Var): observation space -> state space."""
    if obs_A.assim_A:
        state_p = obs_A.obs_op_adj_A(dim_p, dim_obs, ostate, state_p)
    if obs_B.assim_B:
        state_p = obs_B.obs_op_adj_B(dim_p, dim_obs, ostate, state_p)
    if obs_C.assim_C:
        state_p = obs_C.obs_op_adj_C(dim_p, dim_obs, ostate, state_p)
    return state_p
