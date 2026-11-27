"""PDAFomi observation module for observation type C (translation of obs_C_pdafomi.F90).

Observation type C: observations at arbitrary positions between grid points.
The observation operator uses bilinear interpolation of the four
surrounding grid points. The file ``../../inputs_offline/obsC.txt`` contains in
the first line the number of observations and then one line per observation
with: value, x-coordinate, y-coordinate.
"""
import numpy as np
import pyPDAF.PDAFomi

import mod_assimilation as assim
import mod_parallel_pdaf as par

I_OBS = 3            # Index of this observation type in PDAFomi
NROWS = 4            # Number of grid points used for the interpolation
assim_C: bool = False    # Whether to assimilate this data type
rms_obs_C: float = 0.0   # Observation error standard deviation (constant)


def init_dim_obs_C(step: int, dim_obs: int) -> int:
    """Read observations and initialise the observation information."""
    if par.mype_filter == 0:
        print(' ' * 8 + 'Assimilate observations - obs type C: '
              'interpolated observations')

    if assim_C:
        pyPDAF.PDAFomi.set_doassim(I_OBS, 1)
    pyPDAF.PDAFomi.set_disttype(I_OBS, 0)
    ncoord = 2
    pyPDAF.PDAFomi.set_ncoord(I_OBS, ncoord)

    # *** Read observation list ***
    with open('../../inputs_offline/obsC.txt') as f:
        nobs = int(f.readline())
        obs_list = np.loadtxt(f, ndmin=2)      # shape (nobs, 3)
    assert obs_list.shape == (nobs, 3)

    dim_obs_p = nobs
    dim_obs = nobs

    if par.mype_filter == 0:
        print(' ' * 8 + f'--- number of full observations{dim_obs:6d}')

    obs_p = obs_list[:, 0].copy()
    ocoord_p = np.asfortranarray(obs_list[:, 1:3].T)   # (2, dim_obs_p)

    # *** Indices of the 4 surrounding grid points in the state vector ***
    # 1-based, column-wise storage: index = (x-1)*ny + y
    xf = np.floor(obs_list[:, 1]).astype(np.intc)
    yf = np.floor(obs_list[:, 2]).astype(np.intc)
    id_obs_p = np.zeros((NROWS, dim_obs_p), dtype=np.intc, order='F')
    id_obs_p[0, :] = (xf - 1) * assim.ny + yf   # (x,   y)
    id_obs_p[1, :] = xf * assim.ny + yf         # (x+1, y)
    id_obs_p[2, :] = id_obs_p[0, :] + 1         # (x,   y+1)
    id_obs_p[3, :] = id_obs_p[1, :] + 1         # (x+1, y+1)
    pyPDAF.PDAFomi.set_id_obs_p(I_OBS, NROWS, dim_obs_p, id_obs_p)

    # *** Interpolation coefficients (thisobs%icoeff_p) ***
    icoeff_p = np.zeros((NROWS, dim_obs_p), order='F')
    gcoords = np.zeros((NROWS, ncoord), order='F')
    for i in range(dim_obs_p):
        # Only the entries needed for bilinear interpolation are set
        gcoords[0, 0] = np.floor(ocoord_p[0, i])
        gcoords[0, 1] = np.floor(ocoord_p[1, i])
        gcoords[1, 0] = gcoords[0, 0] + 1.0
        gcoords[2, 1] = gcoords[0, 1] + 1.0
        icoeff_p[:, i] = pyPDAF.PDAFomi.get_interp_coeff_lin(
            NROWS, ncoord, gcoords, ocoord_p[:, i].copy(), icoeff_p[:, i].copy())
    pyPDAF.PDAFomi.set_icoeff_p(I_OBS, NROWS, dim_obs_p, icoeff_p)

    ivar_obs_p = np.full(dim_obs_p, 1.0 / (rms_obs_C * rms_obs_C))

    dim_obs = pyPDAF.PDAFomi.gather_obs(I_OBS, dim_obs_p, obs_p, ivar_obs_p,
                                        ocoord_p, ncoord, assim.cradius)
    return dim_obs


def obs_op_C(dim_p: int, dim_obs: int, state_p: np.ndarray,
             ostate: np.ndarray) -> np.ndarray:
    """Observation operator: bilinear interpolation."""
    return pyPDAF.PDAFomi.obs_op_interp_lin(I_OBS, NROWS, state_p, ostate)


def init_dim_obs_l_C(domain_p: int, step: int, dim_obs: int,
                     dim_obs_l: int) -> int:
    """Initialise local observations for the local analysis domain."""
    return pyPDAF.PDAFomi.init_dim_obs_l_iso(I_OBS, assim.coords_l,
                                             assim.locweight, assim.cradius,
                                             assim.sradius, dim_obs_l)


def obs_op_adj_C(dim_p: int, dim_obs: int, ostate: np.ndarray,
                 state_p: np.ndarray) -> np.ndarray:
    """Adjoint of the bilinear interpolation."""
    return pyPDAF.PDAFomi.obs_op_adj_interp_lin(I_OBS, NROWS, ostate, state_p)
