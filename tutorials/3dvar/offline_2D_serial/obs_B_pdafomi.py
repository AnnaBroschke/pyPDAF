"""PDAFomi observation module for observation type B (translation of obs_B_pdafomi.F90).

Observation type B: observations of the model field at grid points, read
from ``../../inputs_offline/obsB.txt``. Missing values are marked by -999.

Difference to Fortran: In Fortran the observation is described by the
derived type ``TYPE(obs_f) :: thisobs``. In pyPDAF this object lives inside
the PDAF library and is accessed via the observation index ``I_OBS``. The
components are set with functions like ``pyPDAF.PDAFomi.set_doassim``.
"""
import numpy as np
import pyPDAF.PDAFomi

import mod_assimilation as assim
import mod_parallel_pdaf as par

I_OBS = 2            # Index of this observation type in PDAFomi
assim_B: bool = False    # Whether to assimilate this data type
rms_obs_B: float = 0.0   # Observation error standard deviation (constant)


def init_dim_obs_B(step: int, dim_obs: int) -> int:
    """Read observations and initialise the observation information.

    Returns the full dimension of the observation vector for this type.
    """
    if par.mype_filter == 0:
        print(' ' * 8 + 'Assimilate observations - obs type B')

    # Store whether to assimilate this observation type (thisobs%doassim)
    if assim_B:
        pyPDAF.PDAFomi.set_doassim(I_OBS, 1)
    # Type of distance computation (0: Cartesian)   (thisobs%disttype)
    pyPDAF.PDAFomi.set_disttype(I_OBS, 0)
    # Number of coordinates used for distance computation (thisobs%ncoord)
    ncoord = 2
    pyPDAF.PDAFomi.set_ncoord(I_OBS, ncoord)

    # *** Read observation field, shape (ny, nx) ***
    obs_field = np.loadtxt('../../inputs_offline/obsB.txt')

    # *** Count valid observations ***
    # Fortran loops j = 1..nx (outer), i = 1..ny (inner). Flattening the
    # field in Fortran order gives exactly the same sequence.
    obs_flat = obs_field.ravel(order='F')
    valid = obs_flat > -999.0
    dim_obs_p = int(np.count_nonzero(valid))
    dim_obs = dim_obs_p

    if par.mype_filter == 0:
        print(' ' * 8 + f'--- number of full observations{dim_obs:6d}')

    # *** Initialize vector of observations, coordinates and index array ***
    obs_p = obs_flat[valid]

    # Grid indices (1-based like in Fortran)
    i_idx, j_idx = np.indices((assim.ny, assim.nx))
    ocoord_p = np.zeros((ncoord, dim_obs_p), order='F')
    ocoord_p[0, :] = j_idx.ravel(order='F')[valid] + 1.0   # x-coordinate
    ocoord_p[1, :] = i_idx.ravel(order='F')[valid] + 1.0   # y-coordinate

    # Index of observed element in the state vector (1-based, thisobs%id_obs_p)
    id_obs_p = np.zeros((1, dim_obs_p), dtype=np.intc, order='F')
    id_obs_p[0, :] = np.nonzero(valid)[0] + 1
    pyPDAF.PDAFomi.set_id_obs_p(I_OBS, 1, dim_obs_p, id_obs_p)

    # *** Inverse observation error variances ***
    ivar_obs_p = np.full(dim_obs_p, 1.0 / (rms_obs_B * rms_obs_B))

    # *** Provide observation information to PDAFomi ***
    dim_obs = pyPDAF.PDAFomi.gather_obs(I_OBS, dim_obs_p, obs_p, ivar_obs_p,
                                        ocoord_p, ncoord, assim.cradius)
    return dim_obs


def obs_op_B(dim_p: int, dim_obs: int, state_p: np.ndarray,
             ostate: np.ndarray) -> np.ndarray:
    """Observation operator: select observed grid points from the state."""
    return pyPDAF.PDAFomi.obs_op_gridpoint(I_OBS, state_p, ostate)


def init_dim_obs_l_B(domain_p: int, step: int, dim_obs: int,
                     dim_obs_l: int) -> int:
    """Initialise local observations for the local analysis domain ``domain_p``.

    ``assim.coords_l`` was set before in ``init_dim_l_pdaf``.
    """
    return pyPDAF.PDAFomi.init_dim_obs_l_iso(I_OBS, assim.coords_l,
                                             assim.locweight, assim.cradius,
                                             assim.sradius, dim_obs_l)


def obs_op_adj_B(dim_p: int, dim_obs: int, ostate: np.ndarray,
             state_p: np.ndarray) -> np.ndarray:
    """Adjoint observation operator: add observed values to their grid points."""
    return pyPDAF.PDAFomi.obs_op_adj_gridpoint(I_OBS, ostate, state_p)
