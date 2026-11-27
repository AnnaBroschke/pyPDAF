"""Ensemble control variable transformation (translation of cvt_ens_pdaf.F90).

Call-back routine for 3D-EnVar and hybrid 3D-Var. In the first iteration
the ensemble square root ``Vmat_ens_p`` is computed from the ensemble
perturbations::

    Vmat_ens_p = (ens_p - mean) / sqrt(dim_cvec_ens - 1)

With ``mcols_cvec_ens > 1`` the columns are repeated (this is where model
error or a localisation of the ensemble covariance could be included).
Then ``Vv_p = Vmat_ens_p v_p``.
"""
import numpy as np

import mod_assimilation as assim


def cvt_ens_pdaf(iter: int, dim_p: int, dim_ens: int, dim_cvec_ens: int,
                 ens_p: np.ndarray, v_p: np.ndarray, vv_p: np.ndarray) -> np.ndarray:
    """Return Vmat_ens_p @ v_p (Vmat_ens_p is set up at iter == 1)."""
    if iter == 1:
        fact = 1.0 / np.sqrt(dim_cvec_ens - 1)
        assim.Vmat_ens_p = np.zeros((dim_p, dim_cvec_ens), order='F')

        # Ensemble mean (vv_p is used as temporary array, as in Fortran)
        vv_p[:] = 0.0
        invdimens = 1.0 / dim_ens
        for member in range(dim_ens):             # same summation order as Fortran
            vv_p[:] += invdimens * ens_p[:, member]

        # Scaled ensemble perturbations
        for member in range(dim_ens):
            assim.Vmat_ens_p[:, member] = fact * (ens_p[:, member] - vv_p)

        # Repeat the columns for mcols_cvec_ens > 1
        for i in range(2, assim.mcols_cvec_ens + 1):
            for member in range((i - 1) * dim_ens, i * dim_ens):
                assim.Vmat_ens_p[:, member] = assim.Vmat_ens_p[:, member - (i - 1) * dim_ens]

    vv_p[:] = assim.Vmat_ens_p @ v_p
    return vv_p
