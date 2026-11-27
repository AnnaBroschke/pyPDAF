"""PDAFomi observation module for observation type A (translation of online_2D_parallelmodel/obs_A_pdafomi.F90).

Each process provides the observations in its nx_p columns.

Observation type A: observations of the model field at grid points, read
from ``../inputs_online/obs_step<step>.txt``. Missing values are marked by -999.

Difference to Fortran: In Fortran the observation is described by the
derived type ``TYPE(obs_f) :: thisobs``. In pyPDAF this object lives inside
the PDAF library and is accessed via the observation index ``I_OBS``. The
components are set with functions like ``pyPDAF.PDAFomi.set_doassim``.
"""
import numpy as np
import pyPDAF.PDAFomi

import mod_assimilation as assim
import mod_model as model
import mod_parallel_pdaf as par

I_OBS = 1            # Index of this observation type in PDAFomi
assim_A: bool = False    # Whether to assimilate this data type
rms_obs_A: float = 0.0   # Observation error standard deviation (constant)


def init_dim_obs_A(step: int, dim_obs: int) -> int:
    """Read observations and initialise the observation information.

    Returns the full dimension of the observation vector for this type.
    """
    if par.mype_filter == 0:
        print(' ' * 8 + 'Assimilate observations - obs type A')

    # Store whether to assimilate this observation type (thisobs%doassim)
    if assim_A:
        pyPDAF.PDAFomi.set_doassim(I_OBS, 1)
    # Type of distance computation (0: Cartesian)   (thisobs%disttype)
    pyPDAF.PDAFomi.set_disttype(I_OBS, 0)
    # Number of coordinates used for distance computation (thisobs%ncoord)
    ncoord = 2
    pyPDAF.PDAFomi.set_ncoord(I_OBS, ncoord)
    # Domain size and use of global observations (thisobs%domainsize, %use_global_obs)
    pyPDAF.PDAFomi.set_domainsize(I_OBS, ncoord,
                                  np.array([float(model.nx), float(model.ny)]))
    pyPDAF.PDAFomi.set_use_global_obs(I_OBS, 1)

    # *** Read observation field, shape (ny, nx) ***
    obs_field = np.loadtxt(f'../inputs_online/obs_step{step}.txt')

    # *** Observations in the process-local columns ***
    off_nx = model.nx_p * par.mype_filter
    obs_local = obs_field[:, off_nx:off_nx + model.nx_p]      # (ny, nx_p)
    obs_flat = obs_local.ravel(order='F')
    valid = obs_flat > -999.0
    dim_obs_p = int(np.count_nonzero(valid))

    if dim_obs_p > 0:
        obs_p = obs_flat[valid]
        # Global grid coordinates (1-based)
        i_idx, j_idx = np.indices((model.ny, model.nx_p))
        ocoord_p = np.zeros((ncoord, dim_obs_p), order='F')
        ocoord_p[0, :] = j_idx.ravel(order='F')[valid] + off_nx + 1.0
        ocoord_p[1, :] = i_idx.ravel(order='F')[valid] + 1.0
        # Index in the process-local state vector (1-based)
        id_obs_p = np.zeros((1, dim_obs_p), dtype=np.intc, order='F')
        id_obs_p[0, :] = np.nonzero(valid)[0] + 1
        ivar_obs_p = np.full(dim_obs_p, 1.0 / (rms_obs_A * rms_obs_A))
        pyPDAF.PDAFomi.set_id_obs_p(I_OBS, 1, dim_obs_p, id_obs_p)
    else:
        # No observation on this process: dummy arrays of size 1 (as in Fortran)
        obs_p = np.zeros(1)
        ivar_obs_p = np.ones(1)
        ocoord_p = np.zeros((ncoord, 1), order='F')
        pyPDAF.PDAFomi.set_id_obs_p(I_OBS, 1, 1, np.ones((1, 1), dtype=np.intc, order='F'))

    # *** Provide observation information to PDAFomi ***
    dim_obs = pyPDAF.PDAFomi.gather_obs(I_OBS, dim_obs_p, obs_p, ivar_obs_p,
                                        ocoord_p, ncoord, assim.cradius)
    return dim_obs


def obs_op_A(dim_p: int, dim_obs: int, state_p: np.ndarray,
             ostate: np.ndarray) -> np.ndarray:
    """Observation operator: select observed grid points from the state."""
    return pyPDAF.PDAFomi.obs_op_gridpoint(I_OBS, state_p, ostate)


def init_dim_obs_l_A(domain_p: int, step: int, dim_obs: int,
                     dim_obs_l: int) -> int:
    """Initialise local observations for the local analysis domain ``domain_p``.

    ``assim.coords_l`` was set before in ``init_dim_l_pdaf``.
    """
    return pyPDAF.PDAFomi.init_dim_obs_l_iso(I_OBS, assim.coords_l,
                                             assim.locweight, assim.cradius,
                                             assim.sradius, dim_obs_l)
