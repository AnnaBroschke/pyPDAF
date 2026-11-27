"""PDAFomi observation module for observation type B (translation of offline_2D_parallel/obs_B_pdafomi.F90).

With domain decomposition each process provides the observations of its
own part of the domain; PDAFomi_gather_obs collects the full vector.

Observation type B: observations of the model field at grid points, read
from ``../inputs_offline/obsB.txt``. Missing values are marked by -999.

Difference to Fortran: In Fortran the observation is described by the
derived type ``TYPE(obs_f) :: thisobs``. In pyPDAF this object lives inside
the PDAF library and is accessed via the observation index ``I_OBS``. The
components are set with functions like ``pyPDAF.PDAFomi.set_doassim``.
"""
import numpy as np
import pyPDAF.PDAFomi

import mod_assimilation as assim
import mod_model_pdaf as model
import mod_parallel_pdaf as par
from init_dim_obs_l_pdafomi_user import gather_ocoord, init_dim_obs_l_pdafomi_user

I_OBS = 2            # Index of this observation type in PDAFomi
assim_B: bool = False    # Whether to assimilate this data type
rms_obs_B: float = 0.0   # Observation error standard deviation (constant)
ocoord_f: np.ndarray = np.zeros((2, 0))   # Coordinates of all observations (for the user search)


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
    obs_field = np.loadtxt('../inputs_offline/obsB.txt')

    # *** Select the observations in the process-local domain ***
    # Global index (0-based) of each grid point in the state vector; process
    # mype_filter holds the indices off_p, ..., off_p + local_dims - 1.
    off_p = model.offset(par.mype_filter)
    dim_p = int(model.local_dims[par.mype_filter])
    obs_flat = obs_field.ravel(order='F')
    gidx = np.arange(obs_flat.size)
    local = (gidx >= off_p) & (gidx < off_p + dim_p)
    valid = local & (obs_flat > -999.0)
    dim_obs_p = int(np.count_nonzero(valid))

    # Grid coordinates (1-based) of all grid points
    i_idx, j_idx = np.indices((model.ny, model.nx))
    xcoord = j_idx.ravel(order='F') + 1.0
    ycoord = i_idx.ravel(order='F') + 1.0

    if dim_obs_p > 0:
        obs_p = obs_flat[valid]
        ocoord_p = np.zeros((ncoord, dim_obs_p), order='F')
        ocoord_p[0, :] = xcoord[valid]
        ocoord_p[1, :] = ycoord[valid]
        # Index in the process-local state vector (1-based)
        id_obs_p = np.zeros((1, dim_obs_p), dtype=np.intc, order='F')
        id_obs_p[0, :] = gidx[valid] - off_p + 1
        ivar_obs_p = np.full(dim_obs_p, 1.0 / (rms_obs_B * rms_obs_B))
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

    # Coordinates of all observations, only needed for the user-provided
    # search for local observations (Fortran: thisobs%ocoord_f)
    if assim.obs_l_user:
        global ocoord_f
        ocoord_f = gather_ocoord(ocoord_p, dim_obs_p)
        assert ocoord_f.shape[1] == dim_obs
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
    if assim.obs_l_user:
        return init_dim_obs_l_pdafomi_user(I_OBS, ocoord_f, assim.coords_l,
                                           assim.locweight, assim.cradius,
                                           assim.sradius, dim_obs_l)
    return pyPDAF.PDAFomi.init_dim_obs_l_iso(I_OBS, assim.coords_l,
                                             assim.locweight, assim.cradius,
                                             assim.sradius, dim_obs_l)
