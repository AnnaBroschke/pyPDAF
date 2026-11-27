"""User-provided search for local observations
(translation of offline_2D_parallel/init_dim_obs_l_pdafomi_user.F90).

This is an example how the search for the observations within the cut-off
radius of a local analysis domain can be implemented by the user instead of
calling ``PDAFomi.init_dim_obs_l_iso``. It is useful if the distance
computation should be done differently, e.g. for a special grid.

In this tutorial it is only used with the command line option
``-obs_l_user .true.``; by default the PDAFomi routine is used.

Differences to the Fortran example:

* Fortran writes directly into the PDAF-internal arrays of ``thisobs_l``
  (``id_obs_l``, ``distance_l``, ``cradius_l``, ``sradius_l``). pyPDAF has no
  access to these arrays; the PDAFomi function ``store_obs_l_index`` does the
  same.
* ``PDAFomi_set_dim_obs_l`` requires the argument ``mode`` in PDAF 3.1
  (0: allocate all arrays). The Fortran example omits it and therefore does
  not compile with the current PDAF; it is not part of the tutorial's Makefile.
* The coordinates of all observations (Fortran: ``thisobs%ocoord_f``) are not
  accessible in pyPDAF. They are gathered by the observation module with
  ``gather_ocoord`` below, in the same order as in PDAFomi_gather_obs.
* As in the Fortran example, the Cartesian distance is computed without
  periodicity. This is the same as PDAFomi does for ``disttype = 0`` (used in
  this tutorial), so the results are identical to those of
  ``PDAFomi.init_dim_obs_l_iso``.
"""
from mpi4py import MPI
import numpy as np
import pyPDAF.PDAFomi

import mod_parallel_pdaf as par


def gather_ocoord(ocoord_p: np.ndarray, dim_obs_p: int) -> np.ndarray:
    """Gather the observation coordinates of all processes (shape (ncoord, dim_obs)).

    Corresponds to ``thisobs%ocoord_f`` set by PDAFomi_gather_obs: the
    process-local parts are concatenated in the order of the ranks.
    """
    comm = MPI.Comm.f2py(par.COMM_filter)
    local = np.ascontiguousarray(ocoord_p[:, :dim_obs_p].T)     # (dim_obs_p, ncoord)
    ncoord = ocoord_p.shape[0]
    counts = np.array(comm.allgather(dim_obs_p)) * ncoord
    full = np.empty((counts.sum() // ncoord, ncoord))
    comm.Allgatherv(local, [full, counts])
    return np.asfortranarray(full.T)


def init_dim_obs_l_pdafomi_user(i_obs: int, ocoord_f: np.ndarray,
                                coords_l: np.ndarray, locweight: int,
                                cradius: float, sradius: float,
                                cnt_obs_l_all: int) -> int:
    """Find the observations within ``cradius`` of the local domain ``coords_l``.

    Parameters
    ----------
    i_obs : int
        Index of the observation type in PDAFomi
    ocoord_f : ndarray (2, dim_obs)
        Coordinates of all observations of this type
    coords_l : ndarray (2,)
        Coordinates of the local analysis domain
    locweight, cradius, sradius
        Localization parameters
    cnt_obs_l_all : int
        Number of local observations of all previous observation types

    Returns
    -------
    cnt_obs_l_all : int
        Updated number of local observations of all observation types
    """
    # Store localization parameters (cradius, sradius, locweight)
    pyPDAF.PDAFomi.set_localization(i_obs, cradius, sradius, locweight)
    crad2 = cradius * cradius

    # *** Count local observations: squared Cartesian distance ***
    dists = np.abs(coords_l[:2, None] - ocoord_f[:2, :])
    distance2 = dists[0] * dists[0] + dists[1] * dists[1]
    inside = distance2 <= crad2
    cnt_obs = int(np.count_nonzero(inside))

    # Store the number of local observations (mode 0: allocate all arrays)
    cnt_obs_l_all, cnt_obs = pyPDAF.PDAFomi.set_dim_obs_l(i_obs, cnt_obs_l_all, cnt_obs, 0)

    # *** Store index, distance and radii of each local observation ***
    for cnt_l, i in enumerate(np.nonzero(inside)[0], start=1):
        pyPDAF.PDAFomi.store_obs_l_index(i_obs, cnt_l, int(i) + 1,
                                         float(np.sqrt(distance2[i])),
                                         cradius, sradius)

    return cnt_obs_l_all
